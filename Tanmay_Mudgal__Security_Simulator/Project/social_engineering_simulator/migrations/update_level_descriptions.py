"""
Migration: Update Difficulty Level Descriptions for all Topics
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
print("DATABASE UPDATE: Updating Level Descriptions")
print("=" * 80)

# Data Mapping
# Topic Name -> { Level Name -> New Description }
updates = {
    "Phishing & Variations": {
        "Fundamentals": "Basic concepts and awareness",
        "Intermediate": "Pattern recognition and common attacks",
        "Advanced": "Decision making under pressure",
        "Expert": "Prevention strategies and incident response"
    },
    "Passwords": {
        "Fundamentals": "Password basics and common risks",
        "Intermediate": "Strong authentication and best practices",
        "Advanced": "Managing credentials across systems",
        "Expert": "Defending identities with MFA and zero trust"
    },
    "Cloud Security": {
        "Fundamentals": "Cloud concepts and shared responsibility",
        "Intermediate": "Securing accounts, data, and access",
        "Advanced": "Misconfigurations, leaks, and threat scenarios",
        "Expert": "Cloud incident handling and hardening strategies"
    },
    "Ransomware": {
        "Fundamentals": "What ransomware is and how it spreads",
        "Intermediate": "Recognizing early signs and entry points",
        "Advanced": "Containment decisions under pressure",
        "Expert": "Recovery planning and resilience building"
    },
    "Deepfakes": {
        "Fundamentals": "Understanding deepfakes and media manipulation",
        "Intermediate": "Spotting visual and audio red flags",
        "Advanced": "Verification workflows and tool‑assisted checks",
        "Expert": "Responding to deepfake incidents and reputational attacks"
    },
    # Note: DB name is "Human Factors & Social Engineering Basics" based on previous script
    # User asked for "Human Factors & Social Engineering" - handling partial match or rename?
    # I will query filter using 'like' or exact if I can match.
    # Let's use the DB name "Human Factors & Social Engineering Basics"
    "Human Factors & Social Engineering Basics": {
        "Fundamentals": "Psychology of influence and bias awareness",
        "Intermediate": "Tactics used by social engineers",
        "Advanced": "Resisting pressure, urgency, and authority",
        "Expert": "Building a security‑aware culture"
    },
    "Secure Browsing & Malware": {
        "Fundamentals": "Safe browsing habits and basic threats",
        "Intermediate": "Malicious downloads, ads, and drive‑by attacks",
        "Advanced": "Recognizing suspicious behavior on endpoints",
        "Expert": "Practical containment and reporting of malware events"
    },
    "Public Wi‑Fi & Device Safety": {
        "Fundamentals": "Risks of public Wi‑Fi and shared devices",
        "Intermediate": "Safe configuration of devices on the move",
        "Advanced": "Using VPNs and secure channels effectively",
        "Expert": "Handling lost devices and travel‑related incidents"
    }
}

count = 0

for topic_name, levels in updates.items():
    topic = Topic.query.filter_by(topic_name=topic_name).first()
    
    if not topic:
        # Try finding without "Basics" suffix if it failed?
        # Or just print not found.
        print(f"❌ Topic NOT FOUND: {topic_name}")
        continue
        
    print(f"\nUpdating Topic: {topic.topic_name}")
    
    for level_name, new_desc in levels.items():
        level = DifficultyLevel.query.filter_by(
            topic_id=topic.topic_id,
            level_name=level_name
        ).first()
        
        if level:
            level.description = new_desc
            count += 1
            print(f"  ✓ {level_name}: {new_desc}")
        else:
            print(f"  ⚠️ Level NOT FOUND: {level_name}")

db.session.commit()
print(f"\n✓ Updated {count} level descriptions.")
