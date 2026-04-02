import os
from datetime import datetime, timezone, date

from flask import Blueprint, request, jsonify, send_file
from flask_security import auth_token_required, current_user

from ..extensions import db, cache
from ..models import Company, PlacementDrive, Application, Interview, Placement
from ..utils.cache_helpers import bump_cache_version
from ..utils.decorators import role_required
from tasks.mail_tasks import send_application_status_email, send_interview_scheduled_email
from tasks.report_tasks import export_company_history_csv

company_bp = Blueprint("company", __name__)
ADMIN_DRIVES_CACHE_KEY = "admin_drives_cache_version"
STUDENT_DRIVES_CACHE_KEY = "student_drives_cache_version"


def _get_current_company():
    return Company.query.filter_by(user_id=current_user.id).first()


@company_bp.route("/profile", methods=["GET"])
@auth_token_required
@role_required("company")
def get_profile():
    company = _get_current_company()
    if not company:
        return jsonify({"error": "Company profile not found"}), 404
    return jsonify({"company": company.to_dict()}), 200


@company_bp.route("/profile", methods=["PUT"])
@auth_token_required
@role_required("company")
def update_profile():
    company = _get_current_company()
    if not company:
        return jsonify({"error": "Company profile not found"}), 404

    data = request.get_json()
    if data.get("name"):
        company.name = data["name"]
    if data.get("description") is not None:
        company.description = data["description"]
    if data.get("website") is not None:
        company.website = data["website"]
    if data.get("location") is not None:
        company.location = data["location"]
    if data.get("industry") is not None:
        company.industry = data["industry"]

    db.session.commit()
    return jsonify({"message": "Profile updated", "company": company.to_dict()}), 200


@company_bp.route("/drives", methods=["GET"])
@auth_token_required
@role_required("company")
def list_drives():
    company = _get_current_company()
    if not company:
        return jsonify({"error": "Company profile not found"}), 404

    drives = company.drives.order_by(PlacementDrive.created_at.desc()).all()
    return jsonify({"drives": [d.to_dict() for d in drives]}), 200


