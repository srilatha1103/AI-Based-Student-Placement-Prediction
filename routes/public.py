import os
import json
import numpy as np
import joblib
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, send_file
from werkzeug.utils import secure_filename
import database
import resume_analyzer

public_bp = Blueprint('public', __name__)

MODEL_PATH = os.path.join('models', 'model.pkl')
FALLBACK_MODEL_PATH = os.path.join('models', 'placement_model.pkl')
SCALER_PATH = os.path.join('models', 'scaler.pkl')
METRICS_PATH = os.path.join('models', 'metrics.json')

model = None
scaler = None
metrics = {}

def load_ml_artifacts():
    """Load machine learning model, scaler, and metrics into memory."""
    global model, scaler, metrics
    try:
        if os.path.exists(MODEL_PATH):
            model = joblib.load(MODEL_PATH)
        elif os.path.exists(FALLBACK_MODEL_PATH):
            model = joblib.load(FALLBACK_MODEL_PATH)

        if os.path.exists(SCALER_PATH):
            scaler = joblib.load(SCALER_PATH)

        if os.path.exists(METRICS_PATH):
            with open(METRICS_PATH, 'r') as f:
                metrics = json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load ML artifacts: {str(e)}")

# Load artifacts initially
load_ml_artifacts()

def generate_recommendations(features):
    """Generate tailored recommendations based on student's input metrics."""
    recommendations = []

    if features.get('cgpa', 7.0) < 7.0:
        recommendations.append({
            'category': 'Academic Performance',
            'type': 'critical',
            'icon': 'fa-graduation-cap',
            'title': 'Improve Academic CGPA',
            'text': 'Your CGPA is currently below 7.0. Focus on semester exams to raise your aggregate score above cutoff levels.'
        })
    elif features.get('cgpa', 7.0) < 8.0:
        recommendations.append({
            'category': 'Academic Performance',
            'type': 'warning',
            'icon': 'fa-book-open',
            'title': 'Aim for CGPA 8.0+',
            'text': 'A CGPA above 8.0 significantly increases your eligibility for top tier companies.'
        })

    if features.get('internships', 0) == 0:
        recommendations.append({
            'category': 'Work Experience',
            'type': 'critical',
            'icon': 'fa-briefcase',
            'title': 'Secure an Internship',
            'text': 'Having no internship experience makes your profile less competitive. Apply for virtual or summer internships.'
        })

    if features.get('projects', 0) < 2:
        recommendations.append({
            'category': 'Technical Portfolio',
            'type': 'warning',
            'icon': 'fa-code-branch',
            'title': 'Build Hands-On Projects',
            'text': 'Build at least 2 end-to-end projects featuring modern tech stacks with live demos or GitHub links.'
        })

    if features.get('aptitude_score', 70) < 65:
        recommendations.append({
            'category': 'Assessment Skills',
            'type': 'critical',
            'icon': 'fa-brain',
            'title': 'Practice Quantitative Aptitude',
            'text': 'Initial screening tests heavily focus on Quant and Logical Reasoning. Target 75+ in mock tests.'
        })

    coding_score = features.get('coding_score', 80)
    if coding_score < 60:
        recommendations.append({
            'category': 'Coding Skills',
            'type': 'critical',
            'icon': 'fa-code',
            'title': 'Improve Coding Proficiency',
            'text': 'Your coding score is below 60. Practice Data Structures & Algorithms on LeetCode or HackerRank.'
        })
    elif coding_score < 75:
        recommendations.append({
            'category': 'Coding Skills',
            'type': 'warning',
            'icon': 'fa-laptop-code',
            'title': 'Elevate Coding Quality',
            'text': 'Aim to score above 75 in coding test simulators to clear Tier-1 engineering screening filters.'
        })

    certifications = features.get('certifications', 0)
    if certifications == 0:
        recommendations.append({
            'category': 'Certifications',
            'type': 'warning',
            'icon': 'fa-certificate',
            'title': 'Earn Technical Certifications',
            'text': 'Consider certifications in Cloud (AWS/Azure) or specific web/data frameworks.'
        })

    if features.get('soft_skills_score', 3.5) < 3.5:
        recommendations.append({
            'category': 'Communication',
            'type': 'warning',
            'icon': 'fa-comments',
            'title': 'Enhance Soft Skills & HR Readiness',
            'text': 'Participate in mock interviews and presentation sessions to project confidence during HR rounds.'
        })

    if features.get('backlogs', 0) > 0:
        recommendations.append({
            'category': 'Academic Clearance',
            'type': 'critical',
            'icon': 'fa-exclamation-triangle',
            'title': 'Clear Active Backlogs',
            'text': f'You have {features["backlogs"]} backlog(s). Most recruiters specify 0 active backlogs as a prerequisite.'
        })

    if len(recommendations) == 0:
        recommendations.append({
            'category': 'Profile Strength',
            'type': 'success',
            'icon': 'fa-star',
            'title': 'Excellent Candidate Profile',
            'text': 'Your profile satisfies top-tier recruitment standards! Keep honing advanced problem-solving.'
        })

    return recommendations

