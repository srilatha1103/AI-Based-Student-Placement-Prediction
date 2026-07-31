from flask import Blueprint, render_template, request, jsonify, session
import database

notifications_bp = Blueprint('notifications', __name__, url_prefix='/notifications')

def _get_current_user_context():
    """Determine logged-in user type and ID from session."""
    if session.get('student_logged_in') and session.get('student_reg'):
        return 'student', session.get('student_reg')
    elif session.get('company_logged_in') and session.get('company_id'):
        return 'company', str(session.get('company_id'))
    elif session.get('admin_logged_in'):
        return 'admin', session.get('admin_user', 'admin')
    return None, None

@notifications_bp.route('/hub')
def hub():
    user_type, user_id = _get_current_user_context()
    if not user_type:
        user_type = 'student'
        user_id = 'REG20261001' # Default demo context if guest

    unread_only = request.args.get('unread') == 'true'
    is_read = False if unread_only else None

    notifications = database.get_user_notifications(user_type, user_id, is_read=is_read)
    unread_count = database.get_unread_notification_count(user_type, user_id)
    analytics = database.get_notification_analytics()

    return render_template(
        'notifications/hub.html',
        notifications=notifications,
        unread_count=unread_count,
        user_type=user_type,
        user_id=user_id,
        analytics=analytics,
        unread_only=unread_only
    )

@notifications_bp.route('/api/unread-count')
def unread_count_api():
    user_type, user_id = _get_current_user_context()
    if not user_type:
        return jsonify({'unread_count': 0})

    count = database.get_unread_notification_count(user_type, user_id)
    return jsonify({'unread_count': count})

@notifications_bp.route('/api/<int:notif_id>/read', methods=['POST'])
def mark_read_api(notif_id):
    user_type, user_id = _get_current_user_context()
    if not user_type:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    database.mark_notification_as_read(notif_id, user_type, user_id)
    return jsonify({'success': True})

@notifications_bp.route('/api/read-all', methods=['POST'])
def mark_all_read_api():
    user_type, user_id = _get_current_user_context()
    if not user_type:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    database.mark_all_notifications_read(user_type, user_id)
    return jsonify({'success': True})

@notifications_bp.route('/api/<int:notif_id>/delete', methods=['POST'])
def delete_notif_api(notif_id):
    user_type, user_id = _get_current_user_context()
    if not user_type:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403

    database.delete_notification(notif_id, user_type, user_id)
    return jsonify({'success': True})

@notifications_bp.route('/api/analytics')
def analytics_api():
    data = database.get_notification_analytics()
    return jsonify(data)
