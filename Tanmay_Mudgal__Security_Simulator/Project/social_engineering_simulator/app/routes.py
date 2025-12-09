from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, flash, current_app
from werkzeug.utils import secure_filename
import os
from werkzeug.security import generate_password_hash, check_password_hash
from app import db, limiter
from app.models import User, Scenario, UserResponse, LearningProgress, Achievement, ResponseDetail, Notification, AuditLog, MicroLesson, AssignedLesson, Category, SuspiciousReport, Role, UserRole, Organization, Department, Team
from app.utils import log_audit, create_notification, require_permission
from app.ml_model import ml_engine
from datetime import datetime
import random
import numpy as np
import json

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('main.login'))

@main_bp.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    feedback = data.get('feedback')
    
    if not feedback:
        return jsonify({'error': 'No feedback provided'}), 400
        
    user = User.query.get(session['user_id'])
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Telegram Integration
    bot_token = current_app.config.get('TELEGRAM_BOT_TOKEN')
    chat_id = current_app.config.get('TELEGRAM_CHAT_ID')
    
    success = False
    
    if bot_token and chat_id:
        import requests
        try:
            message = (
                f"📝 *New Feedback Received*\n"
                f"👤 *User:* {user.username} (ID: {user.user_id})\n"
                f"🕒 *Time:* {timestamp}\n\n"
                f"💬 *Message:*\n{feedback}"
            )
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            response = requests.post(url, json=payload)
            if response.status_code == 200:
                success = True
            else:
                print(f"Telegram Error: {response.text}")
        except Exception as e:
            print(f"Error sending to Telegram: {e}")
            
    # Fallback log if Telegram fails or is not configured
    print(f"[FEEDBACK] User {user.username}: {feedback}")
    
    return jsonify({
        'success': True, 
        'message': 'Feedback sent!' if success else 'Feedback saved (Telegram not configured)'
    })


from flask_wtf.csrf import generate_csrf


@main_bp.route('/register', methods=['GET', 'POST'])
@limiter.limit("3 per minute")
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        organization = request.form.get('organization')
        account_type = request.form.get('account_type')
        
        # Validate Password Strength
        import re
        password_regex = r'^(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*(),.?":{}|<>]).{8,}$'
        
        if not re.match(password_regex, password):
            flash('Password must be at least 8 characters long and include an uppercase letter, a number, and a special character.', 'error')
            return render_template('register.html')
            
        # Check if user exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists. Please choose another.', 'error')
            return render_template('register.html')
        
        # Organization Handling
        user_org_id = None
        user_dept_id = None
        is_new_org = False

        if account_type == 'Enterprise' and organization:
            # Check if organization exists
            org_obj = Organization.query.filter_by(name=organization).first()
            if org_obj:
                # SECURITY: Prevent hijacking or accidental joining.
                # Enterprise registration implies creation. Existing orgs require invites.
                flash(f'Organization "{organization}" already exists. Please choose a unique name or ask your administrator for an invite link.', 'error')
                return render_template('register.html')
            
            # Create NEW Organization
            org_obj = Organization(name=organization, is_active=True)
            db.session.add(org_obj)
            db.session.flush() # Get ID
            is_new_org = True 
                
            # Ensure default department exists
            dept_obj = Department.query.filter_by(org_id=org_obj.org_id, name='General').first()
            if not dept_obj:
                dept_obj = Department(org_id=org_obj.org_id, name='General', description='Default Department')
                db.session.add(dept_obj)
                db.session.flush()
                
            # Assign Org/Dept to User
            user_org_id = org_obj.org_id
            user_dept_id = dept_obj.dept_id

        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(
            username=username, 
            password=hashed_password, 
            email=email,
            organization=organization,
            account_type=account_type,
            org_id=user_org_id,
            dept_id=user_dept_id
        )
        
        try:
            db.session.add(new_user)
            db.session.commit()

            # Assign Role based on Account Type AND Org Status
            # Security Fix: Only assign ORG_ADMIN if they successfully created a NEW organization.
            # Joining an existing organization defaults to LEARNER.
            if account_type == 'Enterprise' and is_new_org:
                role = Role.query.filter_by(role_name='ORG_ADMIN').first()
                flash(f'Organization "{organization}" created. You are the Administrator.', 'success')
            else:
                role = Role.query.filter_by(role_name='LEARNER').first()
                if account_type == 'Enterprise' and not is_new_org:
                     flash(f'Joined existing organization "{organization}".', 'info')
            
            if role:
                user_role = UserRole(user_id=new_user.user_id, role_id=role.role_id)
                db.session.add(user_role)
                db.session.commit()
            
            # Create learning progress entry
            progress = LearningProgress(user_id=new_user.user_id)
            db.session.add(progress)
            db.session.commit()
            
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error during registration: {str(e)}', 'error')
            return render_template('register.html')
    
    return render_template('register.html')

