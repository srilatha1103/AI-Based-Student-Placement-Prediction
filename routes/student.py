import os
import json
import numpy as np
import joblib
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app, send_file
from werkzeug.utils import secure_filename
import database
import train_model
import notification_service
import resume_analyzer as resume_analyzer_lib
import mock_interview_engine



student_bp = Blueprint('student', __name__, url_prefix='/student')

def student_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('student_logged_in') or not session.get('student_reg'):
            flash('Please log in to access your Student Portal.', 'warning')
            return redirect(url_for('student.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------------------------------------
# Authentication Routes
# ---------------------------------------------------------
@student_bp.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('student_logged_in'):
        return redirect(url_for('student.dashboard'))

    departments_list = train_model.DEPARTMENTS

    if request.method == 'POST':
        data = {
            'student_name': request.form.get('student_name', '').strip(),
            'register_number': request.form.get('register_number', '').strip().upper(),
            'email': request.form.get('email', '').strip().lower(),
            'password': request.form.get('password', '').strip(),
            'department': request.form.get('department', '').strip(),
            'cgpa': request.form.get('cgpa', 7.5),
            'tenth_percentage': request.form.get('tenth_percentage', 75.0),
            'twelfth_percentage': request.form.get('twelfth_percentage', 75.0),
            'aptitude_score': request.form.get('aptitude_score', 70),
            'coding_score': request.form.get('coding_score', 70),
            'communication_skill': request.form.get('communication_skill', 'Good'),
            'internship': request.form.get('internship', 'No'),
            'certifications_count': request.form.get('certifications_count', 0),
            'projects_count': request.form.get('projects_count', 1),
            'backlogs': request.form.get('backlogs', 0)
        }

        if not data['student_name'] or not data['register_number'] or not data['email'] or not data['password']:
            flash('All required fields must be filled!', 'danger')
            return render_template('student/register.html', departments=departments_list, data=data)

        if len(data['password']) < 6:
            flash('Password must be at least 6 characters long.', 'warning')
            return render_template('student/register.html', departments=departments_list, data=data)

        success, err = database.register_student(data)
        if success:
            notification_service.notify_student_registration(data['register_number'], data['email'], data['student_name'])
            notification_service.notify_admin_system_alert(
                'New Student Registration',
                f"Student {data['student_name']} ({data['register_number']}) from {data['department']} has registered.",
                'info'
            )
            flash('Account registered successfully! Welcome email sent.', 'success')
            return redirect(url_for('student.login'))
        else:
            flash(f"Registration failed: {err}", 'danger')

    return render_template('student/register.html', departments=departments_list)

@student_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('student_logged_in'):
        return redirect(url_for('student.dashboard'))

    if request.method == 'POST':
        email_or_reg = request.form.get('email_or_reg', '').strip()
        password = request.form.get('password', '').strip()

        student = database.verify_student(email_or_reg, password)
        if student:
            session['student_logged_in'] = True
            session['student_reg'] = student['register_number']
            session['student_name'] = student['student_name']
            session['student_email'] = student['email']
            flash(f"Welcome back, {student['student_name']}!", 'success')
            next_url = request.args.get('next')
            return redirect(next_url or url_for('student.dashboard'))
        else:
            flash('Invalid email/register number or password. Please try again.', 'danger')

    return render_template('student/login.html')

@student_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out of the Student Portal.', 'info')
    return redirect(url_for('student.login'))

@student_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        if new_password != confirm_password:
            flash('Passwords do not match!', 'danger')
        elif len(new_password) < 6:
            flash('New password must be at least 6 characters long.', 'warning')
        else:
            success, err = database.reset_student_password_by_email(email, new_password)
            if success:
                flash('Your password has been reset successfully! Please log in with your new password.', 'success')
                return redirect(url_for('student.login'))
            else:
                flash(f"Password reset failed: {err}", 'danger')

    return render_template('student/forgot_password.html')

@student_bp.route('/change-password', methods=['GET', 'POST'])
@student_login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password', '').strip()
        new_password = request.form.get('new_password', '').strip()
        confirm_password = request.form.get('confirm_password', '').strip()

        student_reg = session.get('student_reg')
        student = database.get_student_user(student_reg)

        if not database.verify_student(student_reg, current_password):
            flash('Current password is incorrect!', 'danger')
        elif new_password != confirm_password:
            flash('New passwords do not match!', 'danger')
        elif len(new_password) < 6:
            flash('New password must be at least 6 characters long.', 'warning')
        else:
            database.update_student_user_password(student_reg, new_password)
            flash('Your password has been updated successfully!', 'success')
            return redirect(url_for('student.dashboard'))

    return render_template('student/change_password.html')

# ---------------------------------------------------------
# Student Dashboard & Profile
# ---------------------------------------------------------
@student_bp.route('/')
@student_bp.route('/dashboard')
@student_login_required
def dashboard():
    student_reg = session.get('student_reg')
    student = database.get_student_user(student_reg)

    if not student:
        session.clear()
        flash('Student record not found. Please log in again.', 'warning')
        return redirect(url_for('student.login'))

    completion_pct = database.calculate_profile_completion(student)
    predictions = database.get_student_predictions(student_reg)
    latest_pred = predictions[0] if predictions else None

    notifications = database.get_student_notifications(student_reg)
    unread_count = sum(1 for n in notifications if n['is_read'] == 0)

    metrics = {}
    metrics_path = os.path.join('models', 'metrics.json')
    if os.path.exists(metrics_path):
        try:
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)
        except Exception:
            pass

    return render_template(
        'student/dashboard.html',
        student=student,
        completion_pct=completion_pct,
        latest_pred=latest_pred,
        notifications=notifications[:4],
        unread_count=unread_count,
        metrics=metrics
    )

@student_bp.route('/profile', methods=['GET', 'POST'])
@student_login_required
def profile():
    student_reg = session.get('student_reg')
    student = database.get_student_user(student_reg)
    departments_list = train_model.DEPARTMENTS

    if request.method == 'POST':
        data = {
            'student_name': request.form.get('student_name', student['student_name']).strip(),
            'department': request.form.get('department', student['department']).strip(),
            'cgpa': request.form.get('cgpa', student['cgpa']),
            'tenth_percentage': request.form.get('tenth_percentage', student['tenth_percentage']),
            'twelfth_percentage': request.form.get('twelfth_percentage', student['twelfth_percentage']),
            'aptitude_score': request.form.get('aptitude_score', student['aptitude_score']),
            'coding_score': request.form.get('coding_score', student['coding_score']),
            'communication_skill': request.form.get('communication_skill', student['communication_skill']),
            'internship': request.form.get('internship', student['internship']),
            'certifications_count': request.form.get('certifications_count', student['certifications_count']),
            'projects_count': request.form.get('projects_count', student['projects_count']),
            'backlogs': request.form.get('backlogs', student['backlogs']),
            'skills_list': request.form.get('skills_list', '').strip(),
            'certifications_details': request.form.get('certifications_details', '').strip(),
            'internship_details': request.form.get('internship_details', '').strip(),
            'project_details': request.form.get('project_details', '').strip()
        }

        # Handle Profile Photo Upload
        if 'profile_photo' in request.files:
            file = request.files['profile_photo']
            if file and file.filename != '':
                ext = file.filename.rsplit('.', 1)[-1].lower()
                if ext in ['png', 'jpg', 'jpeg', 'webp']:
                    filename = f"photo_{student_reg}_{int(os.times().system)}.{ext}"
                    upload_folder = os.path.join('static', 'uploads', 'profile_photos')
                    os.makedirs(upload_folder, exist_ok=True)
                    filepath = os.path.join(upload_folder, filename)
                    file.save(filepath)
                    data['profile_photo'] = filename

        success, err = database.update_student_user_profile(student_reg, data)
        if success:
            session['student_name'] = data['student_name']
            flash('Your profile details have been updated successfully!', 'success')
            return redirect(url_for('student.profile'))
        else:
            flash(f"Profile update failed: {err}", 'danger')

    completion_pct = database.calculate_profile_completion(student)
    return render_template('student/profile.html', student=student, departments=departments_list, completion_pct=completion_pct)

# ---------------------------------------------------------
# Placement Prediction Module
# ---------------------------------------------------------
@student_bp.route('/predict', methods=['GET', 'POST'])
@student_login_required
def predict():
    student_reg = session.get('student_reg')
    student = database.get_student_user(student_reg)

    if request.method == 'POST':
        # Load ML artifacts
        model_path = os.path.join('models', 'model.pkl')
        fallback_path = os.path.join('models', 'placement_model.pkl')
        scaler_path = os.path.join('models', 'scaler.pkl')

        model = None
        if os.path.exists(model_path):
            model = joblib.load(model_path)
        elif os.path.exists(fallback_path):
            model = joblib.load(fallback_path)

        scaler = joblib.load(scaler_path) if os.path.exists(scaler_path) else None

        if model is None or scaler is None:
            flash('ML Model artifacts missing. Please notify system admin to train the model.', 'danger')
            return redirect(url_for('student.dashboard'))

        cgpa = float(request.form.get('cgpa', student['cgpa']))
        tenth_percentage = float(request.form.get('tenth_percentage', student['tenth_percentage']))
        twelfth_percentage = float(request.form.get('twelfth_percentage', student['twelfth_percentage']))

        aptitude_score = int(request.form.get('aptitude_score', student['aptitude_score']))
        coding_score = int(request.form.get('coding_score', student['coding_score']))

        communication_skill = str(request.form.get('communication_skill', student['communication_skill'])).strip()
        internship_val = str(request.form.get('internship', student['internship'])).strip()

        certifications = int(request.form.get('certifications_count', student['certifications_count']))
        projects_completed = int(request.form.get('projects_count', student['projects_count']))
        backlogs = int(request.form.get('backlogs', student['backlogs']))

        comm_enc = {'Poor': 0, 'Average': 1, 'Good': 2, 'Excellent': 3}.get(communication_skill, 1)
        intern_enc = 1 if internship_val.lower() == 'yes' else 0

        DEPARTMENTS = train_model.DEPARTMENTS
        dept_onehot = [1 if student['department'] == d else 0 for d in DEPARTMENTS]

        feature_vector = [
            cgpa, tenth_percentage, twelfth_percentage, aptitude_score, coding_score,
            certifications, projects_completed, backlogs, comm_enc, intern_enc
        ] + dept_onehot

        scaled_input = scaler.transform(np.array([feature_vector]))
        prediction_class = int(model.predict(scaled_input)[0])
        probabilities = model.predict_proba(scaled_input)[0]
        placement_prob = float(probabilities[1])
        prob_percentage = round(placement_prob * 100, 1)

        if prob_percentage >= 75:
            status = 'High Probability'
            color = '#10b981'
            confidence = 'High Confidence (85%+ accuracy model)'
        elif prob_percentage >= 50:
            status = 'Moderate Chance'
            color = '#f59e0b'
            confidence = 'Moderate Confidence'
        else:
            status = 'Needs Improvement'
            color = '#ef4444'
            confidence = 'Action Required'

        # Log prediction to database
        database.log_prediction(
            student_name=student['student_name'],
            register_number=student_reg,
            department=student['department'],
            cgpa=cgpa,
            prediction=prediction_class,
            probability=prob_percentage,
            status=status
        )

        # Notify student
        database.add_student_notification(
            student_reg,
            'Placement Prediction Completed',
            f"Your AI placement probability is calculated as {prob_percentage}% ({status}). Check skill gap feedback for recommendations.",
            'prediction'
        )

        flash(f"AI Prediction completed! Your placement probability is {prob_percentage}%.", 'success')

        return render_template(
            'student/predict_result.html',
            student=student,
            prediction=prediction_class,
            probability=prob_percentage,
            status=status,
            color=color,
            confidence=confidence,
            inputs={
                'cgpa': cgpa, 'aptitude_score': aptitude_score, 'coding_score': coding_score,
                'communication_skill': communication_skill, 'internship': internship_val,
                'certifications': certifications, 'projects_completed': projects_completed, 'backlogs': backlogs
            }
        )

    return render_template('student/predict.html', student=student)

# ---------------------------------------------------------
# Skill Gap Analysis
# ---------------------------------------------------------
@student_bp.route('/skill-gap')
@student_login_required
def skill_gap():
    student_reg = session.get('student_reg')
    student = database.get_student_user(student_reg)
    predictions = database.get_student_predictions(student_reg)
    latest_pred = predictions[0] if predictions else None

    # Generate personalized recommendations
    gaps = []
    suggestions = {
        'missing_skills': [],
        'coding_tips': [],
        'aptitude_tips': [],
        'communication_tips': [],
        'internship_recs': [],
        'certification_recs': []
    }

    # 1. CGPA & Academic
    if student['cgpa'] < 7.0:
        gaps.append('Academic CGPA below 7.0 (recruitment eligibility risk)')
    elif student['cgpa'] < 8.0:
        suggestions['coding_tips'].append('Maintain CGPA above 8.0 to qualify for Tier-1 technology cutoffs.')

    # 2. Coding Score Analysis
    if student['coding_score'] < 65:
        gaps.append('Coding Score below 65 (Technical Round Risk)')
        suggestions['coding_tips'].extend([
            'Practice Data Structures & Algorithms daily on LeetCode (Arrays, Trees, Graphs, Dynamic Programming).',
            'Target completing at least 50 medium-level coding problems in Python/Java/C++.',
            'Participate in weekly online coding contests on CodeChef or HackerRank.'
        ])

    # 3. Aptitude Score Analysis
    if student['aptitude_score'] < 65:
        gaps.append('Aptitude Score below 65 (Initial Screening Risk)')
        suggestions['aptitude_tips'].extend([
            'Focus on Quantitative Aptitude (Speed Math, Ratios, Time & Work, Probability).',
            'Practice Logical Reasoning & Data Interpretation mock tests daily.',
            'Aim for 75+ in timed practice tests on IndiaBIX or GeeksforGeeks.'
        ])

    # 4. Soft Skills & Communication
    if student['communication_skill'] in ['Poor', 'Average']:
        gaps.append('Communication level needs polish for HR & Managerial rounds')
        suggestions['communication_tips'].extend([
            'Attend mock HR interview sessions and practice STAR method responses.',
            'Enhance self-introduction and project explanation articulation.',
            'Join Group Discussion (GD) practice circles.'
        ])

    # 5. Internships
    if student['internship'].lower() == 'no':
        gaps.append('No industrial internship experience recorded')
        suggestions['internship_recs'].extend([
            'Apply for virtual internships on AICTE / Forage / Internshala.',
            'Secure a 4 to 8-week summer apprenticeship in software development or data engineering.'
        ])

    # 6. Certifications & Projects
    if student['certifications_count'] == 0:
        suggestions['certification_recs'].extend([
            'Earn industry-recognized certifications (e.g. AWS Certified Cloud Practitioner, Meta Frontend Developer).',
            'Complete Python or Full-Stack web development certifications on Coursera or Udemy.'
        ])

    if student['projects_count'] < 2:
        suggestions['coding_tips'].append('Build at least 2 full-stack projects with live deployment links on GitHub.')

    return render_template(
        'student/skill_gap.html',
        student=student,
        latest_pred=latest_pred,
        gaps=gaps,
        suggestions=suggestions
    )

# ---------------------------------------------------------
# AI Career Roadmap
# ---------------------------------------------------------
@student_bp.route('/roadmap')
@student_login_required
def roadmap():
    student_reg = session.get('student_reg')
    student = database.get_student_user(student_reg)
    predictions = database.get_student_predictions(student_reg)
    latest_pred = predictions[0] if predictions else None

    dept = student['department']

    # Tailor roadmap based on department
    if 'Computer' in dept or 'Information' in dept or 'Artificial' in dept:
        languages = ['Python', 'Java', 'C++', 'JavaScript / TypeScript', 'SQL']
        certifications = ['AWS Certified Cloud Practitioner', 'Meta Full Stack Developer', 'Oracle Certified Java SE Specialist']
    elif 'Electronics' in dept or 'Electrical' in dept:
        languages = ['Python', 'C / C++', 'Embedded C', 'MATLAB', 'SQL']
        certifications = ['ARM Microcontroller Specialist', 'AWS Cloud Practitioner', 'Python for Data Science']
    else:
        languages = ['Python', 'SQL', 'C++', 'Excel / VBA']
        certifications = ['Python Data Analysis Specialist', 'Project Management Associate', 'AutoCAD / SolidWorks Specialist']

    learning_platforms = [
        {'name': 'LeetCode', 'icon': 'fa-code', 'desc': 'Practice Data Structures & Algorithms problems daily'},
        {'name': 'HackerRank', 'icon': 'fa-laptop-code', 'desc': 'Build domain certificates in Python, Problem Solving & SQL'},
        {'name': 'Coursera / Udemy', 'icon': 'fa-graduation-cap', 'desc': 'Master Full-Stack web apps, Cloud Computing & AI'},
        {'name': 'GeeksforGeeks', 'icon': 'fa-book-open', 'desc': 'Revise CS Fundamentals (OS, DBMS, Computer Networks)'}
    ]

    schedule = [
        {'week': 'Week 1: Core Fundamentals & Aptitude', 'tasks': 'Master Quantitative Aptitude formulas, practice 15 LeetCode Easy problems, update LinkedIn profile.'},
        {'week': 'Week 2: Data Structures & Project Polish', 'tasks': 'Practice Trees, Graphs, and HashMaps. Build/deploy end-to-end Web/AI project on GitHub.'},
        {'week': 'Week 3: Advanced Coding & CS Core', 'tasks': 'Solve Medium DSA problems under 30 mins. Revise SQL queries, DBMS normalization, and OS concepts.'},
        {'week': 'Week 4: Mock Interviews & HR Readiness', 'tasks': 'Conduct 3 mock technical interviews, refine resume formatting, prepare STAR method HR answers.'}
    ]

    interview_tips = [
        'Master the STAR Method (Situation, Task, Action, Result) for behavioral HR questions.',
        'Always explain your thought process out loud during live technical coding interviews.',
        'Be ready to discuss system architecture & trade-offs of your listed projects in depth.'
    ]

    resume_tips = [
        'Format resume using clean single-column ATS-friendly template.',
        'Quantify achievements (e.g. "Improved API response speed by 35%").',
        'Include clickable GitHub repository and live project demo links.'
    ]

    return render_template(
        'student/roadmap.html',
        student=student,
        latest_pred=latest_pred,
        languages=languages,
        certifications=certifications,
        platforms=learning_platforms,
        schedule=schedule,
        interview_tips=interview_tips,
        resume_tips=resume_tips
    )

# ---------------------------------------------------------
# Prediction History & PDF Report Generation
# ---------------------------------------------------------
@student_bp.route('/history')
@student_login_required
def history():
    student_reg = session.get('student_reg')
    student = database.get_student_user(student_reg)
    predictions = database.get_student_predictions(student_reg)

    metrics = {}
    metrics_path = os.path.join('models', 'metrics.json')
    if os.path.exists(metrics_path):
        try:
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)
        except Exception:
            pass

    return render_template(
        'student/history.html',
        student=student,
        predictions=predictions,
        metrics=metrics
    )

