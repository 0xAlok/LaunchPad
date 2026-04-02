import csv
import io
import os
from datetime import datetime, timezone

import weasyprint
from flask import current_app
from flask_mail import Message

from app.extensions import db, mail
from app.models import Company, PlacementDrive, Application, Student, User, Role, Placement
from . import celery_app


def _patch_pydyf_transform():
    """Backfill removed pydyf.Stream methods expected by WeasyPrint."""
    try:
        import pydyf
    except Exception:
        return

    stream_cls = getattr(pydyf, "Stream", None)
    if not stream_cls:
        return

    if not hasattr(stream_cls, "transform"):
        def transform(self, a=1, b=0, c=0, d=1, e=0, f=0):
            self.set_matrix(a, b, c, d, e, f)
        stream_cls.transform = transform

    if not hasattr(stream_cls, "text_matrix"):
        def text_matrix(self, a=1, b=0, c=0, d=1, e=0, f=0):
            self.set_text_matrix(a, b, c, d, e, f)
        stream_cls.text_matrix = text_matrix


def _render_pdf_or_none(report_html):
    """Render HTML to PDF bytes. Return None on rendering errors."""
    _patch_pydyf_transform()
    try:
        return weasyprint.HTML(string=report_html).write_pdf()
    except Exception as exc:
        print(f"PDF generation failed, falling back to HTML-only email: {exc}")
        return None


@celery_app.task
def generate_monthly_report():
    """
    Generate monthly placement reports:
    - Admin summary report 
    - Company-wise report (applications, selections, analytics)
    """
    admin = User.query.join(User.roles).filter(Role.name == "admin").first()
    admin_email = admin.email if admin else "admin@test.com"

    now = datetime.now(timezone.utc)
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    new_companies = Company.query.filter(Company.created_at >= month_start).count()
    new_drives = PlacementDrive.query.filter(PlacementDrive.created_at >= month_start).count()
    new_applications = Application.query.filter(Application.applied_at >= month_start).count()
    new_selections = Application.query.filter(
        Application.status == "selected",
        Application.updated_at >= month_start,
    ).count()

    admin_report_html = f"""
    <h2>Monthly Placement Report — {now.strftime('%B %Y')}</h2>
    <table border="1" cellpadding="8" cellspacing="0">
        <tr><td><strong>New Companies</strong></td><td>{new_companies}</td></tr>
        <tr><td><strong>New Drives</strong></td><td>{new_drives}</td></tr>
        <tr><td><strong>Applications</strong></td><td>{new_applications}</td></tr>
        <tr><td><strong>Selections</strong></td><td>{new_selections}</td></tr>
    </table>
    """

    admin_pdf_data = _render_pdf_or_none(admin_report_html)

    try:
        msg = Message(
            subject=f"Monthly Placement Report — {now.strftime('%B %Y')}",
            recipients=[admin_email],
            html=admin_report_html,
        )
        if admin_pdf_data:
            msg.attach(f"monthly_report_admin_{now.strftime('%b_%Y')}.pdf", "application/pdf", admin_pdf_data)
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send admin monthly report: {e}")

    approved_companies = Company.query.filter_by(is_approved=True).all()
    sent_company_reports = 0

    for company in approved_companies:
        if not company.user or not company.user.email:
            continue

        drives_q = PlacementDrive.query.filter(PlacementDrive.company_id == company.id)
        monthly_drives = drives_q.filter(PlacementDrive.created_at >= month_start).count()
        total_active_drives = drives_q.filter(PlacementDrive.status == "open").count()

        monthly_apps = (
            Application.query
            .join(PlacementDrive, PlacementDrive.id == Application.drive_id)
            .filter(
                PlacementDrive.company_id == company.id,
                Application.applied_at >= month_start,
            )
            .count()
        )
        monthly_selected = (
            Application.query
            .join(PlacementDrive, PlacementDrive.id == Application.drive_id)
            .filter(
                PlacementDrive.company_id == company.id,
                Application.status == "selected",
                Application.updated_at >= month_start,
            )
            .count()
        )
        monthly_shortlisted = (
            Application.query
            .join(PlacementDrive, PlacementDrive.id == Application.drive_id)
            .filter(
                PlacementDrive.company_id == company.id,
                Application.status == "shortlisted",
                Application.updated_at >= month_start,
            )
            .count()
        )
        selection_rate = round((monthly_selected / monthly_apps * 100), 1) if monthly_apps else 0

        company_report_html = f"""
        <h2>Monthly Company Placement Report — {now.strftime('%B %Y')}</h2>
        <p><strong>Company:</strong> {company.name}</p>
        <table border="1" cellpadding="8" cellspacing="0">
            <tr><td><strong>Drives Created (This Month)</strong></td><td>{monthly_drives}</td></tr>
            <tr><td><strong>Active Drives</strong></td><td>{total_active_drives}</td></tr>
            <tr><td><strong>Applications Received (This Month)</strong></td><td>{monthly_apps}</td></tr>
            <tr><td><strong>Shortlisted (This Month)</strong></td><td>{monthly_shortlisted}</td></tr>
            <tr><td><strong>Selected (This Month)</strong></td><td>{monthly_selected}</td></tr>
            <tr><td><strong>Selection Rate</strong></td><td>{selection_rate}%</td></tr>
        </table>
        """

        company_pdf_data = _render_pdf_or_none(company_report_html)

        try:
            company_msg = Message(
                subject=f"Monthly Company Report — {now.strftime('%B %Y')}",
                recipients=[company.user.email],
                html=company_report_html,
            )
            if company_pdf_data:
                company_msg.attach(
                    f"monthly_report_{company.id}_{now.strftime('%b_%Y')}.pdf",
                    "application/pdf",
                    company_pdf_data,
                )
            mail.send(company_msg)
            sent_company_reports += 1
        except Exception as e:
            print(f"Failed to send monthly company report to {company.name}: {e}")

    return f"Monthly reports generated. Company reports sent: {sent_company_reports}"


