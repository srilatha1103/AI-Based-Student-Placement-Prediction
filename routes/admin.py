import os
import io
import csv
import json
from functools import wraps
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, Response
import pandas as pd
import database
import train_model

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('admin_logged_in'):
            flash('Please log in to access the Admin Dashboard.', 'warning')
            return redirect(url_for('admin.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# ---------------------------------------------------------
# Authentication Routes
# ---------------------------------------------------------
@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))

    if request.method == 'POST':
        username_or_email = request.form.get('username', '').strip() or request.form.get('email', '').strip() or request.form.get('email_or_username', '').strip()
        password = request.form.get('password', '').strip()

        admin = database.verify_admin(username_or_email, password)
        if admin:
            session['admin_logged_in'] = True
            session['admin_user'] = admin['username']
            session['admin_email'] = admin.get('email', 'admin@gmail.com')
            session['admin_name'] = admin.get('name', 'System Administrator')
            flash(f"Welcome back, {session['admin_name']}!", 'success')
            next_url = request.args.get('next')
            return redirect(next_url or url_for('admin.dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'danger')

    return render_template('admin/login.html')


@admin_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('admin.login'))

# ---------------------------------------------------------
# Dashboard Home
# ---------------------------------------------------------
@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    stats = database.get_dashboard_stats()
    recent_predictions = database.get_predictions(limit=5) if hasattr(database, 'get_predictions') else []
    # Fetch latest 5 predictions safely
    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM prediction_history ORDER BY id DESC LIMIT 5")
    recent_predictions = [dict(row) for row in cursor.fetchall()]
    conn.close()

    metrics = {}
    metrics_path = os.path.join('models', 'metrics.json')
    if os.path.exists(metrics_path):
        try:
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)
        except Exception:
            pass

    return render_template('admin/dashboard.html', stats=stats, recent_predictions=recent_predictions, metrics=metrics)

# ---------------------------------------------------------
# Student Management (CRUD)
# ---------------------------------------------------------
@admin_bp.route('/students')
@login_required
def students():
    search = request.args.get('search', '').strip()
    department = request.args.get('department', '').strip()
    placement_status = request.args.get('placement_status', '').strip()

    student_list = database.get_students(
        search_query=search,
        department_filter=department,
        status_filter=placement_status
    )

    departments_list = train_model.DEPARTMENTS

    return render_template(
        'admin/students.html',
        students=student_list,
        search=search,
        selected_dept=department,
        selected_status=placement_status,
        departments=departments_list
    )

@admin_bp.route('/students/add', methods=['POST'])
@login_required
def add_student_route():
    try:
        data = {
            'student_name': request.form.get('student_name', '').strip(),
            'register_number': request.form.get('register_number', '').strip(),
            'department': request.form.get('department', '').strip(),
            'cgpa': request.form.get('cgpa', 7.0),
            'tenth_percentage': request.form.get('tenth_percentage', 70.0),
            'twelfth_percentage': request.form.get('twelfth_percentage', 70.0),
            'aptitude_score': request.form.get('aptitude_score', 65),
            'coding_score': request.form.get('coding_score', 65),
            'communication_skill': request.form.get('communication_skill', 'Average'),
            'internship': request.form.get('internship', 'No'),
            'certifications': request.form.get('certifications', 0),
            'projects_completed': request.form.get('projects_completed', 1),
            'backlogs': request.form.get('backlogs', 0),
            'placement_status': request.form.get('placement_status', 0)
        }

        if not data['student_name'] or not data['register_number']:
            flash('Student Name and Register Number are required!', 'danger')
            return redirect(url_for('admin.students'))

        student_id, err = database.add_student(data)
        if err:
            flash(f"Error adding student: {err}", 'danger')
        else:
            flash(f"Student '{data['student_name']}' added successfully!", 'success')
    except Exception as e:
        flash(f"Unexpected error: {str(e)}", 'danger')

    return redirect(url_for('admin.students'))