@student_bp.route('/report/<int:pred_id>/pdf')
@student_login_required
def download_report_pdf(pred_id):
    student_reg = session.get('student_reg')
    student = database.get_student_user(student_reg)
    prediction = database.get_prediction_by_id(pred_id)

    if not prediction or prediction['register_number'] != student_reg:
        flash('Prediction record not found or access denied.', 'danger')
        return redirect(url_for('student.history'))

    metrics = {}
    metrics_path = os.path.join('models', 'metrics.json')
    if os.path.exists(metrics_path):
        try:
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)
        except Exception:
            pass

    return render_template(
        'student/report_pdf.html',
        student=student,
        prediction=prediction,
        metrics=metrics
    )

# ---------------------------------------------------------
# Student Notifications
# ---------------------------------------------------------
@student_bp.route('/notifications')
@student_login_required
def notifications():
    student_reg = session.get('student_reg')
    notifications_list = database.get_student_notifications(student_reg)

    # Mark all as read
    for n in notifications_list:
        if n['is_read'] == 0:
            database.mark_notification_read(n['id'])

    return render_template('student/notifications.html', notifications=notifications_list)

# ---------------------------------------------------------
# Student Resume Analyzer & Job Recommendation Routes
# ---------------------------------------------------------
ALLOWED_RESUME_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_RESUME_EXTENSIONS

