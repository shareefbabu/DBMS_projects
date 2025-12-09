"""
Admin Routes Blueprint
Handles global admin and organization admin functionalities
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash, make_response
from app.auth_decorators import require_role, require_permission, login_required
from app.models import User, Role, Permission, UserRole, Organization, Department, Team, LearningProgress, UserResponse, db, SuspiciousReport, Scenario
from sqlalchemy import func
import io
import csv
from datetime import datetime

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
@require_role('GLOBAL_ADMIN')
def dashboard(current_user):
    """Global Admin Dashboard"""
    # Get statistics
    total_users = User.query.count()
    total_roles = Role.query.count()
    
    # Get role distribution
    role_stats = db.session.query(
        Role.role_name,
        func.count(UserRole.user_id).label('count')
    ).join(UserRole).group_by(Role.role_name).all()
    
    # Recent users
    recent_users = User.query.order_by(User.created_date.desc()).limit(10).all()
    
    # Achievement Distribution
    from app.models import AchievementDefinition, Achievement
    achievement_stats = db.session.query(
        AchievementDefinition.name,
        func.count(Achievement.achievement_id)
    ).join(Achievement, AchievementDefinition.definition_id == Achievement.definition_id)\
     .filter(Achievement.status == 'Earned')\
     .group_by(AchievementDefinition.name)\
     .order_by(func.count(Achievement.achievement_id).desc())\
     .limit(10).all()

    return render_template('admin/dashboard.html',
                         current_user=current_user,
                         total_users=total_users,
                         total_roles=total_roles,
                         role_stats=role_stats,
                         achievement_stats=achievement_stats,
                         recent_users=recent_users)

@admin_bp.route('/users')
@require_role('GLOBAL_ADMIN', 'ORG_ADMIN')
def manage_users(current_user):
    """User Management Page"""
    # Get all users with their roles
    users = User.query.all()
    roles = Role.query.all()
    organizations = Organization.query.order_by(Organization.name).all()
    
    # If org admin, filter by organization
    if current_user.is_org_admin():
        users = [u for u in users if u.org_id == current_user.org_id]
        # Org admins can't assign organizations, so list might be irrelevant or restricted
        organizations = [Organization.query.get(current_user.org_id)]
    
    return render_template('admin/users.html',
                         current_user=current_user,
                         users=users,
                         roles=roles,
                         organizations=organizations)

@admin_bp.route('/users/<int:user_id>/role', methods=['POST'])
@require_permission('manage_users')
def assign_role(current_user, user_id):
    """Assign role to a user"""
    try:
        user = User.query.get_or_404(user_id)
        role_id = request.json.get('role_id')
        
        # Check if org admin is trying to manage user from different org
        if current_user.is_org_admin() and user.organization != current_user.organization:
            return jsonify({'success': False, 'message': 'Cannot manage users from other organizations'}), 403
        
        # Remove existing role assignment
        UserRole.query.filter_by(user_id=user_id).delete()
        
        # Assign new role
        new_user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
            assigned_by=current_user.user_id
        )
        db.session.add(new_user_role)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Role assigned successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/tier', methods=['POST'])
@require_role('GLOBAL_ADMIN')
def assign_tier(current_user, user_id):
    """Assign subscription tier to a user (Free/Pro)"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.json
        tier = data.get('tier')
        
        if tier not in ['free', 'pro']:
            return jsonify({'success': False, 'message': 'Invalid tier value'}), 400
            
        user.subscription_tier = tier
        db.session.commit()
        
        return jsonify({'success': True, 'message': f'User updated to {tier.upper()} tier successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/users/<int:user_id>/organization', methods=['POST'])
@require_role('GLOBAL_ADMIN')
def assign_organization(current_user, user_id):
    """Assign user to an organization"""
    try:
        user = User.query.get_or_404(user_id)
        data = request.json
        org_id = data.get('org_id')
        
        # If org_id is empty/null, remove user from organization
        if not org_id:
            user.org_id = None
            user.dept_id = None
            user.team_id = None
            # Update legacy field
            user.organization = None
        else:
            org = Organization.query.get_or_404(org_id)
            user.org_id = org.org_id
            # Update legacy field for compatibility
            user.organization = org.name
            
            # Reset dept/team when changing org
            user.dept_id = None
            user.team_id = None
            
        db.session.commit()
        return jsonify({'success': True, 'message': 'Organization assigned successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/organizations')
@require_role('GLOBAL_ADMIN')
def manage_organizations(current_user):
    """Organization Management Page"""
    organizations = Organization.query.order_by(Organization.name).all()
    return render_template('admin/organizations.html',
                         current_user=current_user,
                         organizations=organizations)

@admin_bp.route('/organizations/create', methods=['POST'])
@require_role('GLOBAL_ADMIN')
def create_organization(current_user):
    """Create new organization"""
    try:
        data = request.json
        
        if Organization.query.filter_by(name=data['name']).first():
            return jsonify({'success': False, 'message': 'Organization with this name already exists'}), 400
            
        new_org = Organization(
            name=data['name'],
            logo_url=data.get('logo_url'),
            primary_color=data.get('primary_color', '#06b6d4'),
            is_active=data.get('is_active', True)
        )
        
        db.session.add(new_org)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Organization created successfully', 'org_id': new_org.org_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/organizations/<int:org_id>/edit', methods=['POST'])
@require_role('GLOBAL_ADMIN')
def edit_organization(current_user, org_id):
    """Edit organization"""
    try:
        org = Organization.query.get_or_404(org_id)
        data = request.json
        
        # Check name uniqueness if changed
        if data['name'] != org.name:
            if Organization.query.filter_by(name=data['name']).first():
                return jsonify({'success': False, 'message': 'Organization name already taken'}), 400
        
        org.name = data['name']
        org.logo_url = data.get('logo_url')
        org.primary_color = data.get('primary_color', '#06b6d4')
        org.is_active = data.get('is_active', True)
        
        db.session.commit()
        return jsonify({'success': True, 'message': 'Organization updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/organizations/<int:org_id>/delete', methods=['POST'])
@require_role('GLOBAL_ADMIN')
def delete_organization(current_user, org_id):
    """Delete organization"""
    try:
        org = Organization.query.get_or_404(org_id)
        
        # Check if has users
        if len(org.users) > 0:
            return jsonify({'success': False, 'message': f'Cannot delete organization with {len(org.users)} users'}), 400
            
        db.session.delete(org)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Organization deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

# ================================
# Department Management
# ================================

@admin_bp.route('/organizations/<int:org_id>/departments')
@require_role('GLOBAL_ADMIN', 'ORG_ADMIN')
def manage_departments(current_user, org_id):
    """List departments for an organization"""
    # Security check for ORG_ADMIN
    if current_user.is_org_admin() and current_user.org_id != org_id:
        return redirect(url_for('admin.dashboard'))
        
    org = Organization.query.get_or_404(org_id)
    return render_template('admin/departments.html',
                         current_user=current_user,
                         organization=org,
                         departments=org.departments)

@admin_bp.route('/organizations/<int:org_id>/departments/create', methods=['POST'])
@require_role('GLOBAL_ADMIN', 'ORG_ADMIN')
def create_department(current_user, org_id):
    """Create new department"""
    if current_user.is_org_admin() and current_user.org_id != org_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    try:
        data = request.json
        if Department.query.filter_by(org_id=org_id, name=data['name']).first():
            return jsonify({'success': False, 'message': 'Department already exists'}), 400
            
        new_dept = Department(
            org_id=org_id,
            name=data['name'],
            description=data.get('description')
        )
        db.session.add(new_dept)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Department created successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/departments/<int:dept_id>/delete', methods=['POST'])
@require_role('GLOBAL_ADMIN', 'ORG_ADMIN')
def delete_department(current_user, dept_id):
    dept = Department.query.get_or_404(dept_id)
    
    if current_user.is_org_admin() and current_user.org_id != dept.org_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    try:
        db.session.delete(dept)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Department deleted successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

# ================================
# Team Management
# ================================

@admin_bp.route('/departments/<int:dept_id>/teams')
@require_role('GLOBAL_ADMIN', 'ORG_ADMIN')
def manage_teams(current_user, dept_id):
    dept = Department.query.get_or_404(dept_id)
    if current_user.is_org_admin() and current_user.org_id != dept.org_id:
        return redirect(url_for('admin.dashboard'))
        
    # Fetch available users: In same Org, NOT in any team, and (in this dept OR no dept)
    available_users = User.query.filter(
        User.org_id == dept.org_id,
        User.team_id == None,
        (User.dept_id == dept_id) | (User.dept_id == None)
    ).all()

    return render_template('admin/teams.html',
                         current_user=current_user,
                         department=dept,
                         teams=dept.teams,
                         available_users=available_users)

@admin_bp.route('/teams/<int:team_id>/edit', methods=['POST'])
@require_role('GLOBAL_ADMIN', 'ORG_ADMIN')
def edit_team(current_user, team_id):
    team = Team.query.get_or_404(team_id)
    if current_user.is_org_admin() and current_user.org_id != team.department.org_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    try:
        data = request.json
        team.name = data['name']
        team.description = data.get('description')
        db.session.commit()
        return jsonify({'success': True, 'message': 'Team updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/teams/<int:team_id>/delete', methods=['POST'])
@require_role('GLOBAL_ADMIN', 'ORG_ADMIN')
def delete_team(current_user, team_id):
    team = Team.query.get_or_404(team_id)
    if current_user.is_org_admin() and current_user.org_id != team.department.org_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    try:
        # Reset users in this team
        for user in team.users:
            user.team_id = None
            
        db.session.delete(team)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Team deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/teams/<int:team_id>/members/add', methods=['POST'])
@require_role('GLOBAL_ADMIN', 'ORG_ADMIN')
def add_team_member(current_user, team_id):
    team = Team.query.get_or_404(team_id)
    if current_user.is_org_admin() and current_user.org_id != team.department.org_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    try:
        data = request.json
        user_id = data.get('user_id')
        user = User.query.get_or_404(user_id)
        
        # Verify user belongs to same org
        if user.org_id != team.department.org_id:
            return jsonify({'success': False, 'message': 'User must belong to the same organization'}), 400

        # If user is in a different department, block them
        if user.dept_id and user.dept_id != team.dept_id:
            return jsonify({'success': False, 'message': 'User belongs to a different department'}), 400

        # Auto-assign department if missing
        if not user.dept_id:
            user.dept_id = team.dept_id
            
        user.team_id = team_id
        db.session.commit()
        return jsonify({'success': True, 'message': 'Member added successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/teams/<int:team_id>/members/remove', methods=['POST'])
@require_role('GLOBAL_ADMIN', 'ORG_ADMIN')
def remove_team_member(current_user, team_id):
    team = Team.query.get_or_404(team_id)
    if current_user.is_org_admin() and current_user.org_id != team.department.org_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    try:
        data = request.json
        user_id = data.get('user_id')
        user = User.query.get_or_404(user_id)
        
        if user.team_id != team_id:
            return jsonify({'success': False, 'message': 'User is not in this team'}), 400
            
        user.team_id = None
        db.session.commit()
        return jsonify({'success': True, 'message': 'Member removed successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/departments/<int:dept_id>/teams/create', methods=['POST'])
@require_role('GLOBAL_ADMIN', 'ORG_ADMIN')
def create_team(current_user, dept_id):
    dept = Department.query.get_or_404(dept_id)
    if current_user.is_org_admin() and current_user.org_id != dept.org_id:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    try:
        data = request.json
        if Team.query.filter_by(dept_id=dept_id, name=data['name']).first():
            return jsonify({'success': False, 'message': 'Team already exists'}), 400
            
        new_team = Team(
            dept_id=dept_id,
            name=data['name'],
            description=data.get('description')
        )
        db.session.add(new_team)
        db.session.commit()
        return jsonify({'success': True, 'message': 'Team created successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/analytics')
@require_role('GLOBAL_ADMIN')
def analytics(current_user):
    """Global Analytics Dashboard"""
    # Get overall statistics
    stats = {
        'total_users': User.query.count(),
        'total_scenarios': db.session.query(func.count()).select_from(db.Model.metadata.tables['scenarios']).scalar() if 'scenarios' in db.Model.metadata.tables else 0,
        'total_responses': db.session.query(func.count()).select_from(db.Model.metadata.tables['user_responses']).scalar() if 'user_responses' in db.Model.metadata.tables else 0
    }
    
    # Data for charts
    # 1. Users per Organization
    org_data = db.session.query(
        Organization.name,
        func.count(User.user_id)
    ).join(User, Organization.org_id == User.org_id).group_by(Organization.name).all()
    
    org_chart_data = {
        'labels': [r[0] for r in org_data],
        'data': [r[1] for r in org_data]
    }
    
    # 2. User Registration Over Time (Last 7 days)
    # Note: SQLite/MySQL syntax difference for date handling might exist, using generic approach
    from datetime import datetime, timedelta
    dates = []
    counts = []
    for i in range(6, -1, -1):
        date = datetime.now().date() - timedelta(days=i)
        count = User.query.filter(func.date(User.created_date) == date).count()
        dates.append(date.strftime('%Y-%m-%d'))
        counts.append(count)
        
    registration_chart_data = {
        'labels': dates,
        'data': counts
    }
    
    return render_template('admin/analytics.html',
                         current_user=current_user,
                         stats=stats,
                         org_chart_data=org_chart_data,
                         registration_chart_data=registration_chart_data)

# Organization Admin Routes
@admin_bp.route('/org')
@require_role('ORG_ADMIN')
def org_dashboard(current_user):
    """Organization Admin Dashboard"""
    # Get users in the same organization
    org_users = User.query.filter_by(organization=current_user.organization).all()
    
    org_id = current_user.org_id
    if not org_id:
        # Fallback for legacy users without org_id set but with organization string
         # (This might happen if data migration wasn't perfect)
        pass 

    # 1. Active Users & Campaigns
    # Assuming 'Active' means they exist in the system for now
    active_users_count = len(org_users)
    campaigns_count = 3 # Placeholder as per plan
    
    # 2. Human-Risk Score Calculation
    # We'll base this on the inverse of their success rates in drills
    # High Success Rate = Low Risk.
    
    # Get all progress for these users
    org_user_ids = [u.user_id for u in org_users]
    
    # Calculate averages
    avg_phishing = db.session.query(func.avg(LearningProgress.phishing_success_rate))\
        .filter(LearningProgress.user_id.in_(org_user_ids)).scalar() or 0
    
    avg_baiting = db.session.query(func.avg(LearningProgress.baiting_success_rate))\
        .filter(LearningProgress.user_id.in_(org_user_ids)).scalar() or 0
        
    avg_pretexting = db.session.query(func.avg(LearningProgress.pretexting_success_rate))\
        .filter(LearningProgress.user_id.in_(org_user_ids)).scalar() or 0
    
    # Overall Average Success
    overall_success = (avg_phishing + avg_baiting + avg_pretexting) / 3 if (avg_phishing or avg_baiting or avg_pretexting) else 0
    
    # Risk Score (0-100). If Success is 80%, Risk is 20.
    # If no data (0% success), let's default to Medium Risk (50) instead of 100 to avoid panic on fresh install?
    # Actually, strict security would say 100% risk until proven otherwise. 
    # But let's go with (100 - Success).
    risk_score = round(100 - overall_success)
    
    risk_label = 'Low'
    if risk_score >= 70:
        risk_label = 'High'
    elif risk_score >= 40:
        risk_label = 'Medium'
        
    # 3. Top Weaknesses
    # Compare the 3 categories
    weaknesses = [
        {'name': 'Phishing', 'value': 100 - avg_phishing, 'color': '#ef4444'},
        {'name': 'Baiting', 'value': 100 - avg_baiting, 'color': '#f59e0b'},
        {'name': 'Pretexting', 'value': 100 - avg_pretexting, 'color': '#3b82f6'}
    ]
    # Sort by value (Risk) descending
    weaknesses.sort(key=lambda x: x['value'], reverse=True)
    
    # 4. Completion vs Failure
    # Get total responses count for these users
    total_responses = UserResponse.query.filter(UserResponse.user_id.in_(org_user_ids)).count()
    failed_responses = UserResponse.query.filter(UserResponse.user_id.in_(org_user_ids), UserResponse.is_correct == False).count()
    
    failure_rate = round((failed_responses / total_responses * 100) if total_responses > 0 else 0)
    completion_rate = 0 # Placeholder for module completion if we don't have easy query
    
    # 5. Department Snapshot
    departments = Department.query.filter_by(org_id=current_user.org_id).all()
    dept_snapshot = []
    
    for dept in departments:
        d_users = [u for u in org_users if u.dept_id == dept.dept_id]
        d_count = len(d_users)
        
        # Calculate Dept Risk
        if d_count > 0:
            d_ids = [u.user_id for u in d_users]
            d_phish = db.session.query(func.avg(LearningProgress.phishing_success_rate)).filter(LearningProgress.user_id.in_(d_ids)).scalar() or 0
            d_bait = db.session.query(func.avg(LearningProgress.baiting_success_rate)).filter(LearningProgress.user_id.in_(d_ids)).scalar() or 0
            d_pre = db.session.query(func.avg(LearningProgress.pretexting_success_rate)).filter(LearningProgress.user_id.in_(d_ids)).scalar() or 0
            d_avg = (d_phish + d_bait + d_pre) / 3
            d_risk = round(100 - d_avg)
            
            # Completion/Fail for dept
            d_total_resp = UserResponse.query.filter(UserResponse.user_id.in_(d_ids)).count()
            d_failed = UserResponse.query.filter(UserResponse.user_id.in_(d_ids), UserResponse.is_correct == False).count()
            d_fail_rate = round((d_failed / d_total_resp * 100) if d_total_resp > 0 else 0)
        else:
            d_risk = 0
            d_fail_rate = 0
            
        dept_snapshot.append({
            'name': dept.name,
            'users': d_count,
            'fail_rate': d_fail_rate,
            'completion': 0, # Placeholder
            'risk_score': d_risk
        })

    return render_template('admin/org_dashboard.html',
                         current_user=current_user,
                         total_org_users=active_users_count,
                         campaigns_count=campaigns_count,
                         risk_score=risk_score,
                         risk_label=risk_label,
                         weaknesses=weaknesses,
                         failure_rate=failure_rate,
                         completion_rate=completion_rate, # Mocked/Placeholder
                         dept_snapshot=dept_snapshot)

@admin_bp.route('/org/users/create', methods=['POST'])
@require_role('ORG_ADMIN')  
def create_org_user(current_user):
    """Create a new user in the organization"""
    try:
        from werkzeug.security import generate_password_hash
        
        username = request.json.get('username')
        email = request.json.get('email')
        password = request.json.get('password', 'temppass123')
        
        # Check if user already exists
        if User.query.filter_by(username=username).first():
            return jsonify({'success': False, 'message': 'Username already exists'}), 400
        
        # Create new user in same organization
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            organization=current_user.organization,
            account_type='Individual'
        )
        db.session.add(new_user)
        db.session.flush()
        
        # Assign LEARNER role by default
        learner_role = Role.query.filter_by(role_name='LEARNER').first()
        if learner_role:
            user_role = UserRole(
                user_id=new_user.user_id,
                role_id=learner_role.role_id,
                assigned_by=current_user.user_id
            )
            db.session.add(user_role)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'User created successfully', 'user_id': new_user.user_id})
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/org/reports')
@require_role('ORG_ADMIN')
def org_reports(current_user):
    """Organization Reports"""
    from datetime import datetime
    if not current_user.org_id:
        return render_template('admin/org_reports.html', current_user=current_user, org_users=[], now_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        
    org_users = User.query.filter_by(org_id=current_user.org_id).all()
    
    return render_template('admin/org_reports.html',
                         current_user=current_user,
                         now_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                         org_users=org_users)

@admin_bp.route('/export/org/<int:org_id>/summary.csv')
@require_role('GLOBAL_ADMIN')
def export_org_summary(current_user, org_id):
    """Export Organization Summary CSV"""
    # Restricted to GLOBAL_ADMIN only per requirements
    
    org = Organization.query.get_or_404(org_id)
    departments = Department.query.filter_by(org_id=org_id).all()
    
    # Generate CSV
    si = io.StringIO()
    cw = csv.writer(si)
    
    # 1. Report Header
    cw.writerow(['Organization Summary Report'])
    cw.writerow(['Organization Name', org.name])
    cw.writerow(['Generated By', current_user.username])
    cw.writerow(['Date', datetime.now().strftime('%Y-%m-%d %H:%M:%S')])
    cw.writerow([])
    
    # 2. Key Metrics
    total_users = User.query.filter_by(org_id=org_id).count()
    cw.writerow(['Key Metrics'])
    cw.writerow(['Total Users', total_users])
    
    # Calculate Org Stats
    avg_phishing = db.session.query(func.avg(LearningProgress.phishing_success_rate)).join(User).filter(User.org_id == org_id).scalar() or 0
    avg_baiting = db.session.query(func.avg(LearningProgress.baiting_success_rate)).join(User).filter(User.org_id == org_id).scalar() or 0
    avg_pretexting = db.session.query(func.avg(LearningProgress.pretexting_success_rate)).join(User).filter(User.org_id == org_id).scalar() or 0
    
    cw.writerow(['Avg Phishing Susceptibility', f"{avg_phishing:.1f}%"])
    cw.writerow(['Avg Baiting Susceptibility', f"{avg_baiting:.1f}%"])
    cw.writerow(['Avg Pretexting Susceptibility', f"{avg_pretexting:.1f}%"])
    cw.writerow([])

    # 3. Department Breakdown
    cw.writerow(['Department Breakdown'])
    cw.writerow(['Department Name', 'User Count', 'Avg Score', 'Phishing Risk', 'Baiting Risk', 'Pretexting Risk'])
    
    for dept in departments:
        dept_users = User.query.filter_by(dept_id=dept.dept_id).all()
        count = len(dept_users)
        avg_score = sum(u.total_score for u in dept_users) / count if count else 0
        
        # Dept specific risks
        d_phishing = db.session.query(func.avg(LearningProgress.phishing_success_rate)).join(User).filter(User.dept_id == dept.dept_id).scalar() or 0
        d_baiting = db.session.query(func.avg(LearningProgress.baiting_success_rate)).join(User).filter(User.dept_id == dept.dept_id).scalar() or 0
        d_pretexting = db.session.query(func.avg(LearningProgress.pretexting_success_rate)).join(User).filter(User.dept_id == dept.dept_id).scalar() or 0

        cw.writerow([
            dept.name, 
            count, 
            f"{avg_score:.2f}",
            f"{d_phishing:.1f}%",
            f"{d_baiting:.1f}%",
            f"{d_pretexting:.1f}%"
        ])
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = f"attachment; filename={org.name.replace(' ', '_')}_summary.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@admin_bp.route('/quick-launch')
@require_role('GLOBAL_ADMIN')
def quick_launch(current_user):
    """Quick Launch Page"""
    return render_template('admin/quick_launch.html', current_user=current_user)

@admin_bp.route('/quick-launch/api', methods=['POST'])
@require_role('GLOBAL_ADMIN')
def quick_launch_api(current_user):
    """Handle Quick Launch Form Submission"""
    try:
        from werkzeug.security import generate_password_hash
        from app.models import Campaign, CampaignTarget
        from app.email_service import send_invite_email
        
        data = request.json
        org_name = data.get('org_name')
        sector = data.get('sector')
        size = data.get('size_bucket')
        country = data.get('country')
        timezone = data.get('timezone')
        user_emails = data.get('user_emails', '').strip().split('\n')
        
        # 1. Create Organization
        if Organization.query.filter_by(name=org_name).first():
            return jsonify({'success': False, 'message': 'Organization name already taken'}), 400
            
        new_org = Organization(
            name=org_name,
            sector=sector,
            size_bucket=size,
            country=country,
            timezone=timezone,
            is_active=True
        )
        db.session.add(new_org)
        db.session.flush() # Get ID
        
        # 2. Create Default Department
        default_dept = Department(
            org_id=new_org.org_id,
            name='General',
            description='Default department for new users.'
        )
        db.session.add(default_dept)
        db.session.flush()
        
        # 3. Create Users
        created_users = []
        learner_role = Role.query.filter_by(role_name='LEARNER').first()
        
        for email in user_emails:
            email = email.strip()
            if not email: continue
            
            # Simple username generation: email prefix + random suffix if needed
            username = email.split('@')[0]
            if User.query.filter_by(username=username).first():
                import random
                username = f"{username}_{random.randint(100,999)}"
            
            new_user = User(
                username=username,
                email=email,
                password=generate_password_hash('temppass123'),
                org_id=new_org.org_id,
                dept_id=default_dept.dept_id,
                organization=new_org.name, # Legacy
                account_type='Individual'
            )
            db.session.add(new_user)
            db.session.flush()
            
            # Assign Role
            if learner_role:
                ur = UserRole(user_id=new_user.user_id, role_id=learner_role.role_id, assigned_by=current_user.user_id)
                db.session.add(ur)
            
            created_users.append(new_user)
            
            # Send Email Invite
            send_invite_email(new_user, org_name, 'temppass123')
            
        # 4. Create Campaign
        campaign = Campaign(
            org_id=new_org.org_id,
            name='Onboarding Phishing Basics',
            type='Phishing',
            status='Active',
            launched_at=datetime.utcnow()
        )
        db.session.add(campaign)
        db.session.flush()
        
        # 5. Link Users to Campaign
        for user in created_users:
            target = CampaignTarget(
                campaign_id=campaign.campaign_id,
                user_id=user.user_id,
                status='Pending'
            )
            db.session.add(target)
            
        db.session.commit()
        
        return jsonify({
            'success': True, 
            'message': f'Launched {org_name} with {len(created_users)} users and active campaign.',
            'org_id': new_org.org_id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500

@admin_bp.route('/reports')
@require_role('GLOBAL_ADMIN')
def suspicious_reports(current_user):
    """List all suspicious reports."""
    reports = SuspiciousReport.query.order_by(SuspiciousReport.created_at.desc()).all()
    return render_template('admin/suspicious_reports.html', current_user=current_user, reports=reports)

@admin_bp.route('/reports/<int:report_id>/convert', methods=['POST'])
@require_role('GLOBAL_ADMIN')
def convert_report(current_user, report_id):
    """Convert a report into a simulation scenario."""
    report = SuspiciousReport.query.get_or_404(report_id)
    
    question_text = request.form.get('question_text')
    # Parse options from form (assuming 4 options)
    options = [
        request.form.get('option1'),
        request.form.get('option2'),
        request.form.get('option3'),
        request.form.get('option4')
    ]
    correct_option_index = int(request.form.get('correct_option'))
    explanation = request.form.get('explanation')
    
    # Create new Scenario
    scenario = Scenario(
        scenario_type=report.category,
        difficulty_level='medium',
        scenario_description=question_text,
        correct_answer=options[correct_option_index],
        options_json=options,
        explanation=explanation
    )
    
    report.status = 'Converted'
    report.admin_notes = f"Converted to scenario ID: {scenario.scenario_id} on {datetime.now()}"
    
    db.session.add(scenario)
    db.session.commit()
    
    flash('Report successfully converted to a new Quiz Scenario!', 'success')
    return redirect(url_for('admin.suspicious_reports'))

