from datetime import datetime, timezone, timedelta

from flask_mail import Message

from app.extensions import mail
from app.models import PlacementDrive, Student, User, Application, Placement
from . import celery_app


def _format_portal_datetime(value):
    """format UTC datetime value to IST timestamp."""
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            return value
    elif isinstance(value, datetime):
        parsed = value
    else:
        return str(value)

    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)

    ist = timezone(timedelta(hours=5, minutes=30))
    return parsed.astimezone(ist).strftime("%d %b %Y, %I:%M %p IST")


def _safe_send(subject, recipients, body):
    """send one plain-text email without raising to caller."""
    try:
        msg = Message(subject=subject, recipients=recipients, body=body)
        mail.send(msg)
    except Exception as e:
        print(f"Failed to send email to {recipients}: {e}")


def _resolve_joining_date(student_email, drive_title):
    """Find selected placement joining date for the student/drive."""
    user = User.query.filter_by(email=student_email).first()
    if not user or not user.student_profile:
        return None

    application = (
        Application.query
        .join(PlacementDrive, PlacementDrive.id == Application.drive_id)
        .filter(
            Application.student_id == user.student_profile.id,
            Application.status == "selected",
            PlacementDrive.title == drive_title,
        )
        .order_by(Application.updated_at.desc())
        .first()
    )
    if not application or not application.drive:
        return None

    placement = (
        Placement.query
        .filter_by(student_id=application.student_id, company_id=application.drive.company_id)
        .order_by(Placement.created_at.desc())
        .first()
    )
    if placement and placement.joining_date:
        return placement.joining_date.strftime("%d %b %Y")
    return None


def _resolve_rejection_feedback(student_email, drive_title):
    user = User.query.filter_by(email=student_email).first()
    if not user or not user.student_profile:
        return None

    application = (
        Application.query
        .join(PlacementDrive, PlacementDrive.id == Application.drive_id)
        .filter(
            Application.student_id == user.student_profile.id,
            Application.status == "rejected",
            PlacementDrive.title == drive_title,
        )
        .order_by(Application.updated_at.desc())
        .first()
    )
    if application and application.company_feedback:
        return application.company_feedback.strip()
    return None