@student_bp.route('/resume-analyzer', methods=['GET', 'POST'])
@student_login_required
def resume_analyzer():
    student_reg = session.get('student_reg')
    student = database.get_student_user(student_reg)

    if request.method == 'POST':
        if 'resume' not in request.files:
            flash('No resume file attached! Please select a PDF or DOCX file.', 'danger')
            return redirect(request.url)

        file = request.files['resume']
        if file.filename == '':
            flash('No file selected for uploading.', 'warning')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_dir = os.path.join('static', 'uploads', 'resumes')
            os.makedirs(upload_dir, exist_ok=True)

            unique_filename = f"resume_{student_reg}_{os.urandom(3).hex()}_{filename}"
            filepath = os.path.join(upload_dir, unique_filename)
            file.save(filepath)

            file_ext = filename.rsplit('.', 1)[1].lower()

            # 1. Raw Text Extraction
            raw_text = resume_analyzer_lib.extract_text_from_file(filepath, file_ext)
            if not raw_text.strip():
                flash('Could not extract readable text from the resume. Please try a text-based PDF or Word document.', 'danger')
                return redirect(request.url)

            # 2. Information Parsing
            parsed_data = resume_analyzer_lib.parse_resume_text(raw_text)

            # Integrate student's profile CGPA if parsed CGPA defaulted
            if parsed_data.get('cgpa', 7.5) == 7.5 and student.get('cgpa'):
                parsed_data['cgpa'] = float(student['cgpa'])

            # 3. AI Scoring
            score_data = resume_analyzer_lib.calculate_ai_resume_score(parsed_data)

            # 4. Skill Gap Analysis
            skill_gap_data = resume_analyzer_lib.analyze_skill_gap(parsed_data['skills'])

            # 5. Job Recommendations
            job_recs = resume_analyzer_lib.recommend_job_roles(parsed_data)

            # 6. Learning Roadmap
            roadmap_data = resume_analyzer_lib.generate_learning_roadmap(skill_gap_data)


            # 7. Calculate Placement Probability using ML Model if present
            model_path = os.path.join('models', 'model.pkl')
            scaler_path = os.path.join('models', 'scaler.pkl')
            prob = 75.0
            if os.path.exists(model_path) and os.path.exists(scaler_path):
                try:
                    model = joblib.load(model_path)
                    scaler = joblib.load(scaler_path)
                    comm_code = 2 if student.get('communication_skill', 'Good') == 'Good' else (3 if student.get('communication_skill') == 'Excellent' else 1)
                    intern_code = 1 if student.get('internship', 'No').lower() == 'yes' or len(parsed_data['experience']) > 0 else 0
                    features_arr = np.array([[
                        student.get('cgpa', parsed_data.get('cgpa', 7.5)),
                        student.get('tenth_percentage', 80.0),
                        student.get('twelfth_percentage', 80.0),
                        student.get('aptitude_score', 75),
                        student.get('coding_score', 75),
                        comm_code, intern_code,
                        student.get('certifications_count', len(parsed_data.get('certifications', []))),
                        student.get('projects_count', len(parsed_data.get('projects', []))),
                        student.get('backlogs', 0)
                    ]])
                    scaled_feats = scaler.transform(features_arr)
                    prob_val = model.predict_proba(scaled_feats)[0][1]
                    prob = float(prob_val * 100)
                except Exception as ml_err:
                    print(f"[WARNING] ML Student Probability calculation fallback: {ml_err}")

            status_text = "High Chance" if prob >= 70 else ("Moderate" if prob >= 50 else "Needs Improvement")

            # 8. Save Record to Database linked to student_reg
            analysis_dict = {
                'register_number': student_reg,
                'filename': unique_filename,
                'original_filename': filename,
                'file_type': file_ext.upper(),
                'name': parsed_data.get('name', student.get('student_name', 'Student')),
                'email': parsed_data.get('email', student.get('email', '')),
                'phone': parsed_data.get('phone', 'Not Specified'),
                'skills_extracted': parsed_data.get('skills', []),
                'education_extracted': parsed_data.get('education', []),
                'projects_extracted': parsed_data.get('projects', []),
                'internships_extracted': parsed_data.get('experience', []),
                'certifications_extracted': parsed_data.get('certifications', []),
                'experience_extracted': parsed_data.get('experience', []),
                'resume_score': score_data['total_score'],
                'score_breakdown': score_data['breakdown'],
                'strengths': score_data['strengths'],
                'weaknesses': score_data['weaknesses'],
                'improvements': score_data['improvements'],
                'skill_gap_data': skill_gap_data,
                'job_recommendations': job_recs,
                'roadmap_data': roadmap_data,
                'placement_probability': round(prob, 1),
                'placement_status': status_text
            }

            analysis_id = database.save_resume_analysis(analysis_dict)
            flash('Resume uploaded and analyzed successfully with AI precision!', 'success')
            return redirect(url_for('student.view_resume_analysis', analysis_id=analysis_id))

        else:
            flash('Invalid file format! Only PDF (.pdf) and Word (.docx) files are supported.', 'danger')
            return redirect(request.url)

    # Fetch past resume analyses for student
    past_analyses = database.get_student_resume_analyses(student_reg)
    return render_template('student/resume_analyzer.html', student=student, past_analyses=past_analyses)

