"""
Database migration: Restructure to Topic → DifficultyLevel → Module hierarchy
Creates topics and difficulty levels for the new hierarchical structure
"""
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from app import create_app, db
from app.models import Topic, DifficultyLevel, LearningModule, PathLevel
from sqlalchemy import text

app = create_app()
app.app_context().push()

print("=" * 80)
print("DATABASE MIGRATION: Restructure to Topic-Level Hierarchy")
print("=" * 80)

# Step 1: Create tables if they don't exist
print("\n[1/5] Creating new tables...")
db.create_all()
print("✓ Tables created")

# Step 2: Create 5 topics
print("\n[2/5] Creating topics...")
topics_data = [
    {'number': 1, 'name': 'Phishing & Variations', 'description': 'Learn about phishing attacks, email scams, and social manipulation techniques.', 'icon': '🎣'},
    {'number': 2, 'name': 'Passwords', 'description': 'Password security, authentication best practices, and credential management.', 'icon': '🔐'},
    {'number': 3, 'name': 'Cloud Security', 'description': 'Securing cloud services, data protection, and cloud-based threats.', 'icon': '☁️'},
    {'number': 4, 'name': 'Ransomware', 'description': 'Understanding ransomware attacks, prevention, and response strategies.', 'icon': '🔒'},
    {'number': 5, 'name': 'Deepfakes', 'description': 'AI-generated deepfakes, manipulation detection, and digital forensics.', 'icon': '🎭'},
]

topics = []
for topic_data in topics_data:
    existing = Topic.query.filter_by(topic_number=topic_data['number']).first()
    if existing:
        print(f"  - Topic {topic_data['number']}: {topic_data['name']} (already exists)")
        topics.append(existing)
    else:
        topic = Topic(
            topic_number=topic_data['number'],
            topic_name=topic_data['name'],
            description=topic_data['description'],
            icon=topic_data['icon']
        )
        db.session.add(topic)
        topics.append(topic)
        print(f"  + Created Topic {topic_data['number']}: {topic_data['name']}")

db.session.commit()
print(f"✓ {len(topics)} topics ready")

# Step 3: Create 4 difficulty levels for each topic (20 total)
print("\n[3/5] Creating difficulty levels...")
difficulty_names = [
    ('Fundamentals', 'Basic concepts and awareness'),
    ('Intermediate', 'Pattern recognition and common attacks'),
    ('Advanced', 'Decision making under pressure'),
    ('Expert', 'Prevention strategies and incident response')
]

level_count = 0
difficulty_levels_map = {}  # Map (topic_id, level_num) -> difficulty_level_id

for topic in topics:
    previous_level_id = None
    for level_num, (level_name, level_desc) in enumerate(difficulty_names, 1):
        existing = DifficultyLevel.query.filter_by(
            topic_id=topic.topic_id,
            level_number=level_num
        ).first()
        
        if existing:
            print(f"  - {topic.topic_name} → {level_name} (already exists)")
            difficulty_levels_map[(topic.topic_id, level_num)] = existing.difficulty_level_id
            previous_level_id = existing.difficulty_level_id
        else:
            level = DifficultyLevel(
                topic_id=topic.topic_id,
                level_number=level_num,
                level_name=level_name,
                description=level_desc,
                previous_level_id=previous_level_id
            )
            db.session.add(level)
            db.session.flush()  # Get the ID
            difficulty_levels_map[(topic.topic_id, level_num)] = level.difficulty_level_id
            previous_level_id = level.difficulty_level_id
            level_count += 1
            print(f"  + Created {topic.topic_name} → {level_name}")

db.session.commit()
print(f"✓ Created {level_count} new difficulty levels (Total: {DifficultyLevel.query.count()})")

# Step 4: Migrate existing modules to difficulty levels
print("\n[4/5] Migrating existing modules to new structure...")
# Get old path levels (which are now topics)
old_levels = PathLevel.query.order_by(PathLevel.level_number).all()

# Mapping of old level to new topic
# Level 1 (Phishing & Variations) → Topic 1
# Level 2 (Passwords) → Topic 2
# etc.
topic_mapping = {
    1: 1,  # Old level 1 → Topic 1 (Phishing)
    2: 2,  # Old level 2 → Topic 2 (Passwords)
    3: 3,  # Old level 3 → Topic 3 (Cloud Security)
    4: 4,  # Old level 4 → Topic 4 (Ransomware)
}

migrated_count = 0
for old_level in old_levels:
    if old_level.level_number not in topic_mapping:
        continue
    
    topic_num = topic_mapping[old_level.level_number]
    topic = Topic.query.filter_by(topic_number=topic_num).first()
    
    if not topic:
        continue
    
    # Get modules from old level
    modules = LearningModule.query.filter_by(level_id=old_level.level_id).all()
    
    if modules:
        # Put all existing modules in "Fundamentals" (level 1) of the new topic
        fundamentals_level = DifficultyLevel.query.filter_by(
            topic_id=topic.topic_id,
            level_number=1
        ).first()
        
        if fundamentals_level:
            for module in modules:
                if not module.difficulty_level_id:
                    module.difficulty_level_id = fundamentals_level.difficulty_level_id
                    migrated_count += 1
            print(f"  ✓ Migrated {len(modules)} modules from '{old_level.level_name}' to '{topic.topic_name} → Fundamentals'")

db.session.commit()
print(f"✓ Migrated {migrated_count} modules")

# Step 5: Update user progress records
print("\n[5/5] Updating user progress records...")
# Use raw SQL to avoid ORM issues
db.session.execute(text("""
    UPDATE user_progress up
    JOIN learning_modules lm ON up.module_id = lm.module_id
    SET 
        up.difficulty_level_id = lm.difficulty_level_id,
        up.topic_id = (
            SELECT dl.topic_id 
            FROM difficulty_levels dl 
            WHERE dl.difficulty_level_id = lm.difficulty_level_id
        )
    WHERE lm.difficulty_level_id IS NOT NULL
      AND up.difficulty_level_id IS NULL
"""))
db.session.commit()

updated_progress = db.session.execute(text("""
    SELECT COUNT(*) as count 
    FROM user_progress 
    WHERE difficulty_level_id IS NOT NULL
""")).fetchone()

print(f"✓ Updated {updated_progress[0] if updated_progress else 0} user progress records")

# Final summary
print("\n" + "=" * 80)
print("MIGRATION COMPLETE!")
print("=" * 80)
print(f"Topics: {Topic.query.count()}")
print(f"Difficulty Levels: {DifficultyLevel.query.count()}")
print(f"Modules: {LearningModule.query.filter(LearningModule.difficulty_level_id.isnot(None)).count()}")
print("\n✓ Database restructure complete!\n")

# Display structure
print("New Structure:")
print("-" * 80)
for topic in Topic.query.order_by(Topic.topic_number).all():
    print(f"\n📚 Topic {topic.topic_number}: {topic.topic_name}")
    for level in topic.difficulty_levels:
        module_count = len(level.modules)
        lock_status = "🔓" if level.level_number == 1 else "🔒"
        print(f"  {lock_status} Level {level.level_number}: {level.level_name} ({module_count} modules)")
