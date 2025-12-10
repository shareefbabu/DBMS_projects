"""
Database migration: Add Topics 6, 7, 8
"""
import sys
import os

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from app import create_app, db
from app.models import Topic, DifficultyLevel

app = create_app()
app.app_context().push()

print("=" * 80)
print("DATABASE UPDATE: Adding Topics 6, 7, 8")
print("=" * 80)

# Step 1: Define new topics
print("\n[1/3] Defining new topics...")
new_topics_data = [
    {
        'number': 6, 
        'name': 'Human Factors & Social Engineering Basics', 
        'description': 'Understanding psychology, manipulation techniques, and human vulnerabilities.', 
        'icon': '🧠'
    },
    {
        'number': 7, 
        'name': 'Secure Browsing & Malware', 
        'description': 'Safe surfing habits, recognizing malicious downloads, and browser security.', 
        'icon': '🛡️'
    },
    {
        'number': 8, 
        'name': 'Public Wi‑Fi & Device Safety', 
        'description': 'Risks of public networks, VPN usage, and physical device security.', 
        'icon': '📶'
    },
]

added_topics = []
for topic_data in new_topics_data:
    existing = Topic.query.filter_by(topic_number=topic_data['number']).first()
    if existing:
        print(f"  - Topic {topic_data['number']}: {topic_data['name']} (already exists)")
        added_topics.append(existing)
    else:
        topic = Topic(
            topic_number=topic_data['number'],
            topic_name=topic_data['name'],
            description=topic_data['description'],
            icon=topic_data['icon']
        )
        db.session.add(topic)
        added_topics.append(topic)
        print(f"  + Created Topic {topic_data['number']}: {topic_data['name']}")

db.session.commit()
print(f"✓ {len(added_topics)} topics processed")

# Step 2: Create difficulty levels for new topics
print("\n[2/3] Creating difficulty levels...")
difficulty_names = [
    ('Fundamentals', 'Basic concepts and awareness'),
    ('Intermediate', 'Pattern recognition and common attacks'),
    ('Advanced', 'Decision making under pressure'),
    ('Expert', 'Prevention strategies and incident response')
]

level_count = 0

for topic in added_topics:
    # Only process if this topic was just added or we want to ensure levels exist
    # (Checking all just in case)
    previous_level_id = None
    for level_num, (level_name, level_desc) in enumerate(difficulty_names, 1):
        existing = DifficultyLevel.query.filter_by(
            topic_id=topic.topic_id,
            level_number=level_num
        ).first()
        
        if existing:
            # print(f"  - {topic.topic_name} → {level_name} (already exists)")
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
            db.session.flush()  # Get ID
            previous_level_id = level.difficulty_level_id
            level_count += 1
            print(f"  + Created {topic.topic_name} → {level_name}")

db.session.commit()
print(f"✓ Created {level_count} new difficulty levels")

# Step 3: Summary
print("\n" + "=" * 80)
print("UPDATE COMPLETE!")
print(f"Total Topics: {Topic.query.count()}")
print(f"Total Difficulty Levels: {DifficultyLevel.query.count()}")
print("=" * 80)