@main_bp.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # organization = request.form.get('organization') # Removed
        # account_type = request.form.get('account_type') # Removed
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.user_id
            session['username'] = user.username
            session['is_admin'] = user.is_admin()
            session['is_org_admin'] = user.is_org_admin()
            
            # Store primary role for UI display
            user_role_obj = user.role
            session['role'] = user_role_obj.role_name if user_role_obj else 'User'
            
            # Store independent org_id for easier template access
            session['org_id'] = user.org_id
            
            # Log successful login
            log_audit(user.user_id, 'login', 'User logged in successfully', status='success')
            
            # Check Consistency Achievements
            from app.services.achievement_service import AchievementService
            AchievementService.check_consistency_achievements(user.user_id)
            
            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            # Log failed login
            log_audit(None, 'login', f'Failed login attempt for username: {username}', status='failure', severity='high')
            flash('Invalid username or password', 'error')
            return render_template('login.html')
    
    return render_template('login.html')

@main_bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # Calculate statistics
    responses = UserResponse.query.filter_by(user_id=user_id).all()
    total_responses = len(responses)
    correct_responses = sum(1 for r in responses if r.is_correct)
    accuracy = (correct_responses / total_responses * 100) if total_responses > 0 else 0
    
    # Get achievements
    achievements = Achievement.query.filter_by(user_id=user_id).all()
    
    # Get recent activity
    recent_activity = UserResponse.query.filter_by(user_id=user_id).order_by(UserResponse.timestamp.desc()).limit(5).all()
    
    # Calculate Chart Data (Last 7 Days)
    from datetime import timedelta
    today = datetime.utcnow().date()
    dates = [(today - timedelta(days=i)) for i in range(6, -1, -1)]
    chart_labels = [d.strftime('%b %d') for d in dates]
    chart_data = []
    
    # Optimization: Fetch all for user once (already done in all_responses)
    # Filter in memory since dataset is small per user
    for d in dates:
        # Count responses for this day
        count = sum(1 for r in responses if r.timestamp.date() == d)
        chart_data.append(count)
        
    activity_chart = {'labels': chart_labels, 'data': chart_data}
    
    return render_template('dashboard.html', 
                         user=user, 
                         accuracy=round(accuracy, 1),
                         total_responses=total_responses,
                         achievements=achievements,
                         recent_activity=recent_activity,
                         activity_chart=activity_chart)

