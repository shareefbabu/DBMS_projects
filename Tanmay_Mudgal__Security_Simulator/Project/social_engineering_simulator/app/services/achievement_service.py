from app import db
from app.models import User, Achievement, AchievementDefinition, UserResponse, UserProgress, SuspiciousReport, AuditLog, Scenario, LearningModule, Topic, DifficultyLevel
from sqlalchemy import func
from datetime import datetime, timedelta

class AchievementService:
    @staticmethod
    def get_or_create_user_achievement(user_id, slug):
        definition = AchievementDefinition.query.filter_by(slug=slug).first()
        if not definition:
            return None, None

        user_ach = Achievement.query.filter_by(user_id=user_id, definition_id=definition.definition_id).first()
        
        if not user_ach:
            user_ach = Achievement(
                user_id=user_id,
                definition_id=definition.definition_id,
                achievement_name=definition.name,
                criteria_met=definition.description,
                status='Locked', # Default to Locked until progress starts? Or In Progress
                current_value=0
            )
            db.session.add(user_ach)
            # Commit immediately to get ID? No, session management is better
        
        return user_ach, definition

    @staticmethod
    def award_achievement(user_id, slug, current_val=None, force_complete=False):
        user_ach, definition = AchievementService.get_or_create_user_achievement(user_id, slug)
        if not user_ach:
            return

        if user_ach.status == 'Earned':
            return

        # Update status to In Progress if it has value
        if user_ach.status == 'Locked' and (current_val is not None and current_val > 0):
             user_ach.status = 'In Progress'

        if current_val is not None:
            user_ach.current_value = current_val

        # Check completion
        is_completed = force_complete
        if not is_completed and definition.target_value and user_ach.current_value >= definition.target_value:
             is_completed = True
        
        if is_completed:
            user_ach.status = 'Earned'
            user_ach.earned_date = datetime.utcnow()
            user_ach.current_value = definition.target_value # Cap it?
            
            # Send notification
            from app.utils import create_notification
            create_notification(
                user_id=user_id,
                type_name='achievement_earned',
                title='Achievement Unlocked!',
                message=f"You earned the '{definition.name}' badge!",
                priority='high',
                action_url='/badges' # simplified url
            )

        db.session.commit()

    @staticmethod
    def check_learning_achievements(user_id):
        # 1. Phishing Fundamentals
        # Find Phishing topic -> Fundamentals level
        # Assuming Topic 1 is Phishing (seeded) or search by name
        # We need to find Modules in 'Fundamentals' level of 'Phishing' category/topic
        
        # Helper to check level completion
        def check_topic_level(topic_name, level_name):
            # Complex join
            # This relies on correct seeding of Topic/Level names which we might not have guaranteed
            # Let's rely on 'Category' model for topics as per schema? 
            # Schema has 'categories' (Phishing, etc) and 'learning_modules' linking to them.
            # And 'path_levels' (Fundamentals).
            
            # Count modules in this category & level
            total_query = db.session.query(func.count(LearningModule.module_id))\
                .join(Category)\
                .filter(Category.category_name == topic_name)
                
            # Need to filter by Level 'Fundamentals'. 
            # 'learning_modules' links to 'path_levels' via level_id
            # 'path_levels' has level_name='Fundamentals'
            
            # Assuming standard naming
            total = total_query.join(LearningModule.level).filter(DifficultyLevel.level_name == level_name).scalar()
            
            if not total: 
                # Fallback to old schema path_levels?
                # The schema in models.py shows LearningModule links to PathLevel (level_id) AND DifficultyLevel (difficulty_level_id).
                # New structure uses DifficultyLevel.
                from app.models import PathLevel
                total = db.session.query(func.count(LearningModule.module_id))\
                    .join(Category).filter(Category.category_name == topic_name)\
                    .join(PathLevel, LearningModule.level_id == PathLevel.level_id).filter(PathLevel.level_name == level_name).scalar()
                
            if not total: return False # No modules found

            # Count completed
            # Join UserProgress
            completed = db.session.query(func.count(UserProgress.progress_id))\
                .join(LearningModule, UserProgress.module_id == LearningModule.module_id)\
                .join(Category, LearningModule.category_id == Category.category_id)\
                .join(PathLevel, LearningModule.level_id == PathLevel.level_id)\
                .filter(UserProgress.user_id == user_id, 
                        UserProgress.status == 'completed',
                        Category.category_name == topic_name,
                        PathLevel.level_name == level_name).scalar()
                        
            return completed >= total
            
        if check_topic_level('Phishing', 'Fundamentals'):
            AchievementService.award_achievement(user_id, 'phishing_fundamentals', 1)

        # 2. Multi-Topic Learner (Fundamentals in 3 topics)
        # Iterate all categories?
        categories = db.session.query(Category.category_name).all()
        fundamentals_completed = 0
        for cat in categories:
            if check_topic_level(cat[0], 'Fundamentals'):
                fundamentals_completed += 1
        
        AchievementService.award_achievement(user_id, 'multi_topic_learner', fundamentals_completed)
        
        # 3. Path Finisher (All levels of a path)
        # Check 'Social Engineering Mastery' Path
        # Simple check: Are there any modules in this path NOT completed?
        # Get all modules for Path 1
        path_modules = db.session.query(LearningModule)\
            .join(PathLevel)\
            .filter(PathLevel.path_id == 1).all() # Assuming path_id 1
            
        if path_modules:
            completed_ids = [p.module_id for p in UserProgress.query.filter_by(user_id=user_id, status='completed').all()]
            all_done = all(m.module_id in completed_ids for m in path_modules)
            if all_done:
                 AchievementService.award_achievement(user_id, 'path_finisher', 1)

        # 4. Cloud Aware
        # Check for module with 'Cloud' in title
        cloud_modules = LearningModule.query.filter(LearningModule.title.ilike('%Cloud%')).all()
        cloud_done = 0
        for m in cloud_modules:
            prog = UserProgress.query.filter_by(user_id=user_id, module_id=m.module_id, status='completed').first()
            if prog:
                cloud_done = 1
                break
        
        if cloud_done:
            AchievementService.award_achievement(user_id, 'cloud_aware', 1)

    @staticmethod
    def check_simulation_achievements(user_id):
        # 1. First Line of Defense
        responses = UserResponse.query.filter_by(user_id=user_id).all()
        correct_count = sum(1 for r in responses if r.is_correct)
        if correct_count >= 1:
            AchievementService.award_achievement(user_id, 'first_line_defense', 1)

        # 2. Sharp Eye (>80% accuracy last 20)
        last_20 = UserResponse.query.filter_by(user_id=user_id).order_by(UserResponse.timestamp.desc()).limit(20).all()
        # Only start tracking if we have enough data? Prompt says "maintain... over last 20". Implying moving window.
        # If I have 5 responses and all correct, is that 100%? 
        # Usually "over last 20" implies a full window. I'll require at least 10? Or just calculate on what we have? 
        # Condition says "last 20". Let's assume min 5 to avoid instant noise.
        if len(last_20) >= 5:
             acc = sum(1 for r in last_20 if r.is_correct) / len(last_20)
             if acc >= 0.8:
                 AchievementService.award_achievement(user_id, 'sharp_eye', 20) # Max
             else:
                 # Calculate "items in window meeting criteria"? No, it's a binary state.
                 # Progress could be current accuracy * 10 or something.
                 AchievementService.award_achievement(user_id, 'sharp_eye', int(acc * 20))
        
        # 3. Category Specialist - Phishing
        phishing_responses = db.session.query(UserResponse)\
            .join(Scenario)\
            .filter(UserResponse.user_id == user_id, Scenario.scenario_type == 'Phishing').all()
            
        count = len(phishing_responses)
        correct = sum(1 for r in phishing_responses if r.is_correct)
        
        if count >= 15:
            acc = correct / count
            if acc >= 0.9:
                AchievementService.award_achievement(user_id, 'category_specialist_phishing', 15)
            else:
                 # Show progress as count towards 15? Or accuracy?
                 # Prompt says "min 15 attempts".
                 AchievementService.award_achievement(user_id, 'category_specialist_phishing', count) # Progress is count
        else:
            AchievementService.award_achievement(user_id, 'category_specialist_phishing', count)

        # 4. No Click Month
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_fails = UserResponse.query.filter(UserResponse.user_id==user_id, UserResponse.is_correct==False, UserResponse.timestamp >= thirty_days_ago).count()
        
        # We need to verify if user was even active. If no activity, "No Click Month" is trivial? 
        # Prompt: "zero failed simulations over 30 days."
        # Usually requires some activity. I'll require at least 1 attempt.
        recent_activity = UserResponse.query.filter(UserResponse.user_id==user_id, UserResponse.timestamp >= thirty_days_ago).count()
        
        if recent_activity > 0 and recent_fails == 0:
             AchievementService.award_achievement(user_id, 'no_click_month', 30)
        else:
             AchievementService.award_achievement(user_id, 'no_click_month', 0)

    @staticmethod
    def check_behavior_achievements(user_id):
        # 1. Security Reporter
        # Check SuspiciousReport table if it exists
        try:
            report_count = SuspiciousReport.query.filter_by(user_id=user_id).count()
            AchievementService.award_achievement(user_id, 'security_reporter', report_count)
            
            # 2. Human IDS (5 correct/approved reports)
            ids_count = SuspiciousReport.query.filter_by(user_id=user_id, status='Approved').count()
            # Also check 'Converted' status as that implies approval
            converted_count = SuspiciousReport.query.filter_by(user_id=user_id, status='Converted').count()
            total_valid = ids_count + converted_count
            AchievementService.award_achievement(user_id, 'human_ids', total_valid)
            
        except NameError:
            pass # Table might not exist or verify import

        # 3. Hygiene Champion -> Manual or linked to a specific module
        # Placeholder: Award if 'Security Hygiene' module is done (if it existed)
        
        # 4. Incident Ready (Incident Response Drill)
        # Check responses for IncidentResponse type
        ir_responses = db.session.query(UserResponse)\
            .join(Scenario)\
            .filter(UserResponse.user_id == user_id, Scenario.scenario_type == 'IncidentResponse', UserResponse.is_correct == True).count()
            
        if ir_responses >= 1:
            AchievementService.award_achievement(user_id, 'incident_ready', 1)

    @staticmethod
    def check_consistency_achievements(user_id):
        # 1. 7-Day Streak
        # Check audit logs for 'login'
        today = datetime.utcnow().date()
        streak = 0
        for i in range(7):
            d = today - timedelta(days=i)
            # Check if login existed on this day
            # Need strict query:
            # AuditLog.timestamp between d 00:00 and d 23:59
            start = datetime.combine(d, datetime.min.time())
            end = datetime.combine(d, datetime.max.time())
            log = AuditLog.query.filter(
                AuditLog.user_id == user_id, 
                AuditLog.action_type == 'login',
                AuditLog.timestamp >= start,
                AuditLog.timestamp <= end
            ).first()
            
            if log:
                streak += 1
            else:
                if i == 0: continue # If today not yet logged? well we are calling this ON login usually.
                # If missed a day, streak broken
                break
        
        AchievementService.award_achievement(user_id, '7_day_streak', streak)

        # 2. Monthly Commitment
        # 10 sims + 2 modules in current MONTH
        now = datetime.utcnow()
        start_month = datetime(now.year, now.month, 1)
        
        sims_month = UserResponse.query.filter(UserResponse.user_id == user_id, UserResponse.timestamp >= start_month).count()
        
        modules_month = UserProgress.query.filter(
            UserProgress.user_id == user_id, 
            UserProgress.status == 'completed',
            UserProgress.completed_at >= start_month
        ).count()
        
        # How to represent combined progress? 
        # Target is 12 (10+2). 
        # We can sum them, but capped at 10 and 2? 
        # Let's simple sum: sims + modules.
        # But we must ensure 10 sims and 2 modules specifically.
        
        if sims_month >= 10 and modules_month >= 2:
            AchievementService.award_achievement(user_id, 'monthly_commitment', 12)
        else:
            # Show aggregate progress? 
            total_prog = min(sims_month, 10) + min(modules_month, 2)
            AchievementService.award_achievement(user_id, 'monthly_commitment', total_prog)
            
        # 3. Early Adopter
        # Check user creation vs org creation
        user = User.query.get(user_id)
        if user and user.org_id:
            from app.models import Organization
            org = Organization.query.get(user.org_id)
            if org:
                delta = user.created_date - org.created_at
                if delta.days <= 14: # 2 weeks
                     AchievementService.award_achievement(user_id, 'early_adopter', 1)