@admin_bp.route('/students/edit/<int:student_id>', methods=['POST'])
@login_required
def edit_student_route(student_id):
    try:
        data = {
            'student_name': request.form.get('student_name', '').strip(),
            'register_number': request.form.get('register_number', '').strip(),
            'department': request.form.get('department', '').strip(),
            'cgpa': request.form.get('cgpa', 7.0),
            'tenth_percentage': request.form.get('tenth_percentage', 70.0),
            'twelfth_percentage': request.form.get('twelfth_percentage', 70.0),
            'aptitude_score': request.form.get('aptitude_score', 65),
            'coding_score': request.form.get('coding_score', 65),
            'communication_skill': request.form.get('communication_skill', 'Average'),
            'internship': request.form.get('internship', 'No'),
            'certifications': request.form.get('certifications', 0),
            'projects_completed': request.form.get('projects_completed', 1),
            'backlogs': request.form.get('backlogs', 0),
            'placement_status': request.form.get('placement_status', 0)
        }

        success, err = database.update_student(student_id, data)
        if success:
            flash(f"Student details updated successfully!", 'success')
        else:
            flash(f"Error updating student: {err}", 'danger')
    except Exception as e:
        flash(f"Unexpected error: {str(e)}", 'danger')

    return redirect(url_for('admin.students'))

@admin_bp.route('/students/delete/<int:student_id>', methods=['POST'])
@login_required
def delete_student_route(student_id):
    try:
        database.delete_student(student_id)
        flash('Student record deleted successfully.', 'success')
    except Exception as e:
        flash(f"Failed to delete student: {str(e)}", 'danger')

    return redirect(url_for('admin.students'))

# ---------------------------------------------------------
# Dataset Management
# ---------------------------------------------------------
@admin_bp.route('/dataset')
@login_required
def dataset():
    history = database.get_dataset_history()

    csv_path = os.path.join('dataset', 'placement.csv')
    preview_data = []
    headers = []
    file_exists = os.path.exists(csv_path)
    total_rows = 0

    if file_exists:
        try:
            df = pd.read_csv(csv_path)
            total_rows = len(df)
            headers = df.columns.tolist()
            preview_data = df.head(15).to_dict(orient='records')
        except Exception as e:
            flash(f"Error reading dataset preview: {e}", 'warning')

    return render_template(
        'admin/dataset.html',
        history=history,
        file_exists=file_exists,
        total_rows=total_rows,
        headers=headers,
        preview_data=preview_data
    )

@admin_bp.route('/dataset/upload', methods=['POST'])
@login_required
def upload_dataset():
    if 'dataset_file' not in request.files:
        flash('No file part in request!', 'danger')
        return redirect(url_for('admin.dataset'))

    file = request.files['dataset_file']
    if file.filename == '':
        flash('No file selected!', 'danger')
        return redirect(url_for('admin.dataset'))

    if not file.filename.endswith('.csv'):
        flash('Invalid file format. Please upload a valid CSV dataset file!', 'danger')
        return redirect(url_for('admin.dataset'))

    try:
        # Read and validate CSV contents
        df = pd.read_csv(file)

        # Check required columns
        required_cols = ['student_name', 'register_number', 'department', 'cgpa']
        missing_cols = [c for c in required_cols if c not in df.columns]

        if missing_cols:
            flash(f"CSV format validation failed! Missing required columns: {', '.join(missing_cols)}", 'danger')
            return redirect(url_for('admin.dataset'))

        # Save to dataset/placement.csv
        csv_path = os.path.join('dataset', 'placement.csv')
        df.to_csv(csv_path, index=False)

        # Sync with SQLite database students table
        synced_count = database.sync_students_from_dataframe(df)

        # Log dataset upload history
        database.log_dataset_upload('placement.csv', file.filename, len(df), 'Active')

        flash(f"Dataset '{file.filename}' uploaded & validated successfully! {synced_count} student records synced.", 'success')

    except Exception as e:
        flash(f"Failed to process CSV file: {str(e)}", 'danger')

    return redirect(url_for('admin.dataset'))

@admin_bp.route('/dataset/delete/<int:history_id>', methods=['POST'])
@login_required
def delete_dataset(history_id):
    try:
        database.delete_dataset_record(history_id)
        flash('Dataset history record updated to deleted.', 'success')
    except Exception as e:
        flash(f"Error: {str(e)}", 'danger')
    return redirect(url_for('admin.dataset'))

