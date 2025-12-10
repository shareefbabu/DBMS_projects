"""
Authentication and Authorization Decorators for RBAC
Provides role-based and permission-based access control
"""
from functools import wraps
from flask import session, redirect, url_for, flash, abort, request
from app.models import User

def login_required(f):
    """Decorator to require user to be logged in"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('main.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function

def require_role(*allowed_roles):
    """
    Decorator to restrict access based on user role
    Usage: @require_role('GLOBAL_ADMIN', 'ORG_ADMIN')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('main.login', next=request.url))
            
            user = User.query.get(session['user_id'])
            if not user or not user.role:
                flash('Access denied. No role assigned.', 'danger')
                abort(403)
            
            if user.role.role_name not in allowed_roles:
                flash('You do not have permission to access this page.', 'danger')
                abort(403)
            
            # Store user in kwargs for easy access in route
            kwargs['current_user'] = user
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_permission(perm_code):
    """
    Decorator to restrict access based on specific permission
    Usage: @require_permission('manage_campaigns')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in to access this page.', 'warning')
                return redirect(url_for('main.login', next=request.url))
            
            user = User.query.get(session['user_id'])
            if not user or not user.has_permission(perm_code):
                flash('You do not have the required permission to access this page.', 'danger')
                abort(403)
            
            kwargs['current_user'] = user
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    """Helper function to get current logged-in user"""
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None
