"""
Script to update level names from generic names to specific security topics
Run this in the Flask application context
"""
from app import db
from app.models import PathLevel

# Update level names to topics
updates = {
    1: {
        'name': 'Phishing & Variations',
        'description': 'Learn about phishing attacks, email scams, and social manipulation techniques.'
    },
    2: {
        'name': 'Passwords',
        'description': 'Password security, authentication best practices, and credential management.'
    },
    3: {
        'name': 'Cloud Security',
        'description': 'Securing cloud services, data protection, and cloud-based threats.'
    },
    4: {
        'name': 'Ransomware',
        'description': 'Understanding ransomware attacks, prevention, and response strategies.'
    },
    5: {
        'name': 'Deepfakes',
        'description': 'AI-generated deepfakes, manipulation detection, and digital forensics.'
    }
}

print("Updating level names to topics...")
updated_count = 0

for level_num, data in updates.items():
    level = PathLevel.query.filter_by(level_number=level_num).first()
    if level:
        level.level_name = data['name']
        level.description = data['description']
        print(f"✓ Updated Level {level_num}: {data['name']}")
        updated_count += 1
    else:
        print(f"✗ Level {level_num} not found")

db.session.commit()
print(f"\n✓ Successfully updated {updated_count} levels!")

# Verify updates
print("\nCurrent level names:")
levels = PathLevel.query.order_by(PathLevel.level_number).all()
for level in levels:
    print(f"  Topic {level.level_number}: {level.level_name}")