# ---------------------------------------------------------
# AI Model Management
# ---------------------------------------------------------
@admin_bp.route('/model')
@login_required
def model_management():
    metrics = {}
    metrics_path = os.path.join('models', 'metrics.json')
    if os.path.exists(metrics_path):
        try:
            with open(metrics_path, 'r') as f:
                metrics = json.load(f)
        except Exception:
            pass

    latest_metadata = database.get_latest_model_metadata()

    return render_template('admin/model.html', metrics=metrics, metadata=latest_metadata)

@admin_bp.route('/model/train', methods=['POST'])
@login_required
def train_model_action():
    try:
        metrics_data = train_model.train_and_export_model()
        accuracy_pct = round(metrics_data['accuracy'] * 100, 2)
        flash(f"Random Forest ML Model retrained successfully! New Accuracy: {accuracy_pct}%", 'success')
    except Exception as e:
        flash(f"Model training failed: {str(e)}", 'danger')

    return redirect(url_for('admin.model_management'))

# ---------------------------------------------------------
# Prediction History & CSV Export
# ---------------------------------------------------------
@admin_bp.route('/predictions')
@login_required
def predictions():
    search = request.args.get('search', '').strip()
    department = request.args.get('department', '').strip()
    prediction = request.args.get('prediction', '').strip()
    sort_by = request.args.get('sort_by', 'id_desc').strip()

    predictions_list = database.get_predictions(
        search_query=search,
        department_filter=department,
        prediction_filter=prediction,
        sort_by=sort_by
    )

    departments_list = train_model.DEPARTMENTS

    return render_template(
        'admin/predictions.html',
        predictions=predictions_list,
        search=search,
        selected_dept=department,
        selected_pred=prediction,
        selected_sort=sort_by,
        departments=departments_list
    )

@admin_bp.route('/predictions/export')
@login_required
def export_predictions():
    try:
        predictions_list = database.get_predictions()
        output = io.StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(['ID', 'Student Name', 'Register Number', 'Department', 'CGPA', 'Prediction', 'Probability (%)', 'Status', 'Date & Time'])

        for p in predictions_list:
            pred_text = 'Likely to be Placed' if p['prediction'] == 1 else 'Not Likely to be Placed'
            writer.writerow([
                p['id'],
                p['student_name'],
                p['register_number'],
                p['department'],
                p['cgpa'],
                pred_text,
                p['probability'],
                p['status'],
                p['created_at']
            ])

        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-disposition": "attachment; filename=placement_predictions_history.csv"}
        )
    except Exception as e:
        flash(f"Export failed: {str(e)}", 'danger')
        return redirect(url_for('admin.predictions'))

# ---------------------------------------------------------
# Analytics Dashboard
# ---------------------------------------------------------
@admin_bp.route('/analytics')
@login_required
def analytics():
    analytics_data = database.get_analytics_data()
    return render_template('admin/analytics.html', data=analytics_data)

# ---------------------------------------------------------
# Admin Settings
# ---------------------------------------------------------
@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    if request.method == 'POST':
        current_pw = request.form.get('current_password', '').strip()
        new_pw = request.form.get('new_password', '').strip()
        confirm_pw = request.form.get('confirm_password', '').strip()

        username = session.get('admin_user', 'admin')
        admin = database.verify_admin(username, current_pw)

        if not admin:
            flash('Current password is incorrect!', 'danger')
        elif new_pw != confirm_pw:
            flash('New passwords do not match!', 'danger')
        elif len(new_pw) < 6:
            flash('New password must be at least 6 characters long!', 'warning')
        else:
            database.update_admin_password(username, new_pw)
            flash('Admin password updated successfully!', 'success')

    return render_template('admin/settings.html')

# ---------------------------------------------------------
# Admin Companies Overview
# ---------------------------------------------------------
@admin_bp.route('/companies')
@login_required
def companies():
    company_list = database.get_all_companies()
    return render_template('admin/companies.html', companies=company_list)

