from functools import wraps
from flask import session, request, flash, redirect, url_for, current_app
from app import db
from app.models import User, Role, Permission, UserRole, RolePermission, AuditLog, Notification, NotificationType
from datetime import datetime
import json

# ==========================================
# RBAC UTILITIES
# ==========================================

def user_has_permission(user_id, permission_name):
    """
    Check if a user has a specific permission through their assigned roles.
    """
    try:
        # Get user's roles
        user_roles = UserRole.query.filter_by(user_id=user_id).all()
        role_ids = [ur.role_id for ur in user_roles]
        
        if not role_ids:
            return False
            
        # Get permissions for these roles
        # Join RolePermission and Permission tables
        permissions = db.session.query(Permission).join(
            RolePermission, RolePermission.permission_id == Permission.permission_id
        ).filter(
            RolePermission.role_id.in_(role_ids),
            Permission.permission_name == permission_name
        ).first()
        
        return permissions is not None
        
    except Exception as e:
        current_app.logger.error(f"Error checking permission {permission_name} for user {user_id}: {str(e)}")
        return False

def require_permission(permission_name):
    """
    Decorator to restrict access to routes based on permissions.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please login to access this page.', 'error')
                return redirect(url_for('main.login'))
            
            user_id = session['user_id']
            
            # Check if user is admin (bypass check) - optional optimization
            # admin_role = Role.query.filter_by(role_name='Admin').first()
            # if admin_role:
            #     is_admin = UserRole.query.filter_by(user_id=user_id, role_id=admin_role.role_id).first()
            #     if is_admin:
            #         return f(*args, **kwargs)
            
            if not user_has_permission(user_id, permission_name):
                log_audit(
                    user_id=user_id,
                    action_type='access_denied',
                    resource_type='route',
                    action_description=f"Access denied for permission: {permission_name}",
                    status='failure',
                    severity='medium'
                )
                flash('You do not have permission to access this resource.', 'error')
                return redirect(url_for('main.dashboard'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# ==========================================
# AUDIT LOGGING UTILITIES
# ==========================================

def log_audit(user_id, action_type, action_description, resource_type=None, resource_id=None, 
              status='success', severity='medium', error_message=None, old_value=None, new_value=None):
    """
    Create an audit log entry for security-relevant actions.
    """
    try:
        # Get request details if available (might be called outside request context)
        ip_address = request.remote_addr if request else None
        user_agent = str(request.user_agent) if request else None
        request_method = request.method if request else None
        request_url = request.url if request else None
        
        # Get username if user_id is provided
        username = None
        if user_id:
            user = User.query.get(user_id)
            if user:
                username = user.username
        
        audit_entry = AuditLog(
            user_id=user_id,
            username=username,
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            action_description=action_description,
            ip_address=ip_address,
            user_agent=user_agent,
            request_method=request_method,
            request_url=request_url,
            status=status,
            error_message=error_message,
            old_value=old_value,
            new_value=new_value,
            severity=severity,
            timestamp=datetime.utcnow()
        )
        
        db.session.add(audit_entry)
        db.session.commit()
        
    except Exception as e:
        current_app.logger.error(f"Failed to create audit log: {str(e)}")
        db.session.rollback()

# ==========================================
# NOTIFICATION UTILITIES
# ==========================================

def create_notification(user_id, type_name, title, message, priority='medium', action_url=None, metadata=None):
    """
    Create a new notification for a user.
    """
    try:
        # Find notification type
        notif_type = NotificationType.query.filter_by(type_name=type_name).first()
        
        if not notif_type:
            # Create default type if not exists (fallback)
            notif_type = NotificationType(type_name=type_name, description="Auto-generated type")
            db.session.add(notif_type)
            db.session.commit()
            
        notification = Notification(
            user_id=user_id,
            type_id=notif_type.type_id,
            title=title,
            message=message,
            priority=priority,
            action_url=action_url,
            meta_data=metadata,  # Correct attribute name
            status='pending',
            # status_change='created'  # Removed: Not in DB
            created_date=datetime.utcnow()
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return notification
        
    except Exception as e:
        current_app.logger.error(f"Failed to create notification: {str(e)}")
        db.session.rollback()
        return None

def mark_notification_read(notification_id, user_id):
    """
    Mark a notification as read.
    """
    try:
        notification = Notification.query.filter_by(notification_id=notification_id, user_id=user_id).first()
        if notification:
            notification.status = 'read'
            notification.read_at = datetime.utcnow()
            db.session.commit()
            return True
        return False
    except Exception as e:
        db.session.rollback()
        return False
