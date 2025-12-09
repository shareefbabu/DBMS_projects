from app import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120))
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_score = db.Column(db.Integer, default=0)
    vulnerability_level = db.Column(db.String(32), default='Medium')
    organization = db.Column(db.String(100))  # Legacy field, kept for backward compatibility
    account_type = db.Column(db.String(20), default='Individual')
    org_id = db.Column(db.Integer, db.ForeignKey('organizations.org_id'), nullable=True)
    dept_id = db.Column(db.Integer, db.ForeignKey('departments.dept_id'), nullable=True)
    team_id = db.Column(db.Integer, db.ForeignKey('teams.team_id'), nullable=True)
    
    # Subscription Fields
    subscription_tier = db.Column(db.String(20), default='free') # 'free' or 'pro'
    weekly_scenario_count = db.Column(db.Integer, default=0)
    last_week_reset = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    responses = db.relationship('UserResponse', backref='user', lazy=True, cascade='all, delete-orphan')
    progress = db.relationship('LearningProgress', backref='user', lazy=True, cascade='all, delete-orphan')
    achievements = db.relationship('Achievement', backref='user', lazy=True, cascade='all, delete-orphan')
    roles = db.relationship('UserRole', foreign_keys='UserRole.user_id', back_populates='user', lazy=True, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')
    
    # Organization relationships (backrefs defined in org models)
    # org = backref from Organization
    # dept = backref from Department  
    # team = backref from Team
    
    @property
    def role(self):
        """Get the user's primary role"""
        if self.roles and len(self.roles) > 0:
            # Get the role object from the first UserRole relationship
            from app.models import Role
            return Role.query.get(self.roles[0].role_id)
        return None
    
    def has_role(self, role_name):
        """Check if user has a specific role"""
        user_role = self.role
        return user_role and user_role.role_name == role_name
    
    def has_permission(self, permission_name):
        """Check if user has a specific permission"""
        user_role = self.role
        if not user_role:
            return False
        # Check if any of the role's permissions match
        for perm in user_role.permissions:
            if perm.permission_name == permission_name:
                return True
        return False
    
    def is_admin(self):
        """Check if user has admin privileges"""
        return self.has_role('GLOBAL_ADMIN')
    
    def is_org_admin(self):
        """Check if user is an org admin"""
        return self.has_role('ORG_ADMIN')

    def is_global_admin(self):
        """Check if user is global admin"""
        return self.has_role('GLOBAL_ADMIN')
    
    def __repr__(self):
        return f'<User {self.username}>'

class Scenario(db.Model):
    __tablename__ = 'scenarios'
    
    scenario_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    scenario_type = db.Column(db.String(50), nullable=False)
    difficulty_level = db.Column(db.String(32), nullable=False)
    scenario_description = db.Column(db.Text, nullable=False)
    correct_answer = db.Column(db.Text, nullable=False)
    keywords_to_identify = db.Column(db.Text)
    explanation = db.Column(db.Text)
    options_json = db.Column(db.JSON)  # Stores options for MCQ scenarios
    steps_json = db.Column(db.Text)  # Stores JSON list of correct order for IncidentResponse
    
    # Relationships
    responses = db.relationship('UserResponse', backref='scenario', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.scenario_id,
            'type': self.scenario_type,
            'difficulty': self.difficulty_level,
            'description': self.scenario_description,
            'correct_answer': self.correct_answer,
            'explanation': self.explanation,
            'options': self.options_json if self.options_json else None,
            'steps': json.loads(self.steps_json) if self.steps_json else None
        }
    
    def __repr__(self):
        return f'<Scenario {self.scenario_type} - {self.difficulty_level}>'

class UserResponse(db.Model):
    __tablename__ = 'user_responses'
    
    response_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    scenario_id = db.Column(db.Integer, db.ForeignKey('scenarios.scenario_id'), nullable=False)
    user_response = db.Column(db.String(50))
    response_json = db.Column(db.Text)  # Stores complex responses like ordered steps
    is_correct = db.Column(db.Boolean)
    response_time = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    details = db.relationship('ResponseDetail', backref='response', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Response {self.response_id}>'

class LearningProgress(db.Model):
    __tablename__ = 'learning_progress'
    
    progress_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    phishing_success_rate = db.Column(db.Float, default=0.0)
    baiting_success_rate = db.Column(db.Float, default=0.0)
    pretexting_success_rate = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Progress User {self.user_id}>'

class AchievementDefinition(db.Model):
    __tablename__ = 'achievement_definitions'
    
    definition_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50)) # Learning, Simulation, Behavior, Consistency
    tier = db.Column(db.String(20)) # Bronze, Silver, Gold
    icon = db.Column(db.String(50)) 
    condition_description = db.Column(db.String(200))
    target_value = db.Column(db.Integer, default=1)
    is_org_only = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<AchievementDef {self.slug}>'

