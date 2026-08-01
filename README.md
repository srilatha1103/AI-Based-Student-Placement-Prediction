<<<<<<< HEAD
# AI-Based Student Placement Prediction System with Company Recruitment Portal & Email Notification Engine

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/)
[![Framework](https://img.shields.io/badge/framework-Flask-green.svg)](https://flask.palletsprojects.com/)
[![ML Model](https://img.shields.io/badge/ML-Random%20Forest%20(85.67%25)-orange.svg)](https://scikit-learn.org/)
[![Database](https://img.shields.io/badge/database-SQLite3%20Indexed-lightgrey.svg)](https://www.sqlite.org/)

An enterprise-grade, end-to-end web platform that leverages Machine Learning, Natural Language Processing, AI Candidate Matching, and Asynchronous Multi-Threaded Email Notifications to optimize institutional campus recruitment.

---

## Table of Contents
1. [Key Features](#key-features)
2. [Folder Structure](#folder-structure)
3. [Installation & Local Setup](#installation--local-setup)
4. [User Manual](#user-manual)
   - [Student Portal Guide](#student-portal-guide)
   - [Company Recruitment Portal Guide](#company-recruitment-portal-guide)
   - [Admin Portal Guide](#admin-portal-guide)
5. [API Documentation](#api-documentation)
6. [Database Schema Documentation](#database-schema-documentation)
7. [Deployment Instructions](#deployment-instructions)
8. [Automated Testing](#automated-testing)

---

## Key Features

- **Random Forest ML Placement Predictor:** Predicts student placement probability percentage using 13 features with 85.67% accuracy.
- **AI Resume Analyzer:** NLP regex & taxonomy parser for PDF/DOCX/TXT resumes scoring (0-100), extracting technical skills, and generating PDF analysis reports.
- **AI Mock Interview Engine:** Interactive simulator with 10 technical domains & aptitude questions, keyword coverage grading, and instant feedback.
- **Company Recruitment Portal:** Recruiter registration, logo uploads, job posting management, and weighted AI Candidate Matching (Skills, CGPA, ML Score, Internships, Certifications).
- **Multi-Threaded Notification & Email Engine:** Asynchronous background SMTP worker, in-app notification center, live bell unread badge, and HTML email templates.
- **Admin Control Panel:** Dataset uploads, model re-training, student & company account management, and system error logging.

---

## Folder Structure

```
student placement prediction/
├── app.py                      # Main Flask Application Entry Point & Error Handlers
├── database.py                 # SQLite Schema, Performance Indexes, & Queries
├── train_model.py              # ML Dataset Generation & Random Forest Classifier
├── resume_analyzer.py          # NLP Resume Parser & PDF Report Engine
├── mock_interview_engine.py    # AI Question Bank & Keyword Evaluation
├── notification_service.py     # Asynchronous SMTP Email & In-App Notification Service
├── test_system.py              # Automated Unit & Integration Test Suite
├── requirements.txt            # Python Package Dependencies
├── Procfile                    # Production Web Process Config (Gunicorn)
├── .env.example                # Production Environment Variables Template
├── routes/
│   ├── public.py               # Home, Public Predictor, Model Analytics Routes
│   ├── student.py              # Student Portal Auth, Dashboard, Resume, Mock Interview
│   ├── company.py              # Company Recruitment Portal Auth, Job Mgmt, Candidates
│   ├── admin.py                # Admin Dashboard, Dataset, Model Re-training Routes
│   └── notifications.py        # Notification Hub & RESTful APIs
├── static/
│   ├── css/                    # Custom Stylesheets (student.css, company.css)
│   ├── js/                     # Client Scripts & Chart.js Configs
│   └── uploads/                # Profile Photos, Resumes & Company Logos
├── templates/
│   ├── base.html               # Base Public Master Layout
│   ├── index.html              # Main Landing Page
│   ├── predict.html            # Public ML Predictor Form
│   ├── analytics.html          # Model Insights & Confusion Matrix
│   ├── student/                # Student Dashboard & Feature Views
│   ├── company/                # Recruiter Dashboard & Job Management Views
│   ├── admin/                  # Admin Control Panel Views
│   ├── notifications/          # Notification Center Hub View
│   ├── email/                  # Reusable HTML Email Templates
│   └── errors/                 # Custom 404, 500, 403 HTTP Error Pages
├── models/
│   ├── model.pkl               # Serialized Random Forest Classifier
│   ├── scaler.pkl              # Serialized StandardScaler
│   └── metrics.json            # Model Evaluation Performance Metrics
└── dataset/
    └── placement.csv           # Synthetic Placement Dataset (1,500 rows)
```

---

## Installation & Local Setup

### Prerequisites
- Python 3.9 or higher
- Git & Pip package manager

### Step-by-Step Setup

1. **Clone the Repository:**
   ```bash
   git clone <repository_url>
   cd "student placement prediction"
   ```

2. **Create and Activate Virtual Environment:**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Database and Train ML Model:**
   ```bash
   python -c "import database, train_model; database.init_db(); train_model.train_and_export_model()"
   ```

5. **Run Application Server:**
   ```bash
   python app.py
   ```
   Open browser at `http://127.0.0.1:5000`.

---

## User Manual

### Default Credentials

| Portal | Username / Email | Password |
|---|---|---|
| **Admin Portal** | `admin` | `admin123` |
| **Student Portal** | `student@college.edu` | `student123` |
| **Company Portal** | `company@techcorp.com` | `company123` |

### Student Portal Guide
1. **Registration:** Register at `/student/register` with Register Number, Department, CGPA, and Skills.
2. **Predict Placement:** Calculate ML placement chance under *Prediction History* or *Predict Chance*.
3. **AI Resume Analysis:** Upload PDF/DOCX resume at `/student/resume-analyzer` to get resume score and missing keywords.
4. **AI Mock Interview:** Select topic at `/student/mock-interview/start` to practice questions with AI scoring.
5. **Explore Campus Jobs:** Browse active jobs posted by recruiter companies and click *Apply Now*.

### Company Recruitment Portal Guide
1. **Recruiter Login:** Access portal at `/company/login`.
2. **Post Job:** Navigate to *Post New Job*, specify Job Title, Minimum CGPA, Required Skills, Package, and Deadline.
3. **AI Candidate Matching:** View candidate applications sorted automatically by AI match score %.
4. **Schedule Interview:** Click *Schedule Interview* on shortlisted candidates; fill date, time, venue/link to send instant email invitations.

### Admin Portal Guide
1. **Login:** Access at `/admin/login` using `admin / admin123`.
2. **Dataset & Training:** Upload new CSV dataset or click *Train Model Now* to retrain the Random Forest model.
3. **Manage Accounts:** Monitor registered students, company recruiters, and email logs.

---

## API Documentation

| Endpoint | Method | Access | Description |
|---|---|---|---|
| `/api/predict` | POST | Public | Calculates placement probability JSON from input features |
| `/notifications/api/unread-count` | GET | Authenticated | Returns JSON unread notification count for current session user |
| `/notifications/api/<id>/read` | POST | Authenticated | Marks specific notification as read |
| `/notifications/api/read-all` | POST | Authenticated | Marks all notifications as read for current user |
| `/notifications/api/<id>/delete` | POST | Authenticated | Deletes notification record |
| `/notifications/api/analytics` | GET | Admin / Recruiter | Returns JSON email delivery and notification analytics |
| `/company/api/analytics-data` | GET | Company | Returns Chart.js data for company recruitment dashboard |

---

## Database Schema Documentation

The system utilizes SQLite 3 with performance indexes (`idx_student_users_reg_email`, `idx_companies_email`, `idx_jobs_company_status`, `idx_job_applications_job_student`, `idx_notifications_user`).

### Key Tables Overview
1. **`student_users`**: Stores student registration data, CGPA, academic scores, skills list, and hashed passwords.
2. **`companies`**: Stores company profiles, industry, location, website, contact info, and company logo filename.
3. **`jobs`**: Stores posted job opportunities, minimum CGPA cutoff, required skills, salary, location, and status (`Active` / `Closed`).
4. **`job_applications`**: Junction table linking jobs and students with AI match scores and application status (`Applied`, `Shortlisted`, `Interview Scheduled`, `Selected`, `Rejected`).
5. **`interviews`**: Stores scheduled interview details, date, time, mode (`Online` / `Offline`), and venue/link.
6. **`notifications`**: Stores in-app user notifications, title, message, type, read status, and email delivery status.
7. **`email_logs`**: Logs all outgoing SMTP email dispatches, recipients, subjects, body HTML, delivery status, and errors.

---

## Deployment Instructions

### Deploying to Render
1. Push code to GitHub repository.
2. Log in to [Render.com](https://render.com/) and click **New Web Service**.
3. Connect your repository.
4. Set Build Command: `pip install -r requirements.txt`
5. Set Start Command: `gunicorn app:app`
6. Add Environment Variables (from `.env.example`):
   - `SECRET_KEY`: `<your_random_production_key>`
   - `MAIL_SERVER`: `smtp.gmail.com`
   - `MAIL_PORT`: `587`
   - `MAIL_USERNAME`: `<your_email>`
   - `MAIL_PASSWORD`: `<your_app_password>`
7. Click **Deploy Web Service**.

---

## Automated Testing

Run the integration test suite to verify system health:
```bash
python test_system.py
```
**Expected Result:** `Ran 9 tests in ~0.9s - OK (100% Pass)`
=======
# AI-Based-Student-Placement-Prediction
AI-Based Student Placement Prediction System using Python Flask and Machine Learning
>>>>>>> d6689087c3456ee73abdf3919b90f2a9486ab71e