@main_bp.route('/get-scenario')
def get_scenario():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    user_id = session['user_id']
    
    # Get user's response history grouped by type
    all_responses = UserResponse.query.filter_by(user_id=user_id).all()
    
    responses_by_type = {}
    
    for response in all_responses:
        # Dynamically build response dictionary
        scenario = Scenario.query.get(response.scenario_id)
        if scenario:
            if scenario.scenario_type not in responses_by_type:
                responses_by_type[scenario.scenario_type] = []
            responses_by_type[scenario.scenario_type].append(response)
    
    # Calculate user features
    try:
        user_features = ml_engine.calculate_user_features(responses_by_type)
        recommended_type = ml_engine.recommend_scenario_type(user_features)
        difficulty_level = ml_engine.get_difficulty_level(user_features)
    except:
        # Fallback if ML engine expects specific keys
        recommended_type = 'Phishing'
        difficulty_level = 'medium'

    # === FREE TIER LIMIT & RESTRICTION CHECK ===
    user = User.query.get(user_id)
    
    # Check usage limit (5 per week for Free)
    if not user.is_admin and user.subscription_tier != 'pro':
        # Reset counter if new week
        now = datetime.utcnow()
        if not user.last_week_reset or (now - user.last_week_reset).days >= 7:
            user.weekly_scenario_count = 0
            user.last_week_reset = now
            db.session.commit()
            
        if user.weekly_scenario_count >= 5:
            # Render a "limit reached" page or redirect with flash
            # For simplicity, returning a simple limit page or flash + dashboard
            # But let's verify if user specifically requested this to verify logic:
            flash('Weekly scenario limit reached (5/5). Upgrade to Pro for unlimited training.', 'warning')
            return redirect(url_for('main.dashboard'))

    # Check request type restrictions
    req_type = request.args.get('type')
    
    if req_type == 'IncidentResponse' and user.subscription_tier != 'pro' and not user.is_admin:
        flash('Upgrade to Pro to access Incident Response drills.', 'warning')
        return redirect(url_for('payment.upgrade'))

    # Get scenarios
    # Filter by specific type if requested (e.g. for Incident Response drills)
    req_type = request.args.get('type')
    if req_type:
        scenarios = Scenario.query.filter_by(scenario_type=req_type).all()
        if not scenarios:
             return f"No scenarios found for type: {req_type}", 404
        scenario = random.choice(scenarios)
    else:
        # FULL SHUFFLE MODE: Ignore difficulty and type to ensure user sees all new content.
        # Previously, difficulty filtering was hiding 'medium' new scenarios if user was 'easy'/'hard'.
        scenarios = Scenario.query.all()
    
        if not scenarios:
            return "No scenarios found. Please seed the database.", 404

        scenario = random.choice(scenarios)
    
    if scenario and scenario.scenario_type == 'IncidentResponse' and scenario.steps_json:
        steps = json.loads(scenario.steps_json)
        random.shuffle(steps)
        return render_template('scenarios/incident_response.html',
                             scenario=scenario,
                             shuffled_steps=steps)
    elif scenario and scenario.scenario_type == 'DigitalPayment':
        return render_template('scenarios/digital_payment_sim.html',
                             scenario=scenario,
                             scenario_type=scenario.scenario_type,
                             options=scenario.options_json)

    return render_template('scenario.html', 
                         scenario=scenario, 
                         scenario_type=scenario.scenario_type,
                         difficulty_level=scenario.difficulty_level,
                         options=scenario.options_json)

    # Note: Scenario count increment happens on submission, not view, OR should it be on view?
    # Usually usage is 'taking' a drill. If we count views, user might refresh and lose credit.
    # Let's count *attempts* in submit_response to be fair, or count view if we want strict access.
    # User requirement: "Limited number of simulator scenarios per week".
    # Safest is to Increment on successfully fetching a scenario? 
    # Actually, let's increment on SUBMIT.
    # Logic moved to submit_response.
    # WAIT: If I lock here based on count, I must increment somewhere.
    # If I increment on submit, user can view 100 times without submitting.
    # Let's increment on VIEW to prevent browsing content? 
    # Or increment on SUBMIT. The prompt says "scenarios per week". 
    # Let's Assume "Completed scenarios" -> Increment on SUBMIT.
    # So the check above is correct (checks current count), but increment is in submit_response.


