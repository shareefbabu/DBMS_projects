import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def seed_achievements():
    db_config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'database': os.getenv('MYSQL_DB', 'social_engineering_db'),
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }

    achievements = [
        # Learning Milestones
        {
            'slug': 'phishing_fundamentals',
            'name': 'Phishing Fundamentals',
            'description': 'Complete Fundamentals level of Phishing topic.',
            'category': 'Learning',
            'tier': 'Bronze',
            'icon': 'fa-fish',
            'condition_description': 'Complete Phishing Fundamentals level',
            'target_value': 1,
            'is_org_only': False
        },
        {
            'slug': 'multi_topic_learner',
            'name': 'Multi-Topic Learner',
            'description': 'Complete Fundamentals in 3 different topics.',
            'category': 'Learning',
            'tier': 'Silver',
            'icon': 'fa-book-open',
            'condition_description': 'Complete Fundamentals in 3 topics',
            'target_value': 3,
            'is_org_only': False
        },
        {
            'slug': 'path_finisher',
            'name': 'Path Finisher',
            'description': 'Complete all levels of one learning path (e.g., Social Engineering Mastery).',
            'category': 'Learning',
            'tier': 'Gold',
            'icon': 'fa-graduation-cap',
            'condition_description': 'Complete a full Learning Path',
            'target_value': 1,
            'is_org_only': False
        },
        {
            'slug': 'cloud_aware',
            'name': 'Cloud Aware',
            'description': 'Complete any Cloud Security module.',
            'category': 'Learning',
            'tier': 'Bronze',
            'icon': 'fa-cloud',
            'condition_description': 'Complete a Cloud Security module',
            'target_value': 1,
            'is_org_only': False
        },
        
        # Simulation Performance
        {
            'slug': 'first_line_defense',
            'name': 'First Line of Defense',
            'description': 'Pass your first simulation.',
            'category': 'Simulation',
            'tier': 'Bronze',
            'icon': 'fa-shield-alt',
            'condition_description': 'Pass 1 simulation',
            'target_value': 1,
            'is_org_only': False
        },
        {
            'slug': 'sharp_eye',
            'name': 'Sharp Eye',
            'description': 'Maintain ≥80% accuracy over last 20 simulations.',
            'category': 'Simulation',
            'tier': 'Silver',
            'icon': 'fa-eye',
            'condition_description': '≥80% accuracy (last 20 scenarios)',
            'target_value': 20,
            'is_org_only': False
        },
        {
            'slug': 'category_specialist_phishing',
            'name': 'Category Specialist – Phishing',
            'description': '90%+ accuracy in phishing scenarios (min 15 attempts).',
            'category': 'Simulation',
            'tier': 'Gold',
            'icon': 'fa-trophy',
            'condition_description': '≥90% phishing accuracy (min 15)',
            'target_value': 15,
            'is_org_only': False
        },
        {
            'slug': 'no_click_month',
            'name': 'No Click Month',
            'description': 'Zero failed simulations over 30 days.',
            'category': 'Simulation',
            'tier': 'Platinum', # Or Gold? Prompt says Bronze/Silver/Gold.
            'icon': 'fa-calendar-check',
            'condition_description': 'No fails for 30 days',
            'target_value': 30,
            'is_org_only': False
        },
        
        # Behavior
        {
            'slug': 'security_reporter',
            'name': 'Security Reporter',
            'description': 'Report your first real suspicious email/message via “Report Phishing”.',
            'category': 'Behavior',
            'tier': 'Bronze',
            'icon': 'fa-bullhorn',
            'condition_description': 'Report 1 suspicious item',
            'target_value': 1,
            'is_org_only': False
        },
        {
            'slug': 'human_ids',
            'name': 'Human IDS',
            'description': '5+ correct reports of real malicious items.',
            'category': 'Behavior',
            'tier': 'Silver',
            'icon': 'fa-user-secret',
            'condition_description': '5 valid reports',
            'target_value': 5,
            'is_org_only': False
        },
        {
            'slug': 'hygiene_champion',
            'name': 'Hygiene Champion',
            'description': 'Complete security hygiene checklist.',
            'category': 'Behavior',
            'tier': 'Silver',
            'icon': 'fa-clipboard-check',
            'condition_description': 'Complete hygiene checklist',
            'target_value': 1, # Represents 100% completion
            'is_org_only': False
        },
        {
            'slug': 'incident_ready',
            'name': 'Incident Ready',
            'description': 'Successfully complete an incident-response drill with full ordering score.',
            'category': 'Behavior',
            'tier': 'Gold',
            'icon': 'fa-fire-extinguisher',
            'condition_description': 'Perfect incident drill',
            'target_value': 1,
            'is_org_only': False
        },
        
        # Consistency
        {
            'slug': '7_day_streak',
            'name': '7-Day Streak',
            'description': 'Log in and complete at least one activity 7 days in a row.',
            'category': 'Consistency',
            'tier': 'Silver',
            'icon': 'fa-fire',
            'condition_description': '7 day activity streak',
            'target_value': 7,
            'is_org_only': False
        },
        {
            'slug': 'monthly_commitment',
            'name': 'Monthly Commitment',
            'description': 'Complete at least 10 simulations + 2 modules in a calendar month.',
            'category': 'Consistency',
            'tier': 'Gold',
            'icon': 'fa-calendar-alt',
            'condition_description': '10 sims + 2 modules in month',
            'target_value': 12, # Just a target rep
            'is_org_only': False
        },
        {
            'slug': 'team_anchor',
            'name': 'Team Anchor',
            'description': 'Top performer in your department for a given month.',
            'category': 'Consistency',
            'tier': 'Gold',
            'icon': 'fa-anchor',
            'condition_description': 'Top dept performer',
            'target_value': 1,
            'is_org_only': True
        },
        {
            'slug': 'early_adopter',
            'name': 'Early Adopter',
            'description': 'Created an account within first X days of organization onboarding.',
            'category': 'Consistency',
            'tier': 'Bronze',
            'icon': 'fa-rocket',
            'condition_description': 'Early account creation',
            'target_value': 1,
            'is_org_only': True
        }
    ]

    try:
        conn = pymysql.connect(**db_config)
        with conn.cursor() as cursor:
            print(f"Seeding {len(achievements)} achievements...")
            
            for ach in achievements:
                # Check if exists
                cursor.execute("SELECT definition_id FROM achievement_definitions WHERE slug = %s", (ach['slug'],))
                existing = cursor.fetchone()
                
                if existing:
                    print(f"Updating {ach['name']}...")
                    cursor.execute("""
                        UPDATE achievement_definitions 
                        SET name=%s, description=%s, category=%s, tier=%s, icon=%s, condition_description=%s, target_value=%s, is_org_only=%s
                        WHERE slug=%s
                    """, (
                        ach['name'], ach['description'], ach['category'], ach['tier'], ach['icon'], 
                        ach['condition_description'], ach['target_value'], ach['is_org_only'], 
                        ach['slug']
                    ))
                else:
                    print(f"Creating {ach['name']}...")
                    cursor.execute("""
                        INSERT INTO achievement_definitions 
                        (slug, name, description, category, tier, icon, condition_description, target_value, is_org_only)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        ach['slug'], ach['name'], ach['description'], ach['category'], ach['tier'], ach['icon'],
                        ach['condition_description'], ach['target_value'], ach['is_org_only']
                    ))
            
        conn.commit()
        print("Achievements seeded successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    seed_achievements()