@celery_app.task
def export_student_applications_csv(student_id):
    """Generate a CSV of all applications for a given student. 
    Saves to file and notifies the student via email."""
    student = Student.query.get(student_id)
    if not student:
        return "Student not found"

    applications = student.applications.all()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Phone", "Company Name", "Drive Title", "Application Status", "Applied At"])

    for a in applications:
        writer.writerow([
            student.phone,
            a.drive.company.name if a.drive and a.drive.company else "",
            a.drive.title if a.drive else "",
            a.status.capitalize(),
            a.applied_at.strftime("%Y-%m-%d %H:%M") if a.applied_at else "",
        ])

    csv_content = output.getvalue()
    output.close()

    upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
    export_dir = os.path.join(upload_folder, "exports")
    os.makedirs(export_dir, exist_ok=True)
    
    filename = f"applications_export_{student_id}_{int(datetime.now(timezone.utc).timestamp())}.csv"
    filepath = os.path.join(export_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(csv_content)

    try:
        msg = Message(
            subject="Your Applications CSV Export is Ready",
            recipients=[student.user.email],
            body=f"Hi {student.name},\n\nYour applications have been successfully exported as requested.\n\n"
                 f"The file is attached to this email.\n\nBest regards,\nLaunchPad",
        )
        msg.attach(filename, "text/csv", csv_content)
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send CSV export email: {e}")

    return f"Export saved to {filepath} and emailed to {student.user.email}"


@celery_app.task
def export_company_history_csv(company_id):
    """
    Generate a CSV of all applications received by a company and related placement outcomes.
    Saves to file and notifies the company via email with attachment.
    """
    company = Company.query.get(company_id)
    if not company or not company.user:
        return "Company not found"

    applications = (
        Application.query
        .join(PlacementDrive, PlacementDrive.id == Application.drive_id)
        .filter(PlacementDrive.company_id == company.id)
        .order_by(Application.applied_at.desc())
        .all()
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Company Name",
        "Drive Title",
        "Student Name",
        "Student Email",
        "Application Status",
        "Applied At",
        "Joining Date",
        "Feedback",
    ])

    for app in applications:
        joining_date = ""
        if app.status == "selected":
            placement = (
                Placement.query
                .filter_by(student_id=app.student_id, company_id=company.id)
                .order_by(Placement.created_at.desc())
                .first()
            )
            if placement and placement.joining_date:
                joining_date = placement.joining_date.strftime("%Y-%m-%d")

        writer.writerow([
            company.name,
            app.drive.title if app.drive else "",
            app.student.name if app.student else "",
            app.student.user.email if app.student and app.student.user else "",
            app.status.capitalize() if app.status else "",
            app.applied_at.strftime("%Y-%m-%d %H:%M") if app.applied_at else "",
            joining_date,
            app.company_feedback or "",
        ])

    csv_content = output.getvalue()
    output.close()

    upload_folder = current_app.config.get("UPLOAD_FOLDER", "uploads")
    export_dir = os.path.join(upload_folder, "exports")
    os.makedirs(export_dir, exist_ok=True)

    filename = f"company_export_{company.id}_{int(datetime.now(timezone.utc).timestamp())}.csv"
    filepath = os.path.join(export_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(csv_content)

    try:
        msg = Message(
            subject="Your Company Applications CSV Export is Ready",
            recipients=[company.user.email],
            body=f"Hi {company.name},\n\nYour company applications and placement history export is ready.\n\n"
                 f"The CSV file is attached.\n\nBest regards,\nLaunchPad",
        )
        msg.attach(filename, "text/csv", csv_content)
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send company CSV export email: {e}")

    return f"Export saved to {filepath} and emailed to {company.user.email}"