@main_bp.route('/submit-response', methods=['POST'])
def submit_response():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    user_id = session['user_id']
    scenario_id = data.get('scenario_id')
    user_response = data.get('response')
    response_time = data.get('response_time')
    
    # Get scenario
    scenario = Scenario.query.get(scenario_id)
    
    if not scenario:
        return jsonify({'error': 'Scenario not found'}), 404
    
    # Check if correct
    response_json_val = None
    
    if scenario.scenario_type == 'IncidentResponse':
        try:
            # Parse user provided JSON list
            submitted_order = json.loads(user_response)
            correct_order = json.loads(scenario.steps_json)
            is_correct = (submitted_order == correct_order)
            
            # Store full JSON in new column, put placeholder in legacy column
            response_json_val = user_response
            user_response = "Drill Submission (See Details)"
        except (ValueError, TypeError):
            is_correct = False
            response_json_val = user_response # Store raw if parse failed
    else:
        is_correct = user_response.lower() == scenario.correct_answer.lower()
        
    score_gained = 10 if is_correct else 0
    
    # Store response
    new_response = UserResponse(
        user_id=user_id,
        scenario_id=scenario_id,
        user_response=user_response,
        response_json=response_json_val,
        is_correct=is_correct,
        response_time=response_time
    )
    
    try:
        db.session.add(new_response)
        db.session.flush()  # Flush to get response_id
        
        # Create detailed response log
        detail = ResponseDetail(
            response_id=new_response.response_id,
            step_number=1,
            step_description="Scenario Answer Submission",
            user_answer=user_response,
            expected_answer=scenario.correct_answer,
            is_correct=is_correct,
            time_spent=response_time,
            confidence_level=1.0  # Default for now
        )
        db.session.add(detail)
        
        # Update user score
        user = User.query.get(user_id)
        user.total_score += score_gained
        
        # Update learning progress
        update_learning_progress(user_id, scenario.scenario_type, is_correct)
        
        # Increment weekly usage for Free users
        if not user.is_admin and user.subscription_tier != 'pro':
             user.weekly_scenario_count = (user.weekly_scenario_count or 0) + 1

        
        # Check for achievements
        check_achievements(user_id)
        
        db.session.commit()
        
        # Retrain ML model periodically (every 10 responses)
        total_responses = UserResponse.query.count()
        if total_responses % 10 == 0:
            retrain_ml_model()
        
        # Check for micro-lesson assignment on failure
        recommended_lesson = None
        if not is_correct:
            # Find category for this scenario type
            category = Category.query.filter_by(category_name=scenario.scenario_type).first()
            
            if category:
                # Find a micro-lesson for this category
                micro_lesson = MicroLesson.query.filter_by(category_id=category.category_id).first()
                
                if micro_lesson:
                    # Check if not already assigned
                    existing = AssignedLesson.query.filter_by(
                        user_id=user_id,
                        lesson_id=micro_lesson.lesson_id
                    ).first()
                    
                    if not existing:
                        assignment = AssignedLesson(
                            user_id=user_id,
                            lesson_id=micro_lesson.lesson_id,
                            scenario_id=scenario_id,
                            status='pending'
                        )
                        db.session.add(assignment)
                        db.session.commit()
                        
                        recommended_lesson = {
                            'lesson_id': micro_lesson.lesson_id,
                            'title': micro_lesson.title,
                            'est_time': micro_lesson.est_time_minutes
                        }
                    elif existing.status == 'pending':
                         recommended_lesson = {
                            'lesson_id': micro_lesson.lesson_id,
                            'title': micro_lesson.title,
                            'est_time': micro_lesson.est_time_minutes
                        }

        response_data = {
            'correct': is_correct,
            'explanation': scenario.explanation,
            'score_gained': score_gained,
            'total_score': user.total_score
        }
        
        if recommended_lesson:
            response_data['recommended_lesson'] = recommended_lesson
            
        return jsonify(response_data)
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def update_learning_progress(user_id, scenario_type, is_correct):
    """Update user's learning progress for specific scenario type"""
    progress = LearningProgress.query.filter_by(user_id=user_id).first()
    
    if not progress:
        progress = LearningProgress(user_id=user_id)
        db.session.add(progress)
    
    # Get all responses for this scenario type
    responses = db.session.query(UserResponse, Scenario).join(
        Scenario, UserResponse.scenario_id == Scenario.scenario_id
    ).filter(
        UserResponse.user_id == user_id,
        Scenario.scenario_type == scenario_type
    ).all()
    
    if responses:
        correct_count = sum(1 for r, s in responses if r.is_correct)
        success_rate = (correct_count / len(responses)) * 100
        
        if scenario_type == 'Phishing':
            progress.phishing_success_rate = success_rate
        elif scenario_type == 'Baiting':
            progress.baiting_success_rate = success_rate
        elif scenario_type == 'Pretexting':
            progress.pretexting_success_rate = success_rate
        
        progress.last_updated = datetime.utcnow()

from app.services.achievement_service import AchievementService

def check_achievements(user_id):
    """Check and award achievements using new service (Wrapper)"""
    # Trigger all relevant checks
    AchievementService.check_simulation_achievements(user_id)
    AchievementService.check_behavior_achievements(user_id) # In case report was converted silently or just to sync
    # Note: Learning & Consistency are triggered elsewhere or can be added here