@celery_app.task
def send_daily_reminders():
    """Send reminders to students about placement drives closing within the next 2 days.
    Also remind companies about pending application reviews."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    deadline_threshold = now + timedelta(days=2)

    closing_drives = PlacementDrive.query.filter(
        PlacementDrive.is_approved == True,
        PlacementDrive.status == "open",
        PlacementDrive.deadline <= deadline_threshold,
        PlacementDrive.deadline > now,
    ).all()

    for drive in closing_drives:
        applied_ids = [a.student_id for a in drive.applications.all()]
        query = Student.query.filter(
            Student.is_blacklisted == False,
            Student.cgpa >= drive.eligibility_cgpa,
        )
        if applied_ids:
            query = query.filter(~Student.id.in_(applied_ids))
        eligible_students = query.all()

        for student in eligible_students:
            _safe_send(
                subject=f"Reminder: {drive.title} closing soon!",
                recipients=[student.user.email],
                body=f"Hi {student.name},\n\n"
                     f"The placement drive '{drive.title}' by {drive.company.name} "
                     f"is closing on {drive.deadline.strftime('%d %b %Y')}.\n"
                     f"Don't miss this opportunity!\n\n"
                    f"Best regards,\nLaunchPad",
            )

    return "Daily reminders sent"


@celery_app.task
def send_application_status_email(student_email, student_name, drive_title, new_status, *args, **kwargs):
    """Send email notification when application status changes."""
    joining_date = kwargs.get("joining_date")
    if not joining_date and args:
        joining_date = args[0]
    feedback = kwargs.get("feedback")
    if not feedback and len(args) >= 2:
        feedback = args[1]

    status_messages = {
        "shortlisted": "Congratulations! You have been shortlisted",
        "rejected": "We regret to inform you that your application was not selected",
        "selected": "Congratulations! You have been selected",
    }

    message = status_messages.get(new_status, f"Your application status changed to: {new_status}")
    if new_status == "selected":
        formatted_joining_date = None
        if joining_date:
            try:
                formatted_joining_date = datetime.fromisoformat(str(joining_date)).strftime("%d %b %Y")
            except ValueError:
                formatted_joining_date = str(joining_date)
        if not formatted_joining_date:
            formatted_joining_date = _resolve_joining_date(student_email, drive_title)
        if formatted_joining_date:
            message = f"{message}. Your joining date is {formatted_joining_date}"
    elif new_status == "rejected":
        rejection_feedback = (feedback or "").strip() if feedback else None
        if not rejection_feedback:
            rejection_feedback = _resolve_rejection_feedback(student_email, drive_title)
        if rejection_feedback:
            message = f"{message}. Feedback from company: {rejection_feedback}"

    _safe_send(
        subject=f"Application Update: {drive_title}",
        recipients=[student_email],
        body=f"Hi {student_name},\n\n"
             f"{message} for the placement drive '{drive_title}'.\n\n"
             f"Check your portal for more details.\n\n"
            f"Best regards,\nLaunchPad",
    )


@celery_app.task
def send_interview_scheduled_email(student_email, student_name, drive_title, scheduled_at, location, interview_type):
    """send interview schedule notification to students."""
    when_text = _format_portal_datetime(scheduled_at)
    location_text = location.strip() if location else "TBD"
    type_text = interview_type.strip().title() if interview_type else "Interview"
    _safe_send(
        subject=f"Interview Scheduled: {drive_title}",
        recipients=[student_email],
        body=f"Hi {student_name},\n\n"
             f"Your {type_text} interview for '{drive_title}' has been scheduled.\n"
             f"Date & Time: {when_text}\n"
             f"Location: {location_text}\n\n"
             f"Please check your portal for the latest status.\n\n"
             f"Best regards,\nLaunchPad",
    )


@celery_app.task
def send_company_approval_email(company_email, company_name, is_approved):
    """Notify company about registration approval/rejection."""
    if is_approved:
        subject = "Company Registration Approved"
        message = "Your company profile has been approved. You can now create placement drives."
    else:
        subject = "Company Registration Update"
        message = "Your company profile is currently not approved. Please contact placement cell for details."

    _safe_send(
        subject=subject,
        recipients=[company_email],
        body=f"Hi {company_name},\n\n"
             f"{message}\n\n"
             f"Best regards,\nLaunchPad",
    )


@celery_app.task
def send_drive_review_email(company_email, company_name, drive_title, is_approved):
    """Notify company when drive is approved/rejected by admin."""
    if is_approved:
        subject = f"Drive Approved: {drive_title}"
        message = f"Your placement drive '{drive_title}' has been approved and is visible to eligible students."
    else:
        subject = f"Drive Update: {drive_title}"
        message = f"Your placement drive '{drive_title}' has not been approved."

    _safe_send(
        subject=subject,
        recipients=[company_email],
        body=f"Hi {company_name},\n\n"
             f"{message}\n\n"
             f"Best regards,\nLaunchPad",
    )


@celery_app.task
def send_account_status_email(user_email, display_name, role_label, action_label):
    """Notify users/companies when account moderation status changes."""
    _safe_send(
        subject=f"Account Update: {role_label}",
        recipients=[user_email],
        body=f"Hi {display_name},\n\n"
             f"Your {role_label.lower()} account has been {action_label} by admin.\n"
             f"If you believe this is a mistake, contact the placement cell.\n\n"
             f"Best regards,\nLaunchPad",
    )


@celery_app.task
def send_company_application_event_email(company_email, company_name, student_name, drive_title, event_type):
    """Notify company when a student applies to or withdraws from a drive."""
    action_map = {
        "applied": "submitted an application",
        "withdrawn": "withdrawn their application",
    }
    action_text = action_map.get(event_type, f"updated the application ({event_type})")
    _safe_send(
        subject=f"Application Update: {drive_title}",
        recipients=[company_email],
        body=f"Hi {company_name},\n\n"
             f"Student {student_name} has {action_text} for '{drive_title}'.\n\n"
             f"Check your company dashboard for full details.\n\n"
             f"Best regards,\nLaunchPad",
    )


@celery_app.task
def send_welcome_email(user_email, display_name, role_name):
    """Send welcome email after registration."""
    role_label = (role_name or "user").strip().capitalize()
    _safe_send(
        subject="Welcome to LaunchPad Placement Portal",
        recipients=[user_email],
        body=f"Hi {display_name},\n\n"
             f"Welcome to LaunchPad. Your {role_label.lower()} account has been created successfully.\n\n"
             f"Log in to continue your placement activities.\n\n"
             f"Best regards,\nLaunchPad",
    )
