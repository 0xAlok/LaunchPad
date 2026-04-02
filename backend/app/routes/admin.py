from flask import Blueprint, request, jsonify
from flask_security import auth_token_required

from ..extensions import db, cache
from ..models import Student, Company, PlacementDrive, Application
from ..utils.decorators import role_required
from ..utils.cache_helpers import get_cache_version, bump_cache_version
from tasks.mail_tasks import (
    send_company_approval_email,
    send_drive_review_email,
    send_account_status_email,
)
from tasks.report_tasks import generate_monthly_report

admin_bp = Blueprint("admin", __name__)
ADMIN_COMPANIES_CACHE_KEY = "admin_companies_cache_version"
ADMIN_DRIVES_CACHE_KEY = "admin_drives_cache_version"
STUDENT_DRIVES_CACHE_KEY = "student_drives_cache_version"


def _admin_companies_cache_prefix():
    version = get_cache_version(ADMIN_COMPANIES_CACHE_KEY)
    query = request.query_string.decode("utf-8")
    return f"admin_companies:v{version}:{query}"


def _admin_drives_cache_prefix():
    version = get_cache_version(ADMIN_DRIVES_CACHE_KEY)
    query = request.query_string.decode("utf-8")
    return f"admin_drives:v{version}:{query}"


@admin_bp.route("/reports/monthly", methods=["POST"])
@auth_token_required
@role_required("admin")
def trigger_monthly_report():
    generate_monthly_report.delay()
    return jsonify({"message": "Monthly report generation started. Admin will receive an email shortly."}), 200


@admin_bp.route("/companies", methods=["GET"])
@auth_token_required
@role_required("admin")
@cache.cached(timeout=60, key_prefix=_admin_companies_cache_prefix)
def list_companies():
    status = request.args.get("status") 
    search = request.args.get("search", "").strip()
    query = Company.query

    if status == "approved":
        query = query.filter_by(is_approved=True, is_blacklisted=False)
    elif status == "pending":
        query = query.filter_by(is_approved=False, is_blacklisted=False)
    elif status == "blacklisted":
        query = query.filter_by(is_blacklisted=True)

    if search:
        query = query.filter(
            db.or_(
                Company.name.ilike(f"%{search}%"),
                Company.industry.ilike(f"%{search}%"),
            )
        )

    companies = query.order_by(Company.created_at.desc()).all()
    return jsonify({"companies": [c.to_dict() for c in companies]}), 200


@admin_bp.route("/companies/<int:company_id>/approve", methods=["PUT"])
@auth_token_required
@role_required("admin")
def approve_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.is_approved = True
    db.session.commit()
    cache.delete("admin_analytics")
    bump_cache_version(ADMIN_COMPANIES_CACHE_KEY)
    cache.delete("public_analytics")
    try:
        send_company_approval_email.delay(company.user.email, company.name, True)
    except Exception:
        pass
    return jsonify({"message": f"Company '{company.name}' approved", "company": company.to_dict()}), 200


@admin_bp.route("/companies/<int:company_id>/reject", methods=["PUT"])
@auth_token_required
@role_required("admin")
def reject_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.is_approved = False
    db.session.commit()
    cache.delete("admin_analytics")
    bump_cache_version(ADMIN_COMPANIES_CACHE_KEY)
    cache.delete("public_analytics")
    try:
        send_company_approval_email.delay(company.user.email, company.name, False)
    except Exception:
        pass
    return jsonify({"message": f"Company '{company.name}' rejected"}), 200


@admin_bp.route("/companies/<int:company_id>/blacklist", methods=["PUT"])
@auth_token_required
@role_required("admin")
def toggle_blacklist_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.is_blacklisted = not company.is_blacklisted
    db.session.commit()
    cache.delete("admin_analytics")
    bump_cache_version(ADMIN_COMPANIES_CACHE_KEY)
    action = "blacklisted" if company.is_blacklisted else "un-blacklisted"
    try:
        send_account_status_email.delay(
            company.user.email,
            company.name,
            "Company",
            "blacklisted" if company.is_blacklisted else "un-blacklisted",
        )
    except Exception:
        pass
    return jsonify({"message": f"Company '{company.name}' {action}", "company": company.to_dict()}), 200


@admin_bp.route("/companies/<int:company_id>/deactivate", methods=["PUT"])
@auth_token_required
@role_required("admin")
def toggle_deactivate_company(company_id):
    company = Company.query.get_or_404(company_id)
    company.user.active = not company.user.active
    db.session.commit()
    cache.delete("admin_analytics")
    bump_cache_version(ADMIN_COMPANIES_CACHE_KEY)
    action = "activated" if company.user.active else "deactivated"
    try:
        send_account_status_email.delay(
            company.user.email,
            company.name,
            "Company",
            action,
        )
    except Exception:
        pass
    return jsonify({"message": f"Company '{company.name}' {action}", "company": company.to_dict()}), 200


@admin_bp.route("/drives", methods=["GET"])
@auth_token_required
@role_required("admin")
@cache.cached(timeout=60, key_prefix=_admin_drives_cache_prefix)
def list_drives():
    status = request.args.get("status")  
    query = PlacementDrive.query

    if status == "pending":
        query = query.filter_by(is_approved=False)
    elif status == "approved":
        query = query.filter_by(is_approved=True)
    elif status == "closed":
        query = query.filter_by(status="closed")

    drives = query.order_by(PlacementDrive.created_at.desc()).all()
    return jsonify({"drives": [d.to_dict() for d in drives]}), 200