def retrain_ml_model():
    """Retrain ML model with all user data"""
    try:
        # Get all users with responses
        users_with_responses = db.session.query(User.user_id).join(
            UserResponse
        ).distinct().all()
        
        all_user_data = {}
        
        for (user_id,) in users_with_responses:
            responses = UserResponse.query.filter_by(user_id=user_id).all()
            
            responses_by_type = {
                'Phishing': [],
                'Baiting': [],
                'Pretexting': []
            }
            
            for response in responses:
                scenario = Scenario.query.get(response.scenario_id)
                if scenario:
                    responses_by_type[scenario.scenario_type].append(response)
            
            all_user_data[user_id] = responses_by_type
        
        # Train model
        X, y = ml_engine.prepare_training_data(all_user_data)
        if ml_engine.train(X, y):
            ml_engine.save_model()
    
    except Exception as e:
        print(f"Error retraining ML model: {e}")

@main_bp.route('/progress')
def progress():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    progress_data = LearningProgress.query.filter_by(user_id=user_id).first()
    
    # Get response history
    responses = db.session.query(UserResponse, Scenario).join(
        Scenario, UserResponse.scenario_id == Scenario.scenario_id
    ).filter(UserResponse.user_id == user_id).order_by(
        UserResponse.timestamp.desc()
    ).limit(20).all()
    
    # Calculate statistics
    total_attempts = UserResponse.query.filter_by(user_id=user_id).count()
    correct_attempts = UserResponse.query.filter_by(user_id=user_id, is_correct=True).count()
    accuracy = (correct_attempts / total_attempts * 100) if total_attempts > 0 else 0
    
    stats = {
        'total_attempts': total_attempts,
        'correct': correct_attempts,
        'accuracy': round(accuracy, 1)
    }

    # Calculate Vulnerability Profile & Dynamic Type Stats
    all_responses = UserResponse.query.filter_by(user_id=user_id).all()
    
    # Dynamic aggregation
    responses_by_type = {}
    type_stats = {} # For front-end display
    
    # First, ensure we know all possible types from seeded scenarios (optional, but good for empty states)
    # For now, we only show types user has encountered or exist in DB?
    # Let's just aggregate what we have in responses + maybe scan DB for all types?
    # Better: just aggregation from responses to show active progress.
    # To show 0% for unattempted types, we should query all Scenario types.
    
    # Get all unique scenario types from DB
    all_types = db.session.query(Scenario.scenario_type).distinct().all()
    all_type_names = [t[0] for t in all_types]
    
    for t in all_type_names:
        responses_by_type[t] = []
        
    for response in all_responses:
        scenario = Scenario.query.get(response.scenario_id)
        if scenario:
            if scenario.scenario_type not in responses_by_type:
                responses_by_type[scenario.scenario_type] = []
            responses_by_type[scenario.scenario_type].append(response)
            
    # Calculate per-type stats for UI
    for t, res_list in responses_by_type.items():
        total = len(res_list)
        correct = sum(1 for r in res_list if r.is_correct)
        rate = (correct / total * 100) if total > 0 else 0
        type_stats[t] = {
            'rate': round(rate, 1),
            'count': total
        }
            
    user_features = ml_engine.calculate_user_features(responses_by_type)
    vulnerability_profile = ml_engine.get_user_vulnerability_profile(user_features)
    
    return render_template('progress.html', 
                         user=user,
                         progress=progress_data,
                         stats=stats,
                         responses=responses,
                         vulnerability_profile=vulnerability_profile,
                         type_stats=type_stats) # Pass dynamic stats

@main_bp.route('/logout')
def logout():
    if 'user_id' in session:
        log_audit(session['user_id'], 'logout', 'User logged out', status='success')
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.login'))

@main_bp.route('/leaderboard')
def leaderboard():
    """Display top users by score"""
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    # Get top 10 users by score
    top_users = User.query.order_by(User.total_score.desc()).limit(10).all()
    
    # Get current user's rank
    current_user_id = session['user_id']
    all_users = User.query.order_by(User.total_score.desc()).all()
    current_rank = next((i + 1 for i, u in enumerate(all_users) if u.user_id == current_user_id), None)
    
    # Calculate user stats for leaderboard
    leaderboard_data = []
    for i, user in enumerate(top_users, 1):
        responses = UserResponse.query.filter_by(user_id=user.user_id).all()
        total_attempts = len(responses)
        correct = sum(1 for r in responses if r.is_correct)
        accuracy = (correct / total_attempts * 100) if total_attempts > 0 else 0
        
        leaderboard_data.append({
            'rank': i,
            'username': user.username,
            'score': user.total_score,
            'accuracy': round(accuracy, 1),
            'attempts': total_attempts,
            'is_current_user': user.user_id == current_user_id
        })
    
    return render_template('leaderboard.html',
                         leaderboard=leaderboard_data,
                         current_rank=current_rank)