@student_bp.route('/resume-analysis/<int:analysis_id>')
@student_login_required
def view_resume_analysis(analysis_id):
    student_reg = session.get('student_reg')
    analysis = database.get_resume_analysis(analysis_id)
    if not analysis:
        flash('Resume analysis record not found.', 'danger')
        return redirect(url_for('student.resume_analyzer'))
    return render_template('resume_dashboard.html', analysis=analysis, is_student_portal=True)

@student_bp.route('/resume-analysis/<int:analysis_id>/download-pdf')
@student_login_required
def download_resume_pdf(analysis_id):
    analysis = database.get_resume_analysis(analysis_id)
    if not analysis:
        flash('Resume analysis record not found.', 'danger')
        return redirect(url_for('student.resume_analyzer'))

    pdf_dir = os.path.join('static', 'reports')
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_filename = f"Resume_Analysis_Report_{analysis_id}.pdf"
    pdf_path = os.path.join(pdf_dir, pdf_filename)
    resume_analyzer_lib.generate_resume_pdf_report(analysis, pdf_path)

    return send_file(pdf_path, as_attachment=True, download_name=pdf_filename)

# ---------------------------------------------------------
# Student AI Mock Interview Module Routes
# ---------------------------------------------------------
TECHNICAL_DOMAINS = [
    'Python', 'Java', 'C++', 'Web Development', 'Full Stack Development',
    'SQL', 'AI/ML', 'Data Structures', 'Operating Systems', 'Computer Networks'
]

