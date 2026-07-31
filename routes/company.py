import os
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from werkzeug.utils import secure_filename
import database
import notification_service

company_bp = Blueprint('company', __name__, url_prefix='/company')

def company_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('company_logged_in') or not session.get('company_id'):
            flash('Please log in to access your Company Recruitment Portal.', 'warning')
            return redirect(url_for('company.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------------------------------------
# Authentication Routes
# ---------------------------------------------------------
@company_bp.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('company_logged_in'):
        return redirect(url_for('company.dashboard'))

    if request.method == 'POST':
        data = {
            'company_name': request.form.get('company_name', '').strip(),
            'email': request.form.get('email', '').strip().lower(),
            'password': request.form.get('password', '').strip(),
            'contact_person': request.form.get('contact_person', '').strip(),
            'phone': request.form.get('phone', '').strip(),
            'industry': request.form.get('industry', 'Information Technology').strip(),
            'location': request.form.get('location', '').strip(),
            'website': request.form.get('website', '').strip(),
            'company_size': request.form.get('company_size', '100-500 Employees').strip(),
            'description': request.form.get('description', '').strip()
        }

        if not data['company_name'] or not data['email'] or not data['password']:
            flash('Company Name, Email, and Password are required!', 'danger')
            return render_template('company/register.html', data=data)

        if len(data['password']) < 6:
            flash('Password must be at least 6 characters long.', 'warning')
            return render_template('company/register.html', data=data)

        # Handle optional logo upload during registration
        logo_filename = 'default_company.png'
        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                ext = os.path.splitext(filename)[1]
                logo_filename = f"logo_{data['email'].replace('@', '_').replace('.', '_')}{ext}"
                logo_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'company_logos')
                os.makedirs(logo_dir, exist_ok=True)
                file.save(os.path.join(logo_dir, logo_filename))

        data['logo'] = logo_filename

        success, res = database.register_company(data)
        if success:
            notification_service.notify_company_registration(res, data['email'], data['company_name'])
            notification_service.notify_admin_system_alert(
                'New Recruiter Registration',
                f"Company {data['company_name']} ({data['industry']}) has registered.",
                'info'
            )
            flash('Company registered successfully! Welcome email sent.', 'success')
            return redirect(url_for('company.login'))
        else:
            flash(f"Registration failed: {res}", 'danger')

    return render_template('company/register.html')

@company_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('company_logged_in'):
        return redirect(url_for('company.dashboard'))

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        company = database.verify_company(email, password)
        if company:
            session['company_logged_in'] = True
            session['company_id'] = company['id']
            session['company_name'] = company['company_name']
            session['company_email'] = company['email']
            session['company_logo'] = company.get('logo', 'default_company.png')
            flash(f"Welcome back to recruitment portal, {company['company_name']}!", 'success')
            next_url = request.args.get('next')
            return redirect(next_url or url_for('company.dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('company/login.html')

@company_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out of Company Portal.', 'info')
    return redirect(url_for('company.login'))

@company_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        company = database.get_company_by_email(email)
        if company:
            flash(f"A password reset link/instructions have been sent to {email} (Demo: Enter new password directly).", 'info')
            return redirect(url_for('company.reset_password', email=email))
        else:
            flash('No company account found with that email address.', 'warning')

    return render_template('company/forgot_password.html')

@company_bp.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    email = request.args.get('email', '')
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        new_password = request.form.get('new_password', '').strip()
        company = database.get_company_by_email(email)
        if company:
            if len(new_password) < 6:
                flash('Password must be at least 6 characters.', 'warning')
            else:
                success, msg = database.update_company_password(company['id'], new_password)
                if success:
                    flash('Password reset successfully! Please log in.', 'success')
                    return redirect(url_for('company.login'))
                else:
                    flash(f"Reset failed: {msg}", 'danger')
        else:
            flash('Invalid email address.', 'danger')

    return render_template('company/reset_password.html', email=email)

# ---------------------------------------------------------
# Dashboard & Profile
# ---------------------------------------------------------
@company_bp.route('/')
@company_bp.route('/dashboard')
@company_login_required
def dashboard():
    company_id = session['company_id']
    company = database.get_company_by_id(company_id)
    stats = database.get_company_dashboard_stats(company_id)
    jobs = database.get_company_jobs(company_id)
    recent_applicants = database.get_job_applications(company_id=company_id)[:8]
    upcoming_interviews = database.get_interviews(company_id=company_id, status='Scheduled')[:5]

    return render_template(
        'company/dashboard.html',
        company=company,
        stats=stats,
        jobs=jobs,
        recent_applicants=recent_applicants,
        upcoming_interviews=upcoming_interviews
    )

@company_bp.route('/profile', methods=['GET', 'POST'])
@company_login_required
def profile():
    company_id = session['company_id']

    if request.method == 'POST':
        data = {
            'company_name': request.form.get('company_name', '').strip(),
            'contact_person': request.form.get('contact_person', '').strip(),
            'phone': request.form.get('phone', '').strip(),
            'industry': request.form.get('industry', '').strip(),
            'location': request.form.get('location', '').strip(),
            'website': request.form.get('website', '').strip(),
            'company_size': request.form.get('company_size', '').strip(),
            'description': request.form.get('description', '').strip(),
            'logo': None
        }

        if 'logo' in request.files:
            file = request.files['logo']
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                ext = os.path.splitext(filename)[1]
                logo_filename = f"logo_comp_{company_id}{ext}"
                logo_dir = os.path.join(current_app.root_path, 'static', 'uploads', 'company_logos')
                os.makedirs(logo_dir, exist_ok=True)
                file.save(os.path.join(logo_dir, logo_filename))
                data['logo'] = logo_filename
                session['company_logo'] = logo_filename

        success, msg = database.update_company_profile(company_id, data)
        if success:
            session['company_name'] = data['company_name']
            flash('Company profile updated successfully!', 'success')
            return redirect(url_for('company.profile'))
        else:
            flash(f"Update failed: {msg}", 'danger')

    company = database.get_company_by_id(company_id)
    return render_template('company/profile.html', company=company)

# ---------------------------------------------------------
# Job Management Routes
# ---------------------------------------------------------
@company_bp.route('/jobs')
@company_login_required
def jobs_list():
    company_id = session['company_id']
    status_filter = request.args.get('status')
    jobs = database.get_company_jobs(company_id, status=status_filter)
    return render_template('company/jobs/list.html', jobs=jobs, status_filter=status_filter)

@company_bp.route('/jobs/create', methods=['GET', 'POST'])
@company_login_required
def job_create():
    if request.method == 'POST':
        data = {
            'title': request.form.get('title', '').strip(),
            'description': request.form.get('description', '').strip(),
            'required_skills': request.form.get('required_skills', '').strip(),
            'min_cgpa': request.form.get('min_cgpa', 6.0),
            'required_certifications': request.form.get('required_certifications', 0),
            'internship_required': request.form.get('internship_required', 'No'),
            'experience_level': request.form.get('experience_level', 'Freshers'),
            'salary_package': request.form.get('salary_package', '').strip(),
            'location': request.form.get('location', '').strip(),
            'deadline': request.form.get('deadline', ''),
            'status': request.form.get('status', 'Active')
        }

        if not data['title'] or not data['description'] or not data['required_skills'] or not data['salary_package'] or not data['deadline']:
            flash('Please fill in all required job details.', 'danger')
            return render_template('company/jobs/create.html', data=data)

        success, res = database.create_job(session['company_id'], data)
        if success:
            flash('Job posting published successfully! Eligible students have been notified.', 'success')
            return redirect(url_for('company.jobs_list'))
        else:
            flash(f"Error publishing job: {res}", 'danger')

    return render_template('company/jobs/create.html')

@company_bp.route('/jobs/<int:job_id>/edit', methods=['GET', 'POST'])
@company_login_required
def job_edit(job_id):
    company_id = session['company_id']
    job = database.get_job_by_id(job_id)

    if not job or job['company_id'] != company_id:
        flash('Job not found or access denied.', 'danger')
        return redirect(url_for('company.jobs_list'))

    if request.method == 'POST':
        data = {
            'title': request.form.get('title', '').strip(),
            'description': request.form.get('description', '').strip(),
            'required_skills': request.form.get('required_skills', '').strip(),
            'min_cgpa': request.form.get('min_cgpa', 6.0),
            'required_certifications': request.form.get('required_certifications', 0),
            'internship_required': request.form.get('internship_required', 'No'),
            'experience_level': request.form.get('experience_level', 'Freshers'),
            'salary_package': request.form.get('salary_package', '').strip(),
            'location': request.form.get('location', '').strip(),
            'deadline': request.form.get('deadline', ''),
            'status': request.form.get('status', 'Active')
        }

        success, msg = database.update_job(job_id, company_id, data)
        if success:
            flash('Job details updated successfully.', 'success')
            return redirect(url_for('company.jobs_list'))
        else:
            flash(f"Error updating job: {msg}", 'danger')

    return render_template('company/jobs/edit.html', job=job)

@company_bp.route('/jobs/<int:job_id>/delete', methods=['POST'])
@company_login_required
def job_delete(job_id):
    company_id = session['company_id']
    success, msg = database.delete_job(job_id, company_id)
    if success:
        flash('Job posting deleted successfully.', 'info')
    else:
        flash(f"Error deleting job: {msg}", 'danger')
    return redirect(url_for('company.jobs_list'))

@company_bp.route('/jobs/<int:job_id>')
@company_login_required
def job_detail(job_id):
    company_id = session['company_id']
    job = database.get_job_by_id(job_id)
    if not job or job['company_id'] != company_id:
        flash('Job not found.', 'danger')
        return redirect(url_for('company.jobs_list'))

    applications = database.get_job_applications(company_id=company_id, job_id=job_id)
    return render_template('company/jobs/detail.html', job=job, applications=applications)

# ---------------------------------------------------------
# AI Candidate Matching Hub
# ---------------------------------------------------------
@company_bp.route('/jobs/<int:job_id>/candidates')
@company_login_required
def job_candidate_match(job_id):
    company_id = session['company_id']
    job = database.get_job_by_id(job_id)
    if not job or job['company_id'] != company_id:
        flash('Job not found or access denied.', 'danger')
        return redirect(url_for('company.jobs_list'))

    candidates = database.get_job_candidate_matches(job_id, company_id)
    return render_template('company/candidates/match.html', job=job, candidates=candidates)

# ---------------------------------------------------------
# Candidate Management Routes
# ---------------------------------------------------------
@company_bp.route('/candidates')
@company_login_required
def candidate_list():
    company_id = session['company_id']
    status_filter = request.args.get('status', 'All')
    job_filter = request.args.get('job_id')
    job_id = int(job_filter) if job_filter and job_filter.isdigit() else None

    applications = database.get_job_applications(company_id=company_id, job_id=job_id, status=status_filter)
    jobs = database.get_company_jobs(company_id)

    return render_template(
        'company/candidates/list.html',
        applications=applications,
        jobs=jobs,
        status_filter=status_filter,
        job_filter=job_filter
    )

@company_bp.route('/candidate/<int:app_id>/status', methods=['POST'])
@company_login_required
def candidate_status_update(app_id):
    company_id = session['company_id']
    app = database.get_application_by_id(app_id)
    if not app or app['company_id'] != company_id:
        return jsonify({'success': False, 'message': 'Unauthorized or application not found.'}), 403

    status = request.form.get('status', '').strip()
    if not status:
        return jsonify({'success': False, 'message': 'Invalid status.'}), 400

    success, msg = database.update_application_status(app_id, status)
    return jsonify({'success': success, 'message': msg})

@company_bp.route('/candidate/<int:app_id>/report')
@company_login_required
def candidate_ai_report(app_id):
    company_id = session['company_id']
    app = database.get_application_by_id(app_id)
    if not app or app['company_id'] != company_id:
        return jsonify({'success': False, 'message': 'Unauthorized access.'}), 403

    # Generate full candidate summary payload
    payload = {
        'success': True,
        'candidate': {
            'student_name': app['student_name'],
            'register_number': app['student_reg'],
            'department': app['department'],
            'cgpa': app['cgpa'],
            'email': app['student_email'],
            'skills_list': app['skills_list'],
            'coding_score': app['coding_score'],
            'aptitude_score': app['aptitude_score'],
            'communication_skill': app['communication_skill'],
            'internship': app['internship'],
            'internship_details': app['internship_details'],
            'certifications_count': app['certifications_count'],
            'certifications_details': app['certifications_details'],
            'projects_count': app['projects_count'],
            'project_details': app['project_details'],
            'tenth_percentage': app['tenth_percentage'],
            'twelfth_percentage': app['twelfth_percentage'],
            'backlogs': app['backlogs']
        },
        'application': {
            'id': app['id'],
            'job_title': app['job_title'],
            'match_score': app['match_score'],
            'matching_skills': app['matching_skills'],
            'missing_skills': app['missing_skills'],
            'ai_recommendation': app['ai_recommendation'],
            'status': app['status'],
            'applied_at': app['applied_at']
        }
    }
    return jsonify(payload)

# ---------------------------------------------------------
# Interview Management Routes
# ---------------------------------------------------------
@company_bp.route('/interviews')
@company_login_required
def interviews_list():
    company_id = session['company_id']
    status_filter = request.args.get('status', 'All')
    interviews = database.get_interviews(company_id=company_id, status=status_filter)
    applications = database.get_job_applications(company_id=company_id, status='Shortlisted')

    return render_template(
        'company/interviews/list.html',
        interviews=interviews,
        applications=applications,
        status_filter=status_filter
    )

@company_bp.route('/interviews/schedule', methods=['POST'])
@company_login_required
def interview_schedule():
    company_id = session['company_id']
    data = {
        'application_id': request.form.get('application_id'),
        'interview_type': request.form.get('interview_type', 'Online'),
        'interview_date': request.form.get('interview_date'),
        'interview_time': request.form.get('interview_time'),
        'location_or_link': request.form.get('location_or_link', '').strip(),
        'notes': request.form.get('notes', '').strip()
    }

    if not data['application_id'] or not data['interview_date'] or not data['interview_time']:
        flash('Please provide candidate application, interview date, and time.', 'warning')
        return redirect(url_for('company.interviews_list'))

    app = database.get_application_by_id(data['application_id'])
    if not app or app['company_id'] != company_id:
        flash('Unauthorized application request.', 'danger')
        return redirect(url_for('company.interviews_list'))

    success, res = database.schedule_interview(data)
    if success:
        notification_service.notify_student_interview_invite(
            app['student_reg'],
            app['student_email'],
            app['student_name'],
            app['job_title'],
            app['company_name'],
            data['interview_date'],
            data['interview_time'],
            data['interview_type'],
            data['location_or_link']
        )
        flash(f"Interview invitation scheduled and email dispatched to {app['student_name']}!", 'success')
    else:
        flash(f"Failed to schedule interview: {res}", 'danger')

    return redirect(url_for('company.interviews_list'))

@company_bp.route('/interviews/<int:interview_id>/status', methods=['POST'])
@company_login_required
def interview_status_update(interview_id):
    company_id = session['company_id']
    status = request.form.get('status', '').strip()
    if not status:
        return jsonify({'success': False, 'message': 'Invalid status.'}), 400

    success, msg = database.update_interview_status(interview_id, company_id, status)
    return jsonify({'success': success, 'message': msg})

# ---------------------------------------------------------
# Recruitment Analytics Dashboard
# ---------------------------------------------------------
@company_bp.route('/analytics')
@company_login_required
def analytics():
    company_id = session['company_id']
    stats = database.get_company_dashboard_stats(company_id)
    return render_template('company/analytics.html', stats=stats)

@company_bp.route('/api/analytics-data')
@company_login_required
def analytics_api():
    company_id = session['company_id']
    data = database.get_company_analytics_data(company_id)
    return jsonify(data)