@public_bp.route('/')
def home():
    """Render home page with dashboard stats."""
    load_ml_artifacts()
    return render_template('index.html', metrics=metrics)

@public_bp.route('/predict', methods=['GET'])
def predict_page():
    """Render prediction form page."""
    return render_template('predict.html')

@public_bp.route('/analytics')
def analytics_page():
    """Render model analytics & dataset insights page."""
    load_ml_artifacts()
    return render_template('analytics.html', metrics=metrics)

@public_bp.route('/api/predict', methods=['POST'])
def predict_api():
    """API endpoint for student placement prediction & log to DB."""
    global model, scaler

    load_ml_artifacts()
    if model is None or scaler is None:
        return jsonify({
            'success': False,
            'error': 'Machine learning model files not found. Please train the model first.'
        }), 500

    try:
        data = request.get_json() if request.is_json else request.form.to_dict()

        student_name = str(data.get('student_name', 'Student')).strip()
        register_number = str(data.get('register_number', 'N/A')).strip()
        department = str(data.get('department', 'Computer Science and Engineering')).strip()

        cgpa = float(data.get('cgpa', 7.0))
        tenth_percentage = float(data.get('tenth_percentage', 0.0))
        twelfth_percentage = float(data.get('twelfth_percentage', 0.0))

        aptitude_score = int(data.get('aptitude_score', 65))
        coding_score = int(data.get('coding_score', 65))

        communication_skill = str(data.get('communication_skill', 'Average')).strip()
        internship_val = str(data.get('internship', 'No')).strip()

        certifications = int(data.get('certifications', 0))
        projects_completed = int(data.get('projects_completed', 1))
        backlogs = int(data.get('backlogs', 0))

        communication_map = {'Poor': 1.5, 'Average': 2.8, 'Good': 4.0, 'Excellent': 5.0}
        soft_skills_score = communication_map.get(communication_skill, 3.5)

        internships = 1 if internship_val == 'Yes' else 0
        projects = projects_completed
        extracurricular = 1 if (certifications > 0 or projects > 2 or coding_score > 80) else 0

        cgpa = max(0.0, min(10.0, cgpa))
        internships = max(0, min(10, internships))
        projects = max(0, min(20, projects))
        aptitude_score = max(0, min(100, aptitude_score))
        soft_skills_score = max(1.0, min(5.0, soft_skills_score))
        extracurricular = 1 if extracurricular > 0 else 0
        backlogs = max(0, min(10, backlogs))

        input_dict = {
            'cgpa': cgpa,
            'internships': internships,
            'projects': projects,
            'aptitude_score': aptitude_score,
            'soft_skills_score': soft_skills_score,
            'extracurricular': extracurricular,
            'backlogs': backlogs,
            'coding_score': coding_score,
            'certifications': certifications,
            'tenth_percentage': tenth_percentage,
            'twelfth_percentage': twelfth_percentage
        }

        # Build feature vector matching 18 model columns in train_model.py
        comm_enc = {'Poor': 0, 'Average': 1, 'Good': 2, 'Excellent': 3}.get(communication_skill, 1)
        intern_enc = 1 if internship_val.lower() == 'yes' else 0

        DEPARTMENTS = [
            'Computer Science and Engineering', 'Information Technology',
            'Electronics and Communication Engineering', 'Electrical and Electronics Engineering',
            'Mechanical Engineering', 'Civil Engineering',
            'Artificial Intelligence and Data Science', 'Other'
        ]
        dept_onehot = [1 if department == d else 0 for d in DEPARTMENTS]

        feature_vector = [
            cgpa, tenth_percentage, twelfth_percentage, aptitude_score, coding_score,
            certifications, projects_completed, backlogs, comm_enc, intern_enc
        ] + dept_onehot

        input_array = np.array([feature_vector])
        scaled_input = scaler.transform(input_array)

        prediction_class = int(model.predict(scaled_input)[0])
        probabilities = model.predict_proba(scaled_input)[0]
        placement_prob = float(probabilities[1])
        prob_percentage = round(placement_prob * 100, 1)

        if prob_percentage >= 75:
            status = 'High Probability'
            color = '#10b981'
        elif prob_percentage >= 50:
            status = 'Moderate Chance'
            color = '#f59e0b'
        else:
            status = 'Needs Improvement'
            color = '#ef4444'

        recommendations = generate_recommendations(input_dict)
        placed_avg = metrics.get('placed_averages', {})

        # Log prediction to SQLite database
        try:
            database.log_prediction(
                student_name=student_name,
                register_number=register_number,
                department=department,
                cgpa=cgpa,
                prediction=prediction_class,
                probability=prob_percentage,
                status=status
            )
        except Exception as log_err:
            print(f"[WARNING] Failed to log prediction to DB: {log_err}")

        return jsonify({
            'success': True,
            'student_name': student_name,
            'register_number': register_number,
            'department': department,
            'prediction': prediction_class,
            'placed_text': 'Likely to be Placed' if prediction_class == 1 else 'Unlikely to be Placed (Action Required)',
            'probability': prob_percentage,
            'status': status,
            'color': color,
            'inputs': input_dict,
            'recommendations': recommendations,
            'placed_averages': placed_avg
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400

@public_bp.route('/api/metrics', methods=['GET'])
def get_metrics():
    """Return stored model metrics and feature importances."""
    load_ml_artifacts()
    return jsonify(metrics)

# ---------------------------------------------------------
# AI Resume Analyzer & Job Recommendation Routes
# ---------------------------------------------------------
ALLOWED_RESUME_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_RESUME_EXTENSIONS

@public_bp.route('/resume-analyzer', methods=['GET', 'POST'])
def resume_analyzer_route():
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

            unique_filename = f"resume_{os.urandom(4).hex()}_{filename}"
            filepath = os.path.join(upload_dir, unique_filename)
            file.save(filepath)

            file_ext = filename.rsplit('.', 1)[1].lower()

            # 1. Raw Text Extraction
            raw_text = resume_analyzer.extract_text_from_file(filepath, file_ext)
            if not raw_text.strip():
                flash('Could not extract readable text from the resume. Please try a text-based PDF or Word document.', 'danger')
                return redirect(request.url)

            # 2. Information Parsing
            parsed_data = resume_analyzer.parse_resume_text(raw_text)

            # 3. AI Scoring
            score_data = resume_analyzer.calculate_ai_resume_score(parsed_data)

            # 4. Skill Gap Analysis
            skill_gap_data = resume_analyzer.analyze_skill_gap(parsed_data['skills'])

            # 5. Job Recommendations
            job_recs = resume_analyzer.recommend_job_roles(parsed_data)

            # 6. Learning Roadmap
            roadmap_data = resume_analyzer.generate_learning_roadmap(skill_gap_data)

            # 7. Calculate Placement Probability using ML Model if present
            prob = 75.0
            if model and scaler:
                try:
                    # Construct feature vector: [cgpa, tenth, twelfth, aptitude, coding, comm_code, intern_code, certs, projects, backlogs]
                    comm_code = 2  # Good
                    intern_code = 1 if len(parsed_data['experience']) > 0 else 0
                    features_arr = np.array([[
                        parsed_data.get('cgpa', 7.5),
                        80.0, 80.0, 75, 75,
                        comm_code, intern_code,
                        len(parsed_data.get('certifications', [])),
                        len(parsed_data.get('projects', [])),
                        0
                    ]])
                    scaled_feats = scaler.transform(features_arr)
                    prob_val = model.predict_proba(scaled_feats)[0][1]
                    prob = float(prob_val * 100)
                except Exception as ml_err:
                    print(f"[WARNING] ML Probability calculation fallback: {ml_err}")

            status_text = "High Chance" if prob >= 70 else ("Moderate" if prob >= 50 else "Needs Improvement")

            # 8. Save Record to Database
            analysis_dict = {
                'register_number': request.form.get('register_number', 'GUEST'),
                'filename': unique_filename,
                'original_filename': filename,
                'file_type': file_ext.upper(),
                'name': parsed_data.get('name', 'Candidate'),
                'email': parsed_data.get('email', 'Not Specified'),
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
            return redirect(url_for('public.view_resume_analysis', analysis_id=analysis_id))

        else:
            flash('Invalid file format! Only PDF (.pdf) and Word (.docx) files are supported.', 'danger')
            return redirect(request.url)

    return render_template('resume_analyzer.html')

@public_bp.route('/resume-analysis/<int:analysis_id>')
def view_resume_analysis(analysis_id):
    analysis = database.get_resume_analysis(analysis_id)
    if not analysis:
        flash('Resume analysis record not found.', 'danger')
        return redirect(url_for('public.resume_analyzer_route'))
    return render_template('resume_dashboard.html', analysis=analysis)

@public_bp.route('/resume-analysis/<int:analysis_id>/download-pdf')
def download_resume_pdf(analysis_id):
    analysis = database.get_resume_analysis(analysis_id)
    if not analysis:
        flash('Resume analysis record not found.', 'danger')
        return redirect(url_for('public.resume_analyzer_route'))

    pdf_dir = os.path.join('static', 'reports')
    os.makedirs(pdf_dir, exist_ok=True)
    pdf_filename = f"Resume_Analysis_Report_{analysis_id}.pdf"
    pdf_path = os.path.join(pdf_dir, pdf_filename)

    resume_analyzer.generate_resume_pdf_report(analysis, pdf_path)
    return send_file(pdf_path, as_attachment=True, download_name=pdf_filename)

