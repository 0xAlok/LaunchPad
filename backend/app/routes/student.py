import os
from datetime import datetime, timezone

from flask import Blueprint, request, jsonify, current_app, send_file
from flask_security import auth_token_required, current_user
from werkzeug.utils import secure_filename

from ..extensions import db, cache
from ..models import Student, PlacementDrive, Application, Company
from ..utils.decorators import role_required
from ..utils.cache_helpers import get_cache_version, bump_cache_version
from ..utils.helpers import allowed_file, compute_ats_score, extract_resume_text
from tasks.report_tasks import export_student_applications_csv
from tasks.mail_tasks import send_company_application_event_email

student_bp = Blueprint("student", __name__)
STUDENT_DRIVES_CACHE_KEY = "student_drives_cache_version"


def _student_drives_cache_prefix():
    version = get_cache_version(STUDENT_DRIVES_CACHE_KEY)
    query = request.query_string.decode("utf-8")
    return f"student_drives:v{version}:u{current_user.id}:{query}"


def _get_current_student():
    return Student.query.filter_by(user_id=current_user.id).first()

@student_bp.route("/profile", methods=["GET"])
@auth_token_required
@role_required("student")
def get_profile():
    student = _get_current_student()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404
    return jsonify({"student": student.to_dict()}), 200


@student_bp.route("/profile", methods=["PUT"])
@auth_token_required
@role_required("student")
def update_profile():
    student = _get_current_student()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404

    data = request.get_json()
    if data.get("name"):
        student.name = data["name"]
    if data.get("branch"):
        student.branch = data["branch"]
    if data.get("cgpa") is not None:
        student.cgpa = float(data["cgpa"])
    if data.get("phone") is not None:
        student.phone = data["phone"]
    if data.get("skills") is not None:
        student.skills = data["skills"]
    if data.get("experience") is not None:
        student.experience = data["experience"]

    db.session.commit()
    bump_cache_version(STUDENT_DRIVES_CACHE_KEY)
    return jsonify({"message": "Profile updated", "student": student.to_dict()}), 200

