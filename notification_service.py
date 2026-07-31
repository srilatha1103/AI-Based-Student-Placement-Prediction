import os
import smtplib
import threading
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import render_template, current_app
import database

# ---------------------------------------------------------
# SMTP Configuration from Environment
# ---------------------------------------------------------
SMTP_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('MAIL_PORT', 587))
SMTP_USERNAME = os.environ.get('MAIL_USERNAME', '')
SMTP_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'PlacementIQ AI <noreply@placementiq.ai>')
ENABLE_REAL_EMAIL = bool(SMTP_USERNAME and SMTP_PASSWORD)

def _send_email_thread(app, recipient, subject, html_body):
    """Background worker thread to send SMTP email without blocking HTTP responses."""
    with app.app_context():
        if not recipient or '@' not in recipient:
            database.log_email_delivery(recipient or 'Unknown', subject, html_body, 'Failed', 'Invalid recipient email format.')
            return

        if not ENABLE_REAL_EMAIL:
            # Demo Mode: Log email locally in database for simulation
            print(f"[DEMO EMAIL SERVICE] Dispatching to: {recipient} | Subject: {subject}")
            database.log_email_delivery(recipient, subject, html_body, 'Demo Mode', None)
            return

        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = DEFAULT_SENDER
            msg['To'] = recipient

            part = MIMEText(html_body, 'html')
            msg.attach(part)

            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10)
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(DEFAULT_SENDER, [recipient], msg.as_string())
            server.quit()

            database.log_email_delivery(recipient, subject, html_body, 'Sent', None)
            print(f"[EMAIL SUCCESS] Sent to {recipient}")
        except Exception as e:
            err_msg = str(e)
            print(f"[EMAIL ERROR] Failed to send email to {recipient}: {err_msg}")
            database.log_email_delivery(recipient, subject, html_body, 'Failed', err_msg)

def send_async_email(recipient, subject, html_body):
    """Launch non-blocking background thread for email dispatch."""
    app = current_app._get_current_object()
    thread = threading.Thread(target=_send_email_thread, args=(app, recipient, subject, html_body))
    thread.daemon = True
    thread.start()

def send_templated_email(recipient, subject, template_name, context):
    """Render HTML template and send via background thread."""
    try:
        html_body = render_template(template_name, **context)
    except Exception as e:
        print(f"[TEMPLATE ERROR] Could not render {template_name}: {e}")
        html_body = f"<h2>{subject}</h2><p>{context.get('message', '')}</p>"

    send_async_email(recipient, subject, html_body)

# ---------------------------------------------------------
# Modular Notification & Email Handlers
# ---------------------------------------------------------

# 1. Student Notifications
def notify_student_registration(student_reg, email, name):
    title = "Welcome to PlacementIQ AI!"
    msg = f"Hi {name}, your student account ({student_reg}) has been successfully created. Access placement predictions, resume scoring, and campus drives now."
    status = 'Sent' if ENABLE_REAL_EMAIL else 'Demo Mode'
    database.create_notification('student', student_reg, title, msg, 'success', email, status)

    send_templated_email(email, title, 'email/registration_welcome.html', {
        'name': name,
        'user_type': 'Student',
        'reg_number': student_reg,
        'message': msg
    })

def notify_student_prediction(student_reg, email, name, probability, status):
    title = f"Placement Probability Calculated: {probability:.1f}%"
    msg = f"Your latest AI Placement Chance prediction is {probability:.1f}% ({status}). Explore recommended skill gap improvements."
    database.create_notification('student', student_reg, title, msg, 'info', email)

    send_templated_email(email, f"PlacementIQ Prediction Report: {probability:.1f}%", 'email/prediction_report.html', {
        'name': name,
        'probability': probability,
        'status': status,
        'message': msg
    })