@company_bp.route("/drives", methods=["POST"])
@auth_token_required
@role_required("company")
def create_drive():
    company = _get_current_company()
    if not company:
        return jsonify({"error": "Company profile not found"}), 404
    if not company.is_approved:
        return jsonify({"error": "Your company must be approved before creating drives"}), 403
    if company.is_blacklisted:
        return jsonify({"error": "Your company has been blacklisted"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    title = data.get("title", "").strip()
    deadline_str = data.get("deadline", "")

    if not title:
        return jsonify({"error": "Title is required"}), 400
    if not deadline_str:
        return jsonify({"error": "Deadline is required"}), 400

    try:
        deadline = datetime.fromisoformat(deadline_str)
        if deadline.tzinfo is None:
            return jsonify({"error": "Deadline must include timezone information"}), 400
        deadline = deadline.astimezone(timezone.utc).replace(tzinfo=None)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid deadline format. Use ISO 8601."}), 400

    eligible_branches = data.get("eligible_branches", [])
    if isinstance(eligible_branches, list):
        eligible_branches = ",".join(eligible_branches)

    drive = PlacementDrive(
        company_id=company.id,
        title=title,
        description=data.get("description", ""),
        role_offered=data.get("role_offered", ""),
        package_lpa=float(data.get("package_lpa", 0)),
        location=data.get("location", ""),
        eligibility_cgpa=float(data.get("eligibility_cgpa", 0)),
        eligible_branches=eligible_branches,
        deadline=deadline,
    )
    db.session.add(drive)
    db.session.commit()
    bump_cache_version(ADMIN_DRIVES_CACHE_KEY)
    bump_cache_version(STUDENT_DRIVES_CACHE_KEY)
    cache.delete("public_analytics")

    return jsonify({"message": "Drive created, pending admin approval", "drive": drive.to_dict()}), 201


@company_bp.route("/drives/<int:drive_id>", methods=["PUT"])
@auth_token_required
@role_required("company")
def update_drive(drive_id):
    company = _get_current_company()
    if not company:
        return jsonify({"error": "Company profile not found"}), 404

    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.company_id != company.id:
        return jsonify({"error": "You can only edit your own drives"}), 403

    data = request.get_json()
    if data.get("title"):
        drive.title = data["title"]
    if data.get("description") is not None:
        drive.description = data["description"]
    if data.get("role_offered") is not None:
        drive.role_offered = data["role_offered"]
    if data.get("package_lpa") is not None:
        drive.package_lpa = float(data["package_lpa"])
    if data.get("location") is not None:
        drive.location = data["location"]
    if data.get("eligibility_cgpa") is not None:
        drive.eligibility_cgpa = float(data["eligibility_cgpa"])
    if data.get("eligible_branches") is not None:
        branches = data["eligible_branches"]
        if isinstance(branches, list):
            branches = ",".join(branches)
        drive.eligible_branches = branches
    if data.get("deadline"):
        try:
            deadline = datetime.fromisoformat(data["deadline"])
            if deadline.tzinfo is None:
                return jsonify({"error": "Deadline must include timezone information"}), 400
            drive.deadline = deadline.astimezone(timezone.utc).replace(tzinfo=None)
        except (ValueError, TypeError):
            return jsonify({"error": "Invalid deadline format"}), 400
    if data.get("status") in ("open", "closed", "cancelled"):
        drive.status = data["status"]

    db.session.commit()
    bump_cache_version(ADMIN_DRIVES_CACHE_KEY)
    bump_cache_version(STUDENT_DRIVES_CACHE_KEY)
    return jsonify({"message": "Drive updated", "drive": drive.to_dict()}), 200


@company_bp.route("/drives/<int:drive_id>/applications", methods=["GET"])
@auth_token_required
@role_required("company")
def list_applications(drive_id):
    company = _get_current_company()
    if not company:
        return jsonify({"error": "Company profile not found"}), 404

    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.company_id != company.id:
        return jsonify({"error": "Access denied"}), 403

    applications = drive.applications.order_by(Application.applied_at.desc()).all()
    return jsonify({
        "applications": [a.to_dict() for a in applications],
        "drive": {"id": drive.id, "title": drive.title, "is_approved": drive.is_approved, "status": drive.status}
    }), 200


@company_bp.route("/applications/<int:app_id>/status", methods=["PUT"])
@auth_token_required
@role_required("company")
def update_application_status(app_id):
    """Update application status (shortlist, reject, select)."""
    company = _get_current_company()
    if not company:
        return jsonify({"error": "Company profile not found"}), 404
    if company.is_blacklisted:
        return jsonify({"error": "Your company has been blacklisted"}), 403

    application = Application.query.get_or_404(app_id)
    if application.drive.company_id != company.id:
        return jsonify({"error": "Access denied"}), 403
    if not application.drive.is_approved:
        return jsonify({"error": "This drive's approval has been revoked. You cannot update application statuses."}), 403

    data = request.get_json() or {}
    new_status = data.get("status", "").strip().lower()

    valid_transitions = {
        "applied": ["shortlisted", "rejected"],
        "shortlisted": ["selected", "rejected"],
        "rejected": [],
        "selected": [],
        "withdrawn": [],
    }

    current_status = application.status
    if new_status not in valid_transitions.get(current_status, []):
        return jsonify({
            "error": f"Cannot change status from '{current_status}' to '{new_status}'"
        }), 400

    selected_joining_date = None
    rejection_feedback = None
    if new_status == "selected":
        joining_date_str = str(data.get("joining_date", "")).strip()
        if not joining_date_str:
            return jsonify({"error": "Joining date is required when selecting a candidate"}), 400
        try:
            selected_joining_date = date.fromisoformat(joining_date_str)
        except ValueError:
            return jsonify({"error": "Invalid joining date format. Use YYYY-MM-DD."}), 400

        today = datetime.now(timezone.utc).date()
        if selected_joining_date < today:
            return jsonify({"error": "Joining date cannot be in the past"}), 400
    elif new_status == "rejected":
        rejection_feedback = str(data.get("feedback", "")).strip()
        if not rejection_feedback:
            return jsonify({"error": "Feedback is required when rejecting an application"}), 400

    application.status = new_status
    if new_status == "rejected":
        application.company_feedback = rejection_feedback
    
    if new_status == "selected":
        existing_placement = Placement.query.filter_by(student_id=application.student_id, company_id=company.id).first()
        if existing_placement:
            existing_placement.position = application.drive.role_offered or "Selected Candidate"
            existing_placement.salary = application.drive.package_lpa or 0.0
            existing_placement.joining_date = selected_joining_date
        else:
            placement = Placement(
                student_id=application.student_id,
                company_id=company.id,
                position=application.drive.role_offered or "Selected Candidate",
                salary=application.drive.package_lpa or 0.0,
                joining_date=selected_joining_date
            )
            db.session.add(placement)
            
    db.session.commit()
    cache.delete("admin_analytics")
    cache.delete("public_analytics")

    try:
        send_application_status_email.delay(
            application.student.user.email,
            application.student.name,
            application.drive.title,
            new_status,
            joining_date=selected_joining_date.isoformat() if selected_joining_date else None,
            feedback=rejection_feedback
        )
    except Exception:
        pass

    return jsonify({"message": f"Application status updated to '{new_status}'", "application": application.to_dict()}), 200


@company_bp.route("/applications/<int:app_id>/interview", methods=["POST"])
@auth_token_required
@role_required("company")
def schedule_interview(app_id):
    """Schedule an interview for a shortlisted application."""
    company = _get_current_company()
    if not company:
        return jsonify({"error": "Company profile not found"}), 404

    application = Application.query.get_or_404(app_id)
    if application.drive.company_id != company.id:
        return jsonify({"error": "Access denied"}), 403
    if not application.drive.is_approved:
        return jsonify({"error": "This drive's approval has been revoked. You cannot schedule interviews."}), 403
    if application.status != "shortlisted":
        return jsonify({"error": "Only shortlisted applications can have interviews scheduled"}), 400
    if application.interview:
        return jsonify({"error": "Interview already scheduled for this application"}), 409

    data = request.get_json()
    scheduled_at_str = data.get("scheduled_at", "")

    if not scheduled_at_str:
        return jsonify({"error": "Scheduled date/time is required"}), 400

    try:
        scheduled_at = datetime.fromisoformat(scheduled_at_str)
        if scheduled_at.tzinfo is None:
            return jsonify({"error": "Scheduled date must include timezone information"}), 400
        scheduled_at = scheduled_at.astimezone(timezone.utc).replace(tzinfo=None)
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid date format. Use ISO 8601."}), 400

    interview = Interview(
        application_id=application.id,
        scheduled_at=scheduled_at,
        location=data.get("location", ""),
        interview_type=data.get("interview_type", "in-person"),
        notes=data.get("notes", ""),
    )
    db.session.add(interview)
    db.session.commit()

    try:
        send_interview_scheduled_email.delay(
            application.student.user.email,
            application.student.name,
            application.drive.title,
            interview.scheduled_at.isoformat(),
            interview.location or "",
            interview.interview_type or "in-person",
        )
    except Exception:
        pass

    return jsonify({"message": "Interview scheduled", "interview": interview.to_dict()}), 201


@company_bp.route("/applications/<int:app_id>/resume", methods=["GET"])
@auth_token_required
@role_required("company")
def download_student_resume(app_id):
    company = _get_current_company()
    if not company:
        return jsonify({"error": "Company profile not found"}), 404

    application = Application.query.get_or_404(app_id)
    if application.drive.company_id != company.id:
        return jsonify({"error": "Access denied"}), 403

    student = application.student
    if not student or not student.resume_path:
        return jsonify({"error": "No resume available"}), 404

    if not os.path.exists(student.resume_path):
        return jsonify({"error": "Resume file not found"}), 404

    return send_file(student.resume_path, as_attachment=True, download_name=f"{student.name}_resume.pdf")


@company_bp.route("/applications/export", methods=["POST"])
@auth_token_required
@role_required("company")
def export_company_applications():
    company = _get_current_company()
    if not company:
        return jsonify({"error": "Company profile not found"}), 404

    export_company_history_csv.delay(company.id)
    return jsonify({"message": "Export started. You will receive an email shortly."}), 200
