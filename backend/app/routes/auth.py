import re

from flask import Blueprint, request, jsonify
from flask_security import (
    current_user,
    auth_token_required,
    hash_password,
    verify_password,
    login_user,
    logout_user,
)
from sqlalchemy.exc import IntegrityError

from ..extensions import db, cache
from ..models import User, Role, Student, Company, PlacementDrive, Application, user_datastore
from ..utils.cache_helpers import bump_cache_version
from tasks.mail_tasks import send_welcome_email

auth_bp = Blueprint("auth", __name__)
ADMIN_COMPANIES_CACHE_KEY = "admin_companies_cache_version"


@auth_bp.route("/register", methods=["POST"])
def register():
    """Register a new student or company user."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")
    role_name = data.get("role", "").strip().lower()

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400
    if role_name not in ("student", "company"):
        return jsonify({"error": "Role must be 'student' or 'company'"}), 400
    if len(password) < 8:
        return jsonify({"error": "Password must be at least 8 characters"}), 400

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "Email is already registered"}), 409

    role = Role.query.filter_by(name=role_name).first()
    if not role:
        return jsonify({"error": f"Role '{role_name}' not found. Run seed first."}), 500

    user = user_datastore.create_user(
        email=email,
        password=hash_password(password),
        roles=[role],
    )

    if role_name == "student":
        name = data.get("name", "").strip()
        phone = data.get("phone", "").strip()
        branch = data.get("branch", "").strip()

        if not name or not phone or not branch:
            return jsonify({"error": "Name, phone, and branch are required for students"}), 400
        if not re.match(r'^\d{10}$', phone):
            return jsonify({"error": "Phone number must be exactly 10 digits"}), 400

        try:
            cgpa_val = float(data.get("cgpa", 0))
        except (ValueError, TypeError):
            return jsonify({"error": "CGPA must be a valid number"}), 400
            
        student = Student(
            user=user,
            name=name,
            branch=branch,
            cgpa=cgpa_val,
            phone=phone,
            skills=data.get("skills", ""),
            experience=data.get("experience", "")
        )
        db.session.add(student)
    elif role_name == "company":
        company_name = data.get("company_name", "").strip()
        if not company_name:
            return jsonify({"error": "Company name is required for companies"}), 400
            
        company = Company(
            user=user,
            name=company_name,
            description=data.get("description", ""),
            website=data.get("website", ""),
            location=data.get("location", ""),
            industry=data.get("industry", ""),
            hr_contact=data.get("hr_contact", ""),
        )
        db.session.add(company)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "Profile creation failed. A user or profile with the given details already exists."}), 409

    cache.delete("public_analytics")
    if role_name == "company":
        bump_cache_version(ADMIN_COMPANIES_CACHE_KEY)
    try:
        display_name = name if role_name == "student" else company_name
        send_welcome_email.delay(user.email, display_name, role_name)
    except Exception:
        pass

    return jsonify({
        "message": f"{role_name.capitalize()} registered successfully",
        "user": user.to_dict(),
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not verify_password(password, user.password):
        return jsonify({"error": "Invalid email or password"}), 401

    if not user.active:
        return jsonify({"error": "Your account has been deactivated. Contact the placement cell."}), 403

    login_user(user)
    token = user.get_auth_token()

    profile = None
    if user.student_profile:
        profile = user.student_profile.to_dict()
    elif user.company_profile:
        profile = user.company_profile.to_dict()

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": user.to_dict(),
        "profile": profile,
    }), 200


@auth_bp.route("/logout", methods=["POST"])
@auth_token_required
def logout():
    logout_user()
    return jsonify({"message": "Logged out successfully"}), 200


@auth_bp.route("/me", methods=["GET"])
@auth_token_required
def get_current_user():
    profile = None
    if current_user.student_profile:
        profile = current_user.student_profile.to_dict()
    elif current_user.company_profile:
        profile = current_user.company_profile.to_dict()

    return jsonify({
        "user": current_user.to_dict(),
        "profile": profile,
    }), 200


@auth_bp.route("/public/analytics", methods=["GET"])
@cache.cached(timeout=300, key_prefix="public_analytics")
def public_analytics():
    total_students = Student.query.count()
    total_companies = Company.query.filter_by(is_approved=True).count()
    total_drives = PlacementDrive.query.count()
    total_placements = Application.query.filter_by(status="selected").count()

    return jsonify({
        "students": total_students,
        "companies": total_companies,
        "drives": total_drives,
        "placements": total_placements,
    }), 200