@admin_bp.route("/drives/<int:drive_id>/approve", methods=["PUT"])
@auth_token_required
@role_required("admin")
def approve_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.is_approved = True
    db.session.commit()
    cache.delete("admin_analytics")
    bump_cache_version(ADMIN_DRIVES_CACHE_KEY)
    bump_cache_version(STUDENT_DRIVES_CACHE_KEY)
    try:
        send_drive_review_email.delay(drive.company.user.email, drive.company.name, drive.title, True)
    except Exception:
        pass
    return jsonify({"message": f"Drive '{drive.title}' approved", "drive": drive.to_dict()}), 200


@admin_bp.route("/drives/<int:drive_id>/reject", methods=["PUT"])
@auth_token_required
@role_required("admin")
def reject_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.is_approved = False
    db.session.commit()
    cache.delete("admin_analytics")
    bump_cache_version(ADMIN_DRIVES_CACHE_KEY)
    bump_cache_version(STUDENT_DRIVES_CACHE_KEY)
    try:
        send_drive_review_email.delay(drive.company.user.email, drive.company.name, drive.title, False)
    except Exception:
        pass
    return jsonify({"message": f"Drive '{drive.title}' rejected"}), 200


@admin_bp.route("/students", methods=["GET"])
@auth_token_required
@role_required("admin")
def list_students():
    search = request.args.get("search", "").strip()
    query = Student.query

    if search:
        query = query.filter(
            db.or_(
                Student.name.ilike(f"%{search}%"),
                Student.phone.ilike(f"%{search}%"),
                Student.branch.ilike(f"%{search}%"),
            )
        )

    students = query.order_by(Student.created_at.desc()).all()
    return jsonify({"students": [s.to_dict() for s in students]}), 200


@admin_bp.route("/students/<int:student_id>/blacklist", methods=["PUT"])
@auth_token_required
@role_required("admin")
def toggle_blacklist_student(student_id):
    student = Student.query.get_or_404(student_id)
    student.is_blacklisted = not student.is_blacklisted
    db.session.commit()
    cache.delete("admin_analytics")
    action = "blacklisted" if student.is_blacklisted else "un-blacklisted"
    try:
        send_account_status_email.delay(
            student.user.email,
            student.name,
            "Student",
            "blacklisted" if student.is_blacklisted else "un-blacklisted",
        )
    except Exception:
        pass
    return jsonify({"message": f"Student '{student.name}' {action}", "student": student.to_dict()}), 200


@admin_bp.route("/students/<int:student_id>/deactivate", methods=["PUT"])
@auth_token_required
@role_required("admin")
def toggle_deactivate_student(student_id):
    student = Student.query.get_or_404(student_id)
    student.user.active = not student.user.active
    db.session.commit()
    cache.delete("admin_analytics")
    action = "activated" if student.user.active else "deactivated"
    try:
        send_account_status_email.delay(
            student.user.email,
            student.name,
            "Student",
            action,
        )
    except Exception:
        pass
    return jsonify({"message": f"Student '{student.name}' {action}", "student": student.to_dict()}), 200


def get_analytics_data():
    total_students = Student.query.count()
    total_companies = Company.query.count()
    approved_companies = Company.query.filter_by(is_approved=True).count()
    total_drives = PlacementDrive.query.count()
    approved_drives = PlacementDrive.query.filter_by(is_approved=True).count()
    total_applications = Application.query.count()
    selected_count = Application.query.filter_by(status="selected").count()
    rejected_count = Application.query.filter_by(status="rejected").count()

    status_counts = {}
    for status in ["applied", "shortlisted", "rejected", "selected", "withdrawn"]:
        status_counts[status] = Application.query.filter_by(status=status).count()

    top_companies = (
        db.session.query(Company.name, db.func.count(Application.id))
        .join(PlacementDrive, PlacementDrive.company_id == Company.id)
        .join(Application, Application.drive_id == PlacementDrive.id)
        .filter(Application.status == "selected")
        .group_by(Company.name)
        .order_by(db.func.count(Application.id).desc())
        .limit(5)
        .all()
    )

    branch_data = (
        db.session.query(Student.branch, db.func.count(Application.id))
        .join(Application, Application.student_id == Student.id)
        .group_by(Student.branch)
        .all()
    )

    return {
        "summary": {
            "total_students": total_students,
            "total_companies": total_companies,
            "approved_companies": approved_companies,
            "total_drives": total_drives,
            "approved_drives": approved_drives,
            "total_applications": total_applications,
            "selection_rate": round((selected_count / total_applications * 100), 1) if total_applications > 0 else 0,
        },
        "application_status": status_counts,
        "top_companies": [{"name": name, "selections": count} for name, count in top_companies],
        "branch_applications": [{"branch": branch, "count": count} for branch, count in branch_data],
    }


@admin_bp.route("/analytics", methods=["GET"])
@auth_token_required
@role_required("admin")
@cache.cached(timeout=120, key_prefix="admin_analytics")
def analytics():
    data = get_analytics_data()
    return jsonify(data), 200
