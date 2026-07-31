import os
import json
import logging
from flask import Flask, render_template
import database
import train_model
from routes.public import public_bp
from routes.admin import admin_bp
from routes.student import student_bp
from routes.company import company_bp
from routes.notifications import notifications_bp, _get_current_user_context

# Configure Application Error Logging
logging.basicConfig(
    filename='app.log',
    level=logging.ERROR,
    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s'
)

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'placement_iq_super_secure_key_2026')

# Configure Upload Folders
UPLOAD_FOLDER = os.path.join('static', 'uploads', 'profile_photos')
COMPANY_LOGO_FOLDER = os.path.join('static', 'uploads', 'company_logos')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(COMPANY_LOGO_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['COMPANY_LOGO_FOLDER'] = COMPANY_LOGO_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max upload limit

# Custom HTTP Error Handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    app.logger.error(f"Server Error 500: {error}")
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

# Global Template Context Processor for Unread Notifications Count
@app.context_processor
def inject_notifications():
    from flask import session
    user_type, user_id = _get_current_user_context()
    count = 0
    if user_type and user_id:
        count = database.get_unread_notification_count(user_type, user_id)
    return dict(unread_notif_count=count)

# Initialize SQLite Database & Tables
with app.app_context():
    database.init_db()
    model_path = os.path.join('models', 'model.pkl')
    if not os.path.exists(model_path):
        print("[INFO] Initial ML model not found. Training model now...")
        train_model.train_and_export_model()

# Register Blueprints
app.register_blueprint(public_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(student_bp)
app.register_blueprint(company_bp)
app.register_blueprint(notifications_bp)

if __name__ == '__main__':
    print("[INFO] Starting PlacementIQ Flask Application with Admin, Student, Company & Notification Portals...")
    app.run(host='0.0.0.0', port=5000, debug=True)
