# LaunchPad

![447bdf7a-a823-4d13-9bce-6a9acef5e4a4](https://github.com/user-attachments/assets/24f44560-98a1-4564-b7ae-e13780385cb9)


Hey! Welcome to LaunchPad.

This is a web application for managing campus recruitment, created as part of the MAD-2 Project. This platform connects institutes, companies, and students, moving away from messy spreadsheets and manual email chains to a centralized, automated system.

## What's Inside?

The platform is broken down into three main experiences:

**For the Institute (Admin):**

- **Gatekeeping:** You're the moderator. Approve or reject company sign-ups and specific placement drives to maintain quality.
- **Overwatch:** Easily search for and manage students or recruiters. (You can also blacklist them if necessary).
- **Reports:** Automated monthly reports are generated to summarize selection rates and drive activity.

**For Recruiters:**

- **Launch Drives:** Post new job openings and events for the students.
- **Manage Candidates:** Check out student applications, shortlist the best fits, and update interview statuses right on the platform.
- **Track Progress:** Schedule interviews and finalize candidates without needing to juggle third-party tools.

**For Students:**

- **Profile & Resumes:** Fill out your academic profile and upload your resume directly into the system.
- **Find Jobs:** Browse and filter available jobs by branch or CGPA limits, so you don't waste time looking at roles you aren't eligible for.
- **Track Applications:** Know exactly where you stand with real-time updates on your application status.

## Technologies Used

- Python
- Flask
- Flask-SQLAlchemy
- Redis
- Celery
- Vue.js 3
- Bootstrap 5
- Chart.js
- MailHog 

## Project Structure

```text
├── README.md
├── api_docs.yaml
├── backend/
│   ├── main.py
│   ├── seed.py
│   ├── requirements.txt
│   ├── celery_worker.py
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── extensions.py
│   │   ├── models.py
│   │   ├── routes/
│   │   │   ├── admin.py
│   │   │   ├── auth.py
│   │   │   ├── company.py
│   │   │   └── student.py
│   │   └── utils/
│   ├── tasks/
│   │   ├── __init__.py
│   │   ├── mail_tasks.py
│   │   └── report_tasks.py
│   ├── uploads/
│   └── instance/
└── frontend/
    ├── package.json
    ├── package-lock.json
    ├── vite.config.js
    ├── index.html
    ├── public/
    └── src/
        ├── main.js
        ├── App.vue
        ├── api.js
        ├── assets/
        │   ├── auth.css
        │   ├── landing.css
        │   └── main.css
        ├── components/
        │   ├── Navbar.vue
        │   ├── Toast.vue
        │   └── landing/
        │       ├── LandingCTA.vue
        │       ├── LandingFeatures.vue
        │       ├── LandingFooter.vue
        │       ├── LandingHero.vue
        │       └── LandingNavbar.vue
        ├── router/
        │   └── index.js
        ├── stores/
        │   ├── auth.js
        │   └── toast.js
        ├── utils/
        │   └── date.js
        └── views/
            ├── Landing.vue
            ├── Login.vue
            ├── Register.vue
            ├── admin/
            │   ├── Companies.vue
            │   ├── Dashboard.vue
            │   ├── Drives.vue
            │   └── Students.vue
            ├── company/
            │   ├── Applications.vue
            │   ├── Dashboard.vue
            │   ├── DriveCreate.vue
            │   └── Drives.vue
            └── student/
                ├── Applications.vue
                ├── Dashboard.vue
                ├── Drives.vue
                └── Profile.vue
```

## Getting Started Locally


### 1. Set up the Backend

```bash
cd backend
uv venv --python 3.12 venv
uv pip install --python venv/bin/python -r requirements.txt
```
**Seed the database:** We populate the DB with admin and other relevant demo data:

```bash
./venv/bin/python seed.py
```

### 2. Start the Services

**Terminal 1 — Redis + Celery Worker + Celery Beat:**

```bash
cd backend
redis-server --port 6379 --save "" --appendonly no &
./venv/bin/python -m celery -A celery_worker.celery_app worker --loglevel=info &
./venv/bin/python -m celery -A celery_worker.celery_app beat --loglevel=info
```

**Terminal 2 — API Server:**

```bash
cd backend
./venv/bin/python main.py
```

**Terminal 3 — MailHog:**

```bash
mailhog
```

**Terminal 4 — Vue Frontend:**

```bash
cd frontend
npm install
npm run dev
```