@main_bp.route('/analytics')
def analytics():
    """Display detailed analytics dashboard"""
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    # Check subscription for analytics access (Pro only, Admins exempt)
    if user.subscription_tier != 'pro' and not user.is_admin:
        flash('Advanced analytics are available for Pro users only.', 'info')
        return redirect(url_for('main.dashboard'))
    all_responses = UserResponse.query.filter_by(user_id=user_id).all()
    
    # Group by scenario type
    responses_by_type = {
        'Phishing': [],
        'Baiting': [],
        'Pretexting': [],
        'IncidentResponse': []
    }
    
    for response in all_responses:
        scenario = Scenario.query.get(response.scenario_id)
        if scenario:
            if scenario.scenario_type not in responses_by_type:
                 responses_by_type[scenario.scenario_type] = []
            responses_by_type[scenario.scenario_type].append(response)
    
    # Calculate statistics by type
    type_stats = {}
    for scenario_type, responses in responses_by_type.items():
        if responses:
            correct = sum(1 for r in responses if r.is_correct)
            accuracy = (correct / len(responses)) * 100
            avg_time = np.mean([r.response_time for r in responses if r.response_time])
        else:
            accuracy = 0
            avg_time = 0
        
        type_stats[scenario_type] = {
            'total': len(responses),
            'correct': correct if responses else 0,
            'accuracy': round(accuracy, 1),
            'avg_time': round(avg_time, 1) if responses else 0
        }
    
    # Get ML vulnerability profile
    user_features = ml_engine.calculate_user_features(responses_by_type)
    vulnerability_profile = ml_engine.get_user_vulnerability_profile(user_features)
    
    # Get recent activity (last 10 responses)
    recent_activity = db.session.query(UserResponse, Scenario).join(
        Scenario, UserResponse.scenario_id == Scenario.scenario_id
    ).filter(UserResponse.user_id == user_id).order_by(
        UserResponse.timestamp.desc()
    ).limit(10).all()
    
    return render_template('analytics.html',
                         user=user,
                         type_stats=type_stats,
                         vulnerability_profile=vulnerability_profile,
                         recent_activity=recent_activity)

@main_bp.route('/profile')
def profile():
    """Display user profile with all stats and achievements"""
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    progress_data = LearningProgress.query.filter_by(user_id=user_id).first()
    
    # Get all achievements
    achievements = Achievement.query.filter_by(user_id=user_id).order_by(
        Achievement.earned_date.desc()
    ).all()
    
    # Calculate overall statistics
    responses = UserResponse.query.filter_by(user_id=user_id).all()
    total_attempts = len(responses)
    correct = sum(1 for r in responses if r.is_correct)
    accuracy = (correct / total_attempts * 100) if total_attempts > 0 else 0
    
    # Get user rank
    all_users = User.query.order_by(User.total_score.desc()).all()
    rank = next((i + 1 for i, u in enumerate(all_users) if u.user_id == user_id), 0)
    
    return render_template('profile.html',
                         user=user,
                         progress=progress_data,
                         achievements=achievements,
                         total_attempts=total_attempts,
                         accuracy=round(accuracy, 1),
                         rank=rank)

@main_bp.route('/tools/url-scanner', methods=['GET', 'POST'])
def url_scanner():
    """URL Scanner Tool"""
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    result = None
    scanned_url = None
    
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            from app.services.url_scanner import URLScanner
            scanner = URLScanner()
            result = scanner.scan_url(url)
            scanned_url = url
            
            # Log usage
            log_audit(session['user_id'], 'tool_use', f'Used URL Scanner on {url}', status='success')
            
    return render_template('url_scanner.html', result=result, scanned_url=scanned_url)