@student_bp.route("/resume", methods=["POST"])
@auth_token_required
@role_required("student")
def upload_resume():
    student = _get_current_student()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404

    if "resume" not in request.files:
        return jsonify({"error": "No file provided. Use field name 'resume'"}), 400

    file = request.files["resume"]
    if file.filename == "":
        return jsonify({"error": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    if student.resume_path and os.path.exists(student.resume_path):
        os.remove(student.resume_path)

    filename = secure_filename(f"{student.phone}_resume.pdf")
    filepath = os.path.join(current_app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    student.resume_path = filepath

    resume_text = extract_resume_text(student)
    if resume_text.strip():
        active_apps = Application.query.filter(
            Application.student_id == student.id,
            Application.status.in_(["applied", "shortlisted"])
        ).all()
        for app in active_apps:
            if app.drive and app.drive.description:
                app.ats_score = compute_ats_score(resume_text, app.drive.description)

    db.session.commit()
    bump_cache_version(STUDENT_DRIVES_CACHE_KEY)

    return jsonify({"message": "Resume uploaded successfully"}), 200


@student_bp.route("/resume", methods=["GET"])
@auth_token_required
@role_required("student")
def download_resume():
    student = _get_current_student()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404
    if not student.resume_path or not os.path.exists(student.resume_path):
        return jsonify({"error": "No resume uploaded"}), 404
    return send_file(student.resume_path, as_attachment=True)

@student_bp.route("/drives", methods=["GET"])
@auth_token_required
@role_required("student")
@cache.cached(timeout=60, key_prefix=_student_drives_cache_prefix)
def browse_drives():
    """Browse placement drives that are approved, open, and eligible for this student."""
    student = _get_current_student()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404

    search = request.args.get("search", "").strip()
    branch_filter = request.args.get("branch", "").strip()
    min_package = request.args.get("min_package", type=float)

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    query = PlacementDrive.query.filter(
        PlacementDrive.is_approved == True,
        PlacementDrive.status == "open",
        PlacementDrive.deadline > now,
        PlacementDrive.eligibility_cgpa <= student.cgpa,
    )

    query = query.filter(
        db.or_(
            PlacementDrive.eligible_branches == "",
            PlacementDrive.eligible_branches.is_(None),
            PlacementDrive.eligible_branches.ilike(f"%{student.branch}%"),
        )
    )

    if branch_filter:
        query = query.filter(
            db.or_(
                PlacementDrive.eligible_branches == "",
                PlacementDrive.eligible_branches.is_(None),
                PlacementDrive.eligible_branches.ilike(f"%{branch_filter}%"),
            )
        )

    if search:
        query = query.filter(
            db.or_(
                PlacementDrive.title.ilike(f"%{search}%"),
                PlacementDrive.role_offered.ilike(f"%{search}%"),
                PlacementDrive.company.has(Company.name.ilike(f"%{search}%")),
            )
        )

    if min_package is not None:
        query = query.filter(PlacementDrive.package_lpa >= min_package)

    drives = query.order_by(PlacementDrive.deadline.asc()).all()

    applied_drive_ids = set(
        a.drive_id for a in Application.query.filter_by(student_id=student.id).all()
    )

    preview_text = extract_resume_text(student)
    result = []
    for drive in drives:
        d = drive.to_dict()
        d["already_applied"] = drive.id in applied_drive_ids
        d["ats_preview"] = compute_ats_score(preview_text, drive.description) if preview_text.strip() else None
        result.append(d)

    return jsonify({"drives": result, "has_resume": bool(student.resume_path)}), 200

@student_bp.route("/apply/<int:drive_id>", methods=["POST"])
@auth_token_required
@role_required("student")
def apply_to_drive(drive_id):
    """Apply to a placement drive."""
    student = _get_current_student()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404
    if student.is_blacklisted:
        return jsonify({"error": "Your account has been blacklisted"}), 403

    if not student.resume_path or not os.path.exists(student.resume_path):
        return jsonify({"error": "Please upload your resume before applying. Go to Profile > Resume Upload."}), 400

    drive = PlacementDrive.query.get_or_404(drive_id)

    if not drive.is_approved:
        return jsonify({"error": "This drive is not yet approved"}), 400
    if drive.status != "open":
        return jsonify({"error": "This drive is no longer accepting applications"}), 400
    if drive.deadline < datetime.now(timezone.utc).replace(tzinfo=None):
        return jsonify({"error": "The application deadline has passed"}), 400
    if drive.eligibility_cgpa > student.cgpa:
        return jsonify({"error": f"Minimum CGPA required is {drive.eligibility_cgpa}"}), 400

    if drive.eligible_branches:
        eligible = [b.strip().lower() for b in drive.eligible_branches.split(",")]
        if eligible and student.branch.lower() not in eligible:
            return jsonify({"error": "Your branch is not eligible for this drive"}), 400

    existing = Application.query.filter_by(student_id=student.id, drive_id=drive.id).first()
    if existing:
        return jsonify({"error": "You have already applied to this drive"}), 409

    data = request.get_json() or {}

    resume_text = extract_resume_text(student)
    score = compute_ats_score(resume_text, drive.description)

    application = Application(
        student_id=student.id,
        drive_id=drive.id,
        cover_letter=data.get("cover_letter", ""),
        ats_score=score,
    )
    db.session.add(application)
    db.session.commit()
    bump_cache_version(STUDENT_DRIVES_CACHE_KEY)
    cache.delete("admin_analytics")
    try:
        send_company_application_event_email.delay(
            drive.company.user.email,
            drive.company.name,
            student.name,
            drive.title,
            "applied",
        )
    except Exception:
        pass

    return jsonify({"message": "Application submitted successfully", "application": application.to_dict()}), 201

@student_bp.route("/applications", methods=["GET"])
@auth_token_required
@role_required("student")
def list_applications():
    student = _get_current_student()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404

    applications = student.applications.order_by(Application.applied_at.desc()).all()
    return jsonify({"applications": [a.to_dict() for a in applications]}), 200


@student_bp.route("/applications/<int:app_id>/withdraw", methods=["PUT"])
@auth_token_required
@role_required("student")
def withdraw_application(app_id):
    student = _get_current_student()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404

    application = Application.query.get_or_404(app_id)
    if application.student_id != student.id:
        return jsonify({"error": "Access denied"}), 403
    if application.status != "applied":
        return jsonify({"error": "Only applications with 'applied' status can be withdrawn"}), 400

    application.status = "withdrawn"
    db.session.commit()
    bump_cache_version(STUDENT_DRIVES_CACHE_KEY)
    cache.delete("admin_analytics")
    try:
        send_company_application_event_email.delay(
            application.drive.company.user.email,
            application.drive.company.name,
            student.name,
            application.drive.title,
            "withdrawn",
        )
    except Exception:
        pass

    return jsonify({"message": "Application withdrawn", "application": application.to_dict()}), 200


@student_bp.route("/applications/export", methods=["POST"])
@auth_token_required
@role_required("student")
def export_applications():
    student = _get_current_student()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404

    export_student_applications_csv.delay(student.id)

    return jsonify({"message": "Export started. You will receive an email shortly."}), 200

@student_bp.route("/placements", methods=["GET"])
@auth_token_required
@role_required("student")
def list_placements():
    student = _get_current_student()
    if not student:
        return jsonify({"error": "Student profile not found"}), 404

    placements = student.placements.order_by(db.desc('created_at')).all()
    return jsonify({"placements": [p.to_dict() for p in placements]}), 200