@student_bp.route('/mock-interview')
@student_login_required
def mock_interview_hub():
    student_reg = session.get('student_reg')
    student = database.get_student_user(student_reg)
    stats = database.get_student_interview_stats(student_reg)
    past_interviews = database.get_student_mock_interviews(student_reg, limit=5)

    return render_template(
        'mock_interview/index.html',
        student=student,
        stats=stats,
        domains=TECHNICAL_DOMAINS,
        past_interviews=past_interviews,
        is_student_portal=True
    )

@student_bp.route('/mock-interview/start')
@student_login_required
def mock_interview_start():
    category = request.args.get('category', 'Technical')
    domain = request.args.get('domain', 'Python')

    questions = mock_interview_engine.generate_interview_questions(category, domain, count=4)
    qids = [q['id'] for q in questions]

    # Store lightweight QIDs in session to keep cookie size small
    session['current_interview_category'] = category
    session['current_interview_domain'] = domain
    session['current_interview_qids'] = qids

    # Default timer: 10 minutes (600s)
    timer_seconds = 600

    return render_template(
        'mock_interview/session.html',
        category=category,
        domain=domain,
        questions=questions,
        timer_seconds=timer_seconds,
        is_student_portal=True
    )

@student_bp.route('/mock-interview/submit', methods=['POST'])
@student_login_required
def mock_interview_submit():
    student_reg = session.get('student_reg')
    category = session.get('current_interview_category', 'Technical')
    domain = session.get('current_interview_domain', 'Python')
    qids = session.get('current_interview_qids', [])

    # Re-hydrate question objects from QIDs
    questions = mock_interview_engine.get_questions_by_ids(qids, category, domain)

    if not questions:
        flash('Interview session expired or invalid submission.', 'danger')
        return redirect(url_for('student.mock_interview_hub'))

    time_taken = int(request.form.get('time_taken_seconds', 180))

    answers_input = []
    for idx, q in enumerate(questions):
        user_ans = request.form.get(f'ans_{idx}', '').strip()
        answers_input.append({
            'question_obj': q,
            'user_answer': user_ans
        })

    # Evaluate Session
    eval_result = mock_interview_engine.evaluate_interview_session(category, domain, answers_input)

    # Save to SQLite Database
    data = {
        'register_number': student_reg,
        'category': category,
        'domain': domain,
        'total_questions': eval_result['total_questions'],
        'correct_answers': eval_result['correct_answers'],
        'total_score': eval_result['total_score'],
        'time_taken_seconds': time_taken,
        'strengths': eval_result['strengths'],
        'weaknesses': eval_result['weaknesses'],
        'feedback': eval_result['feedback'],
        'recommended_topics': eval_result['recommended_topics']
    }

    interview_id = database.save_mock_interview(data, eval_result['evaluated_answers'])
    flash(f"Mock Interview Completed! Score: {eval_result['total_score']:.1f}%", 'success')

    # Clear session temp questions
    session.pop('current_interview_qids', None)

    return redirect(url_for('student.mock_interview_result', interview_id=interview_id))


