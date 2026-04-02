from datetime import datetime, timezone
from flask_security import UserMixin, RoleMixin, SQLAlchemyUserDatastore
from .extensions import db


roles_users = db.Table(
    "roles_users",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id")),
    db.Column("role_id", db.Integer, db.ForeignKey("role.id")),
)


class Role(db.Model, RoleMixin):
    """user roles: admin, company, student."""
    __tablename__ = "role"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(255))
  
    def to_dict(self):
        return {"id": self.id, "name": self.name, "description": self.description}


class User(db.Model, UserMixin):
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True)
    fs_uniquifier = db.Column(db.String(64), unique=True, nullable=False)
    confirmed_at = db.Column(db.DateTime)
    roles = db.relationship("Role", secondary=roles_users, backref=db.backref("users", lazy="dynamic"))

    student_profile = db.relationship("Student", backref="user", uselist=False, cascade="all, delete-orphan")
    company_profile = db.relationship("Company", backref="user", uselist=False, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "email": self.email,
            "active": self.active,
            "roles": [r.name for r in self.roles],
        }


class Student(db.Model):
    __tablename__ = "student"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    name = db.Column(db.String(150), nullable=False)
    branch = db.Column(db.String(100), nullable=False)
    cgpa = db.Column(db.Float, nullable=False, default=0.0)
    phone = db.Column(db.String(15), nullable=False)
    skills = db.Column(db.Text)
    experience = db.Column(db.Text)
    resume_path = db.Column(db.String(500))
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    applications = db.relationship("Application", backref="student", lazy="dynamic", cascade="all, delete-orphan")
    placements = db.relationship("Placement", backref="student", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "branch": self.branch,
            "cgpa": self.cgpa,
            "phone": self.phone,
            "skills": self.skills,
            "experience": self.experience,
            "resume_path": self.resume_path,
            "is_blacklisted": self.is_blacklisted,
            "active": self.user.active if self.user else False,
            "email": self.user.email if self.user else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class Company(db.Model):
    """Company profile linked to a user account."""
    __tablename__ = "company"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), unique=True, nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    website = db.Column(db.String(500))
    location = db.Column(db.String(200))
    industry = db.Column(db.String(100))
    hr_contact = db.Column(db.String(150))
    is_approved = db.Column(db.Boolean, default=False)
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    drives = db.relationship("PlacementDrive", backref="company", lazy="dynamic", cascade="all, delete-orphan")
    placements = db.relationship("Placement", backref="company", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "description": self.description,
            "website": self.website,
            "location": self.location,
            "industry": self.industry,
            "hr_contact": self.hr_contact,
            "is_approved": self.is_approved,
            "is_blacklisted": self.is_blacklisted,
            "active": self.user.active if self.user else False,
            "email": self.user.email if self.user else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class PlacementDrive(db.Model):
    """A recruitment event created by a company."""
    __tablename__ = "placement_drive"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    role_offered = db.Column(db.String(150))
    package_lpa = db.Column(db.Float)
    location = db.Column(db.String(200))
    eligibility_cgpa = db.Column(db.Float, default=0.0)
    eligible_branches = db.Column(db.String(500))  # Comma-separated
    deadline = db.Column(db.DateTime, nullable=False)
    is_approved = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default="open")  # open, closed, cancelled
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    applications = db.relationship("Application", backref="drive", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "company_id": self.company_id,
            "company_name": self.company.name if self.company else None,
            "title": self.title,
            "description": self.description,
            "role_offered": self.role_offered,
            "package_lpa": self.package_lpa,
            "location": self.location,
            "eligibility_cgpa": self.eligibility_cgpa,
            "eligible_branches": self.eligible_branches.split(",") if self.eligible_branches else [],
            "deadline": self.deadline.isoformat() if self.deadline else None,
            "is_approved": self.is_approved,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "application_count": self.applications.count() if self.applications else 0,
        }


class Application(db.Model):
    """A student's application to a placement drive."""
    __tablename__ = "application"
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    drive_id = db.Column(db.Integer, db.ForeignKey("placement_drive.id"), nullable=False)
    status = db.Column(db.String(20), default="applied")  
    ats_score = db.Column(db.Float, default=0.0)
    cover_letter = db.Column(db.Text)
    company_feedback = db.Column(db.Text)
    applied_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # one application per student per drive
    __table_args__ = (db.UniqueConstraint("student_id", "drive_id", name="uq_student_drive"),)

    interview = db.relationship("Interview", backref="application", uselist=False, cascade="all, delete-orphan")

    def to_dict(self):
        status_value = (self.status or "").strip().lower()
        placement = None
        company_id = self.drive.company_id if self.drive else (
            db.session.query(PlacementDrive.company_id)
            .filter(PlacementDrive.id == self.drive_id)
            .scalar()
        )

        if status_value == "selected" and company_id:
            placement = (
                Placement.query
                .filter_by(student_id=self.student_id, company_id=company_id)
                .order_by(Placement.id.desc())
                .first()
            )

        return {
            "id": self.id,
            "student_id": self.student_id,
            "student_name": self.student.name if self.student else None,
            "student_branch": self.student.branch if self.student else None,
            "student_cgpa": self.student.cgpa if self.student else None,
            "student_phone": self.student.phone if self.student else None,
            "student_skills": self.student.skills if self.student else None,
            "student_experience": self.student.experience if self.student else None,
            "student_email": self.student.user.email if self.student and self.student.user else None,
            "has_resume": bool(self.student.resume_path) if self.student else False,
            "drive_id": self.drive_id,
            "drive_title": self.drive.title if self.drive else None,
            "company_name": self.drive.company.name if self.drive and self.drive.company else None,
            "status": self.status,
            "ats_score": self.ats_score,
            "cover_letter": self.cover_letter,
            "company_feedback": self.company_feedback,
            "applied_at": self.applied_at.isoformat() if self.applied_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "interview": self.interview.to_dict() if self.interview else None,
            "joining_date": placement.joining_date.isoformat() if placement and placement.joining_date else None,
        }


class Interview(db.Model):
    """Interview scheduled for a shortlisted application."""
    __tablename__ = "interview"

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey("application.id"), unique=True, nullable=False)
    scheduled_at = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(300))
    interview_type = db.Column(db.String(50), default="in-person")  # in-person, online
    status = db.Column(db.String(20), default="scheduled")  # scheduled, completed, cancelled
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "application_id": self.application_id,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "location": self.location,
            "interview_type": self.interview_type,
            "status": self.status,
            "notes": self.notes,
        }


class Placement(db.Model):
    """Final placement records for students."""
    __tablename__ = "placement"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey("student.id"), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey("company.id"), nullable=False)
    position = db.Column(db.String(150), nullable=False)
    salary = db.Column(db.Float, nullable=False)
    joining_date = db.Column(db.Date, nullable=False)
    offer_letter_path = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "student_id": self.student_id,
            "company_id": self.company_id,
            "student_name": self.student.name if self.student else None,
            "company_name": self.company.name if self.company else None,
            "position": self.position,
            "salary": self.salary,
            "joining_date": self.joining_date.isoformat() if self.joining_date else None,
            "offer_letter_path": self.offer_letter_path,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


user_datastore = SQLAlchemyUserDatastore(db, User, Role)