def notify_student_resume_analysis(student_reg, email, name, score):
    title = f"Resume Score Analyzed: {score} / 100"
    msg = f"Your uploaded resume scored {score}/100. Review missing keywords, section formatting feedback, and career roadmaps."
    database.create_notification('student', student_reg, title, msg, 'recommendation', email)

    send_templated_email(email, f"AI Resume Analysis Completed: {score}/100", 'email/base_email.html', {
        'title': title,
        'name': name,
        'message': msg,
        'button_text': 'View Resume Dashboard',
        'button_url': '/student/resume-analyzer'
    })

def notify_student_mock_interview(student_reg, email, name, category, score):
    title = f"Mock Interview Score: {score:.1f}% ({category})"
    msg = f"Great effort! You completed your {category} AI mock interview with score {score:.1f}%. Check detailed question feedback."
    database.create_notification('student', student_reg, title, msg, 'success', email)

    send_templated_email(email, f"Mock Interview Results - {category}", 'email/base_email.html', {
        'title': title,
        'name': name,
        'message': msg,
        'button_text': 'View Interview Report',
        'button_url': '/student/mock-interview/dashboard'
    })

def notify_student_interview_invite(student_reg, email, name, job_title, company_name, date_str, time_str, mode, link_or_venue):
    title = f"📅 Interview Invitation: {job_title} at {company_name}"
    msg = f"You have been invited for an interview for {job_title} at {company_name}. Mode: {mode} | Date: {date_str} at {time_str}."
    if link_or_venue:
        msg += f" Details: {link_or_venue}"
    database.create_notification('student', student_reg, title, msg, 'reminder', email)

    send_templated_email(email, title, 'email/interview_invitation.html', {
        'name': name,
        'job_title': job_title,
        'company_name': company_name,
        'date_str': date_str,
        'time_str': time_str,
        'mode': mode,
        'link_or_venue': link_or_venue,
        'message': msg
    })

def notify_student_status_update(student_reg, email, name, job_title, company_name, new_status):
    title = f"Application Update: {job_title} - {new_status}"
    msg = f"Your application status for {job_title} at {company_name} has been updated to '{new_status}'."
    notif_type = 'success' if new_status in ['Shortlisted', 'Selected'] else ('danger' if new_status == 'Rejected' else 'info')
    database.create_notification('student', student_reg, title, msg, notif_type, email)

    send_templated_email(email, title, 'email/application_status.html', {
        'name': name,
        'job_title': job_title,
        'company_name': company_name,
        'status': new_status,
        'message': msg
    })

# 2. Company Notifications
def notify_company_registration(company_id, email, company_name):
    title = "Welcome to PlacementIQ Recruitment Portal!"
    msg = f"Hi {company_name}, your corporate account has been activated. Publish campus job posts and leverage AI candidate matching."
    database.create_notification('company', company_id, title, msg, 'success', email)

    send_templated_email(email, title, 'email/registration_welcome.html', {
        'name': company_name,
        'user_type': 'Recruiter Company',
        'reg_number': f"COMP-{company_id}",
        'message': msg
    })

def notify_company_new_application(company_id, email, company_name, student_name, job_title, match_score):
    title = f"New Applicant: {student_name} applied for {job_title}"
    msg = f"{student_name} submitted an application for {job_title} with AI Match Score {match_score}%."
    database.create_notification('company', company_id, title, msg, 'info', email)

    send_templated_email(email, title, 'email/base_email.html', {
        'title': title,
        'name': company_name,
        'message': msg,
        'button_text': 'Review Candidate',
        'button_url': '/company/candidates'
    })

# 3. Admin Notifications
def notify_admin_system_alert(title, message, notif_type='warning'):
    # Notify system admin
    database.create_notification('admin', 'admin', title, message, notif_type, 'admin@college.edu')
    send_templated_email('admin@college.edu', f"PlacementIQ Admin Alert: {title}", 'email/admin_alert.html', {
        'title': title,
        'message': message,
        'type': notif_type
    })