class Achievement(db.Model):
    __tablename__ = 'achievements'
    
    achievement_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    definition_id = db.Column(db.Integer, db.ForeignKey('achievement_definitions.definition_id'), nullable=True)
    achievement_name = db.Column(db.String(100)) # Legacy
    criteria_met = db.Column(db.String(100)) # Legacy
    earned_date = db.Column(db.DateTime, nullable=True) # Nullable if 'In Progress'
    status = db.Column(db.String(20), default='In Progress') # Locked, In Progress, Earned
    current_value = db.Column(db.Integer, default=0)
    
    # Relationships
    definition = db.relationship('AchievementDefinition', backref='user_achievements')
    
    def __repr__(self):
        return f'<Achievement {self.achievement_name}>'

# ==========================================
# ADVANCED FEATURES MODELS
# ==========================================

class Role(db.Model):
    __tablename__ = 'roles'
    
    role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    is_system_role = db.Column(db.Boolean, default=False)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    updated_date = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    permissions = db.relationship('Permission', secondary='role_permissions', backref='roles', lazy='dynamic')
    
    def __repr__(self):
        return f'<Role {self.role_name}>'

class Permission(db.Model):
    __tablename__ = 'permissions'
    
    permission_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    permission_name = db.Column(db.String(100), unique=True, nullable=False)
    resource = db.Column(db.String(50), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Permission {self.permission_name}>'

# =============================================
# Multi-Tenant Organization Models
# =============================================

class Organization(db.Model):
    __tablename__ = 'organizations'
    
    org_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    logo_url = db.Column(db.String(255))
    primary_color = db.Column(db.String(7), default='#06b6d4')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Detailed Info (Quick Launch)
    sector = db.Column(db.String(50))
    size_bucket = db.Column(db.String(20))
    country = db.Column(db.String(50))
    timezone = db.Column(db.String(50))
    
    # Relationships
    departments = db.relationship('Department', backref='organization', lazy=True, cascade='all, delete-orphan')
    users = db.relationship('User', backref='org', foreign_keys='User.org_id', lazy=True)
    
    def __repr__(self):
        return f'<Organization {self.name}>'
    
    def get_user_count(self):
        """Get total number of users in this organization"""
        return len(self.users)
    
    def get_department_count(self):
        """Get total number of departments"""
        return len(self.departments)


class Department(db.Model):
    __tablename__ = 'departments'
    
    dept_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    org_id = db.Column(db.Integer, db.ForeignKey('organizations.org_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    teams = db.relationship('Team', backref='department', lazy=True, cascade='all, delete-orphan')
    users = db.relationship('User', backref='dept', foreign_keys='User.dept_id', lazy=True)
    
    def __repr__(self):
        return f'<Department {self.name}>'
    
    def get_team_count(self):
        """Get total number of teams in this department"""
        return len(self.teams)
    
    def get_user_count(self):
        """Get total number of users in this department"""
        return len(self.users)


class Team(db.Model):
    __tablename__ = 'teams'
    
    team_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    dept_id = db.Column(db.Integer, db.ForeignKey('departments.dept_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    team_lead_user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    users = db.relationship('User', backref='team', foreign_keys='User.team_id', lazy=True)
    team_lead = db.relationship('User', foreign_keys=[team_lead_user_id], post_update=True)
    
    def __repr__(self):
        return f'<Team {self.name}>'
    
    def get_user_count(self):
        """Get total number of users in this team"""
        return len(self.users)

class UserRole(db.Model):
    __tablename__ = 'user_roles'
    
    user_role_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)
    assigned_by = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow)
    expires_date = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', foreign_keys=[user_id], back_populates='roles')
    assigner = db.relationship('User', foreign_keys=[assigned_by])
    
    def __repr__(self):
        return f'<UserRole {self.user_id}-{self.role_id}>'

class RolePermission(db.Model):
    __tablename__ = 'role_permissions'
    
    role_permission_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.role_id'), nullable=False)
    permission_id = db.Column(db.Integer, db.ForeignKey('permissions.permission_id'), nullable=False)
    granted_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<RolePermission {self.role_id}-{self.permission_id}>'

class ResponseDetail(db.Model):
    __tablename__ = 'response_details'
    
    detail_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    response_id = db.Column(db.Integer, db.ForeignKey('user_responses.response_id'), nullable=False)
    step_number = db.Column(db.Integer, default=1)
    step_description = db.Column(db.Text)
    user_answer = db.Column(db.Text)
    expected_answer = db.Column(db.Text)
    is_correct = db.Column(db.Boolean)
    confidence_level = db.Column(db.Numeric(3, 2))
    time_spent = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    flags = db.Column(db.JSON)
    
    def __repr__(self):
        return f'<ResponseDetail {self.detail_id}>'

class ScenarioProgress(db.Model):
    __tablename__ = 'scenario_progress'
    
    progress_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    scenario_id = db.Column(db.Integer, db.ForeignKey('scenarios.scenario_id'), nullable=False)
    current_step = db.Column(db.Integer, default=1)
    total_steps = db.Column(db.Integer)
    completion_percentage = db.Column(db.Numeric(5, 2))
    last_interaction = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = db.Column(db.Enum('in_progress', 'completed', 'abandoned'), default='in_progress')
    session_data = db.Column(db.JSON)
    
    def __repr__(self):
        return f'<ScenarioProgress {self.user_id}-{self.scenario_id}>'

class NotificationType(db.Model):
    __tablename__ = 'notification_types'
    
    type_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    default_template = db.Column(db.Text)
    is_active = db.Column(db.Boolean, default=True)
    created_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<NotificationType {self.type_name}>'

class Notification(db.Model):
    __tablename__ = 'notifications'
    
    notification_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('notification_types.type_id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.Enum('pending', 'sent', 'read', 'archived'), default='pending')
    priority = db.Column(db.Enum('low', 'medium', 'high', 'urgent'), default='medium')
    scheduled_for = db.Column(db.DateTime, nullable=True)
    action_url = db.Column(db.String(500))  # Added missing column
    sent_at = db.Column(db.DateTime, nullable=True)
    read_at = db.Column(db.DateTime, nullable=True)
    expires_at = db.Column(db.DateTime, nullable=True)
    meta_data = db.Column('metadata', db.JSON)  # Map to DB 'metadata', avoid name conflict
    created_date = db.Column(db.DateTime, default=datetime.utcnow)  # Matches DB 'created_date'
    # status_change = db.Column(db.String(50), nullable=False)  # REMOVED: Not in DB
    # changed_at = db.Column(db.DateTime, default=datetime.utcnow) # REMOVED: Not in DB
    # changed_by = db.Column(db.Integer) # REMOVED: Likely not in DB or nullable
    # notes = db.Column(db.Text) # Check if in DB? Assuming yes or nullable default. But wait, output didn't list it.
    
    def __repr__(self):
        return f'<Notification {self.notification_id}>'

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    audit_id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=True)
    username = db.Column(db.String(80))
    action_type = db.Column(db.String(100), nullable=False)
    resource_type = db.Column(db.String(50))
    resource_id = db.Column(db.Integer)
    action_description = db.Column(db.Text, nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    request_method = db.Column(db.String(10))
    request_url = db.Column(db.String(500))
    status = db.Column(db.Enum('success', 'failure', 'error'), nullable=False)
    error_message = db.Column(db.Text)
    old_value = db.Column(db.JSON)
    new_value = db.Column(db.JSON)
    severity = db.Column(db.Enum('low', 'medium', 'high', 'critical'), default='medium')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    session_id = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<AuditLog {self.action_type} - {self.timestamp}>'

# ==========================================
# CAMPAIGN MANAGEMENT
# ==========================================

class Campaign(db.Model):
    __tablename__ = 'campaigns'
    
    campaign_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    org_id = db.Column(db.Integer, db.ForeignKey('organizations.org_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False) # Phishing, Baiting
    status = db.Column(db.String(20), default='Draft') # Draft, Active, Completed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    launched_at = db.Column(db.DateTime)
    
    # Relationships
    targets = db.relationship('CampaignTarget', backref='campaign', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Campaign {self.name}>'

class CampaignTarget(db.Model):
    __tablename__ = 'campaign_targets'
    
    target_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.campaign_id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    status = db.Column(db.String(20), default='Pending') # Pending, Sent, Opened, Clicked...
    sent_at = db.Column(db.DateTime)
    interacted_at = db.Column(db.DateTime)
    
    # Relationships
    user = db.relationship('User', backref='campaign_targets')
    
    def __repr__(self):
        return f'<CampaignTarget {self.campaign_id}-{self.user_id}>'

# ==========================================
# PATH TO MASTERY - NEW MODELS
# ==========================================

class Topic(db.Model):
    """Security topics like Phishing, Passwords, Cloud Security, etc."""
    __tablename__ = 'topics'
    
    topic_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic_number = db.Column(db.Integer, nullable=False)
    topic_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    icon = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    difficulty_levels = db.relationship('DifficultyLevel', backref='topic', lazy=True, cascade='all, delete-orphan', order_by='DifficultyLevel.level_number')

class DifficultyLevel(db.Model):
    """Difficulty levels within topics: Fundamentals, Intermediate, Advanced, Expert"""
    __tablename__ = 'difficulty_levels'
    
    difficulty_level_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.topic_id'), nullable=False)
    level_number = db.Column(db.Integer, nullable=False)  # 1-4
    level_name = db.Column(db.String(50), nullable=False)  # Fundamentals, Intermediate, Advanced, Expert
    description = db.Column(db.Text)
    previous_level_id = db.Column(db.Integer, db.ForeignKey('difficulty_levels.difficulty_level_id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    modules = db.relationship('LearningModule', backref='difficulty_level', lazy=True, cascade='all, delete-orphan', order_by='LearningModule.order_index')
    previous_level = db.relationship('DifficultyLevel', remote_side=[difficulty_level_id], backref='next_levels')

class LearningPath(db.Model):
    __tablename__ = 'learning_paths'
    
    path_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    path_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    total_levels = db.Column(db.Integer, default=4)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    levels = db.relationship('PathLevel', backref='path', lazy=True, cascade='all, delete-orphan')

class PathLevel(db.Model):
    __tablename__ = 'path_levels'
    
    level_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.path_id'), nullable=False)
    level_number = db.Column(db.Integer, nullable=False)
    level_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    unlock_score = db.Column(db.Integer, default=0)
    
    # Relationships
    modules = db.relationship('LearningModule', backref='level', lazy=True, cascade='all, delete-orphan')

class Category(db.Model):
    __tablename__ = 'categories'
    
    category_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_name = db.Column(db.String(50), unique=True, nullable=False)
    icon = db.Column(db.String(50))
    color_code = db.Column(db.String(20))
    description = db.Column(db.Text)

class ContentType(db.Model):
    __tablename__ = 'content_types'
    
    type_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type_name = db.Column(db.String(20), unique=True, nullable=False)
    difficulty_multiplier = db.Column(db.Float, default=1.0)

class LearningModule(db.Model):
    __tablename__ = 'learning_modules'
    
    module_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    level_id = db.Column(db.Integer, db.ForeignKey('path_levels.level_id'), nullable=True)  # Keep for backward compat
    difficulty_level_id = db.Column(db.Integer, db.ForeignKey('difficulty_levels.difficulty_level_id'), nullable=True)  # New hierarchical structure
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)
    type_id = db.Column(db.Integer, db.ForeignKey('content_types.type_id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    content_json = db.Column(db.JSON)
    points_value = db.Column(db.Integer, default=100)
    estimated_time_minutes = db.Column(db.Integer, default=5)
    order_index = db.Column(db.Integer, default=0)
    
    # Relationships
    category = db.relationship('Category', backref='modules')
    type = db.relationship('ContentType', backref='modules')

class UserProgress(db.Model):
    __tablename__ = 'user_progress'
    
    progress_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.path_id'), nullable=True)  # Keep for backward compat
    level_id = db.Column(db.Integer, db.ForeignKey('path_levels.level_id'), nullable=True)  # Keep for backward compat
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.topic_id'), nullable=True)  # New hierarchical structure
    difficulty_level_id = db.Column(db.Integer, db.ForeignKey('difficulty_levels.difficulty_level_id'), nullable=True)  # New hierarchical structure
    module_id = db.Column(db.Integer, db.ForeignKey('learning_modules.module_id'), nullable=False)
    score = db.Column(db.Integer, default=0)
    status = db.Column(db.Enum('locked', 'unlocked', 'in_progress', 'completed'), default='locked')
    completed_at = db.Column(db.DateTime)
    first_viewed_at = db.Column(db.DateTime)
    last_activity_at = db.Column(db.DateTime)
    view_count = db.Column(db.Integer, default=0)
    
    # Relationships
    module = db.relationship('LearningModule')

class ModuleAttempt(db.Model):
    __tablename__ = 'module_attempts'
    
    attempt_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('learning_modules.module_id'), nullable=False)
    attempt_number = db.Column(db.Integer, default=1)
    score = db.Column(db.Integer)
    time_spent_seconds = db.Column(db.Integer)
    answers_json = db.Column(db.JSON)
    attempt_date = db.Column(db.DateTime, default=datetime.utcnow)

class Certificate(db.Model):
    __tablename__ = 'certificates'
    
    cert_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.path_id'), nullable=False)
    certificate_code = db.Column(db.String(50), unique=True, nullable=False)
    issued_date = db.Column(db.DateTime, default=datetime.utcnow)
    verified_score = db.Column(db.Float)

class Leaderboard(db.Model):
    __tablename__ = 'leaderboards'
    
    rank_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    path_id = db.Column(db.Integer, db.ForeignKey('learning_paths.path_id'), nullable=False)
    total_score = db.Column(db.Integer, default=0)
    modules_completed = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='leaderboard_entries')

class MicroLesson(db.Model):
    __tablename__ = 'micro_lessons'
    
    lesson_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.category_id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    content_text = db.Column(db.Text, nullable=False)
    est_time_minutes = db.Column(db.Integer, default=5)
    quiz_json = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    category = db.relationship('Category', backref='micro_lessons')

class AssignedLesson(db.Model):
    __tablename__ = 'assigned_lessons'
    
    assignment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    lesson_id = db.Column(db.Integer, db.ForeignKey('micro_lessons.lesson_id'), nullable=False)
    scenario_id = db.Column(db.Integer, db.ForeignKey('scenarios.scenario_id'))
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum('pending', 'in_progress', 'completed'), default='pending')
    quiz_score = db.Column(db.Integer, default=0)
    completed_at = db.Column(db.DateTime)
    
    # Relationships
    lesson = db.relationship('MicroLesson')

class SuspiciousReport(db.Model):
    __tablename__ = 'suspicious_reports'
    
    report_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    org_id = db.Column(db.Integer, db.ForeignKey('organizations.org_id'))
    content_text = db.Column(db.Text)
    screenshot_path = db.Column(db.String(255))
    category = db.Column(db.String(50), nullable=False)
    status = db.Column(db.Enum('Pending', 'Approved', 'Rejected', 'Converted'), default='Pending')
    admin_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='suspicious_reports')
    organization = db.relationship('Organization', backref='suspicious_reports')
    
    def __repr__(self):
        return f'<SuspiciousReport {self.report_id} - {self.category}>'

