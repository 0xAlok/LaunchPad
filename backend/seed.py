# seed.py - populate DB with demo data
import sys
import os
from datetime import datetime, timedelta, timezone

from app import create_app
from app.extensions import db
from app.models import user_datastore, Student, Company, PlacementDrive, Application, Interview, Placement
from flask_security import hash_password


def seed():
    """Create roles and initial data."""
    app = create_app()
    with app.app_context():
        print("[SEED] Starting database initialization process...")
        
        if "--reset" in sys.argv:
            print("[SEED] --reset flag detected. Dropping all tables...")
            db.drop_all()
            
        db.create_all()

        if user_datastore.find_user(email="admin@test.com"):
            print("[SEED] Database already contains admin user. Skipping seed process.")
            print("[SEED] (Tip: Run `python seed.py --reset` to force a complete database wipe and re-seed)")
            return

        admin_role = user_datastore.find_or_create_role(name="admin", description="Administrator")
        student_role = user_datastore.find_or_create_role(name="student", description="Student")
        company_role = user_datastore.find_or_create_role(name="company", description="Company")

        user_datastore.create_user(
            email="admin@test.com",
            password=hash_password("admin123"),
            roles=[admin_role],
        )
        print("[SEED] Admin user created: admin@test.com / admin123")

        companies_data = [
            {
                "email": "hiring@google.com",
                "pwd": "password123",
                "name": "Google",
                "industry": "Technology",
                "location": "Mountain View, CA",
                "website": "https://google.com",
                "desc": "Global technology leader.",
                "approved": True,
            },
            {
                "email": "hr@microsoft.com",
                "pwd": "password123",
                "name": "Microsoft",
                "industry": "Software",
                "location": "Redmond, WA",
                "website": "https://microsoft.com",
                "desc": "Empowering every person on the planet.",
                "approved": True,
            },
            {
                "email": "careers@tesla.com",
                "pwd": "password123",
                "name": "Tesla",
                "industry": "Automotive",
                "location": "Austin, TX",
                "website": "https://tesla.com",
                "desc": "Sustainable energy and electric vehicles.",
                "approved": True,
            },
            {
                "email": "talent@nvidia.com",
                "pwd": "password123",
                "name": "NVIDIA",
                "industry": "Semiconductors",
                "location": "Santa Clara, CA",
                "website": "https://nvidia.com",
                "desc": "AI computing and accelerated platforms.",
                "approved": False,
            }
        ]

        created_companies = []
        for c in companies_data:
            u = user_datastore.create_user(
                email=c["email"],
                password=hash_password(c["pwd"]),
                roles=[company_role]
            )
            comp = Company(
                user=u,
                name=c["name"],
                industry=c["industry"],
                location=c["location"],
                website=c["website"],
                description=c["desc"],
                is_approved=c.get("approved", True),
            )
            db.session.add(comp)
            created_companies.append(comp)
            print(f"[SEED] Company user created: {c['email']}")

        students_data = [
            {
                "email": "alok@student.edu",
                "pwd": "password123",
                "name": "Alok Kumar",
                "branch": "Computer Science",
                "cgpa": 9.2,
                "phone": "9876543210",
                "skills": "Python, Flask, Vue.js, Docker, REST APIs, SQLAlchemy, JavaScript, React, Git, Linux, AWS",
                "experience": "Built a full-stack placement portal with Flask and Vue.js. Interned at a startup building microservices with Docker and Kubernetes."
            },
            {
                "email": "priya@student.edu",
                "pwd": "password123",
                "name": "Priya Sharma",
                "branch": "Electronics",
                "cgpa": 8.8,
                "phone": "8765432109",
                "skills": "Embedded C, VHDL, MATLAB, Python, PCB Design, ARM Cortex, RTOS, Signal Processing",
                "experience": "Designed and tested embedded firmware for IoT devices. Research assistant working on FPGA-based signal processing."
            },
            {
                "email": "rohit@student.edu",
                "pwd": "password123",
                "name": "Rohit Verma",
                "branch": "Mechanical",
                "cgpa": 7.5,
                "phone": "7654321098",
                "skills": "AutoCAD, SolidWorks, ANSYS, Python, MATLAB, 3D Printing, Manufacturing Processes, Thermodynamics",
                "experience": "Designed a solar-powered vehicle chassis using SolidWorks. Intern at Tata Motors on assembly line optimization."
            }
        ]

        created_students = []
        for s in students_data:
            u = user_datastore.create_user(
                email=s["email"],
                password=hash_password(s["pwd"]),
                roles=[student_role]
            )
            std = Student(
                user=u,
                name=s["name"],
                branch=s["branch"],
                cgpa=s["cgpa"],
                phone=s["phone"],
                skills=s.get("skills", ""),
                experience=s.get("experience", "")
            )
            db.session.add(std)
            created_students.append(std)
            print(f"[SEED] Student user created: {s['email']}")

        db.session.flush() # Ensure IDs are populated

        # Provide demo resumes so students can apply immediately during viva demo.
        upload_folder = app.config.get("UPLOAD_FOLDER", "uploads")
        resume_dir = os.path.join(upload_folder, "resumes")
        os.makedirs(resume_dir, exist_ok=True)
        for student in created_students:
            safe_name = student.name.lower().replace(" ", "_")
            resume_path = os.path.join(resume_dir, f"{safe_name}_resume.pdf")
            if not os.path.exists(resume_path):
                with open(resume_path, "wb") as resume_file:
                    resume_file.write(b"%PDF-1.4\n% Demo resume for seeded student\n")
            student.resume_path = resume_path

        drives_data = [
            {
                "company_id": created_companies[0].id, # Google
                "title": "Software Engineering Intern 2026",
                "role_offered": "SWE Intern",
                "package_lpa": 12.0,
                "location": "Bangalore / Hyderabad",
                "eligibility_cgpa": 8.0,
                "eligible_branches": "Computer Science,Electronics",
                "deadline": datetime.now(timezone.utc) + timedelta(days=15),
                "is_approved": True,
                "status": "open",
                "description": "Looking for strong engineers with experience in Python, JavaScript, React, REST APIs, Docker, Git, and cloud platforms like AWS or GCP. Familiarity with Flask, Vue.js, or similar frameworks is a plus."
            },
            {
                "company_id": created_companies[1].id, # Microsoft
                "title": "Full Stack Developer - New Grad",
                "role_offered": "Software Engineer 1",
                "package_lpa": 18.0,
                "location": "Noida",
                "eligibility_cgpa": 7.5,
                "eligible_branches": "Computer Science",
                "deadline": datetime.now(timezone.utc) + timedelta(days=10),
                "is_approved": True,
                "status": "open",
                "description": "Build scalable full-stack applications using React, Node.js, Python, and Azure cloud services. Experience with SQL databases, REST APIs, microservices architecture, and Git required."
            },
            {
                "company_id": created_companies[2].id, # Tesla
                "title": "Embedded Systems Engineer",
                "role_offered": "Hardware Engineer",
                "package_lpa": 25.0,
                "location": "Palo Alto (Remote Option)",
                "eligibility_cgpa": 8.5,
                "eligible_branches": "Electronics,Mechanical",
                "deadline": datetime.now(timezone.utc) + timedelta(days=20),
                "is_approved": True,
                "status": "open",
                "description": "Design and develop embedded firmware for automotive systems. Requires Embedded C, RTOS, ARM Cortex, MATLAB, PCB design, and signal processing. Experience with VHDL, FPGA, or SolidWorks is a plus."
            },
            {
                "company_id": created_companies[1].id, # Microsoft
                "title": "Cloud Platform Engineer - Pending Approval",
                "role_offered": "Cloud Engineer",
                "package_lpa": 20.0,
                "location": "Hyderabad",
                "eligibility_cgpa": 8.0,
                "eligible_branches": "Computer Science,Electronics",
                "deadline": datetime.now(timezone.utc) + timedelta(days=12),
                "is_approved": False,
                "status": "open",
                "description": "Pending drive for admin approval demo."
            }
        ]

        created_drives = []
        for d in drives_data:
            drive = PlacementDrive(**d)
            db.session.add(drive)
            created_drives.append(drive)
            print(f"[SEED] Placement Drive created: {d['title']}")

        db.session.flush()

        applications_data = [
            {
                "student_id": created_students[0].id, # Alok -> Google
                "drive_id": created_drives[0].id,
                "status": "selected",
                "ats_score": 85.5,
                "cover_letter": "I love coding and scale."
            },
            {
                "student_id": created_students[0].id, # Alok -> Microsoft
                "drive_id": created_drives[1].id,
                "status": "shortlisted",
                "ats_score": 78.0,
                "cover_letter": "Excited to work on Azure."
            },
            {
                "student_id": created_students[1].id, # Priya -> Google
                "drive_id": created_drives[0].id,
                "status": "rejected",
                "ats_score": 72.5,
                "cover_letter": "Interested in distributed systems.",
                "company_feedback": "Good fundamentals, but current role requires stronger backend system design depth."
            },
            {
                "student_id": created_students[1].id, # Priya -> Tesla
                "drive_id": created_drives[2].id,
                "status": "selected",
                "ats_score": 91.0,
                "cover_letter": "Passionate about electric vehicles."
            },
            {
                "student_id": created_students[2].id, # Rohit -> Tesla
                "drive_id": created_drives[2].id,
                "status": "shortlisted",
                "ats_score": 88.0,
                "cover_letter": "Mechanical engineer for the future."
            },
            {
                "student_id": created_students[2].id, # Rohit -> Microsoft
                "drive_id": created_drives[1].id,
                "status": "withdrawn",
                "ats_score": 65.0,
                "cover_letter": "Ready to learn and grow."
            },
        ]

        created_applications = []
        for a in applications_data:
            app_obj = Application(**a)
            db.session.add(app_obj)
            created_applications.append(app_obj)
            print(f"[SEED] Application created: student {a['student_id']} -> drive {a['drive_id']} ({a['status']})")

        db.session.flush()

        placements_data = [
            {
                "student_id": created_students[0].id,
                "company_id": created_companies[0].id,
                "position": "SWE Intern",
                "salary": 12.0,
                "joining_date": (datetime.now(timezone.utc) + timedelta(days=60)).date(),
            },
            {
                "student_id": created_students[1].id,
                "company_id": created_companies[2].id,
                "position": "Hardware Engineer",
                "salary": 25.0,
                "joining_date": (datetime.now(timezone.utc) + timedelta(days=45)).date(),
            },
        ]
        for p in placements_data:
            db.session.add(Placement(**p))
            print(f"[SEED] Placement recorded: student {p['student_id']} at company {p['company_id']}")

        interviews_data = [
            {
                "application_id": created_applications[1].id, # Alok -> Microsoft (shortlisted)
                "scheduled_at": datetime.now(timezone.utc) + timedelta(days=2, hours=10),
                "location": "Microsoft Teams",
                "interview_type": "online",
                "status": "scheduled",
                "notes": "Technical screening - DSA + System Design"
            },
            {
                "application_id": created_applications[4].id, # Rohit -> Tesla (shortlisted)
                "scheduled_at": datetime.now(timezone.utc) + timedelta(days=3, hours=14),
                "location": "Palo Alto Office",
                "interview_type": "in-person",
                "status": "scheduled",
                "notes": "Mechanical design round"
            }
        ]

        for i in interviews_data:
            interview = Interview(**i)
            db.session.add(interview)
            print(f"[SEED] Interview scheduled for application {i['application_id']}")

        db.session.commit()
        print("[SEED] Database seeded successfully with full test suite.")
        print("[SEED] Demo credentials:")
        print("  Admin: admin@test.com / admin123")
        print("  Company (approved): hiring@google.com / password123")
        print("  Company (pending): talent@nvidia.com / password123")
        print("  Student: alok@student.edu / password123")


if __name__ == "__main__":
    seed()