@student_bp.route('/mock-interview/result/<int:interview_id>')
@student_login_required
def mock_interview_result(interview_id):
    interview = database.get_mock_interview(interview_id)
    if not interview:
        flash('Interview result record not found.', 'danger')
        return redirect(url_for('student.mock_interview_hub'))

    return render_template('mock_interview/result.html', interview=interview, is_student_portal=True)

@student_bp.route('/mock-interview/dashboard')
@student_login_required
def mock_interview_dashboard():
    student_reg = session.get('student_reg')
    student = database.get_student_user(student_reg)
    stats = database.get_student_interview_stats(student_reg)
    all_interviews = database.get_student_mock_interviews(student_reg, limit=50)

    return render_template(
        'mock_interview/dashboard.html',
        student=student,
        stats=stats,
        interviews=all_interviews,
        is_student_portal=True
    )

@student_bp.route('/mock-interview/coding')
@student_login_required
def mock_interview_coding():
    problems = mock_interview_engine.CODING_PRACTICE_PROBLEMS
    return render_template('mock_interview/coding_practice.html', problems=problems, is_student_portal=True)

@student_bp.route('/mock-interview/gd-prep')
@student_login_required
def mock_interview_gd_prep():
    gd_data = mock_interview_engine.GD_PREPARATION_GUIDE
    return render_template('mock_interview/gd_prep.html', gd_data=gd_data, is_student_portal=True)