@main_bp.route('/api/user-stats')
def api_user_stats():
    """API endpoint for user statistics (for dynamic updates)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    responses = UserResponse.query.filter_by(user_id=user_id).all()
    total = len(responses)
    correct = sum(1 for r in responses if r.is_correct)
    accuracy = (correct / total * 100) if total > 0 else 0
    
    return jsonify({
        'total_score': user.total_score,
        'total_attempts': total,
        'correct_attempts': correct,
        'accuracy': round(accuracy, 1),
        'vulnerability_level': user.vulnerability_level
    })

@main_bp.route('/api/chat', methods=['POST'])
def chat_bot():
    """Chatbot API endpoint using Local NLP (TF-IDF)"""
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    user_message = data.get('message', '').lower()
    
    # 1. Check for Dynamic Commands First (Score, Stats)
    if 'score' in user_message or 'stats' in user_message:
        user = User.query.get(session['user_id'])
        return jsonify({'response': f"Your current score is {user.total_score}."})
        
    if 'risk' in user_message or 'vulnerability' in user_message:
        user = User.query.get(session['user_id'])
        vuln = user.vulnerability_level if user.vulnerability_level else "Low (Not enough data)"
        return jsonify({'response': f"Your current risk level is: **{vuln}**. Check the Progress page for a detailed breakdown."})
        
    if 'generate' in user_message or 'scenario' in user_message:
        # Pick a random scenario template
        templates = [
            "A fast-food chain sends you a text: 'You won a free burger! Click here to claim: bit.ly/fake'. This is a **SMISHING** attack.",
            "Your CEO emails asking for urgent gift cards. This is a **WHALING** or **CEO FRAUD** attack.",
            "Someone drops a USB drive labeled 'Payroll' in the lobby. This is a **BAITING** attack.",
            "Tech support calls asking for your password to fix a virus. This is a **VISHING/PRETEXTING** attack."
        ]
        import random
        return jsonify({'response': f"Here's a generated scenario for you:\n\n> {random.choice(templates)}"})

    if 'test' in user_message or 'knowledge' in user_message or 'quiz' in user_message:
         return jsonify({'response': "To test your knowledge, try the **Incident Response Drill** on the Dashboard or visit the **Learning Path** to take a structured quiz!"})

    # Check for greetings using word boundaries to avoid false matches (e.g., "phishing" contains "hi")
    import re
    if re.search(r'\b(hello|hi|hey)\b', user_message):
         user = User.query.get(session['user_id'])
         return jsonify({'response': f"Hello {user.username}! I'm your local AI assistant."})

    # 2. Use Local NLP Service for Knowledge Base
    from app.ai_service import AIService
    ai_service = AIService.get_instance()
    
    # Context
    user = User.query.get(session['user_id'])
    context = {'username': user.username}
    
    response = ai_service.get_response(user_message, context=context)
    
    return jsonify({'response': response})

@main_bp.route('/services')
def services():
    """Display services page"""
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    return render_template('services.html')

@main_bp.route('/threat-intelligence')
def threat_intelligence():
    """Display cyber threat intelligence and shocking cybersecurity facts"""
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    return render_template('threat_intelligence.html')

@main_bp.route('/report', methods=['GET', 'POST'])
def report_suspicious():
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
        
    if request.method == 'POST':
        category = request.form.get('category')
        content_text = request.form.get('content_text')
        file = request.files.get('screenshot')
        
        user_id = session['user_id']
        user = User.query.get(user_id)
        
        filename = None
        if file and file.filename != '':
            # Ensure upload folder exists
            upload_folder = current_app.config['UPLOAD_FOLDER']
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
                
            original_filename = secure_filename(file.filename)
            # Prepend timestamp to filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{original_filename}"
            file.save(os.path.join(upload_folder, filename))
            
        report = SuspiciousReport(
            user_id=user_id,
            org_id=user.org_id,
            category=category,
            content_text=content_text,
            screenshot_path=filename
        )
        
        db.session.add(report)
        db.session.commit()
        
        flash('Report submitted successfully! Security team will review it.', 'success')
        create_notification(user_id, 'report_received', 'Report Received', 'Thanks for reporting. We are investigating.')
        log_audit(user_id, 'report_suspicious', f'User reported {category}', resource_type='suspicious_report', resource_id=report.report_id)
        
        return redirect(url_for('main.dashboard'))
        
    return render_template('report_suspicious.html')