# ---------------------------------------------------------
# Student Campus Placement Jobs & Applications
# ---------------------------------------------------------
@student_bp.route('/jobs')
@student_login_required
def jobs():
    student_reg = session.get('student_reg')
    student = database.get_student_user(student_reg)

    active_jobs = database.get_all_active_jobs()
    applied_apps = database.get_job_applications(student_reg=student_reg)
    applied_job_ids = {a['job_id']: a['status'] for a in applied_apps}

    # Calculate personalized AI Match Score for each active job
    jobs_with_match = []
    for job in active_jobs:
        match_info = database.calculate_student_job_match(student, job)
        is_applied = job['id'] in applied_job_ids
        jobs_with_match.append({
            'job': job,
            'match_score': match_info['match_score'],
            'matching_skills': match_info['matching_skills'],
            'missing_skills': match_info['missing_skills'],
            'ai_recommendation': match_info['ai_recommendation'],
            'is_applied': is_applied,
            'application_status': applied_job_ids.get(job['id'])
        })

    jobs_with_match.sort(key=lambda x: x['match_score'], reverse=True)

    return render_template('student/jobs.html', jobs=jobs_with_match, student=student)

@student_bp.route('/jobs/<int:job_id>/apply', methods=['POST'])
@student_login_required
def apply_job(job_id):
    student_reg = session.get('student_reg')
    success, msg = database.apply_for_job(job_id, student_reg)
    if success:
        flash(msg, 'success')
    else:
        flash(msg, 'warning')
    return redirect(url_for('student.jobs'))

@student_bp.route('/my-applications')
@student_login_required
def my_applications():
    student_reg = session.get('student_reg')
    applications = database.get_job_applications(student_reg=student_reg)
    interviews = database.get_interviews(student_reg=student_reg)

    return render_template(
        'student/my_applications.html',
        applications=applications,
        interviews=interviews
    )



