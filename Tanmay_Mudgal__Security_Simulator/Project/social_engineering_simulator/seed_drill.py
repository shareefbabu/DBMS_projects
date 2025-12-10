import json
from app import create_app, db
from app.models import Scenario

app = create_app()

def seed_drill():
    with app.app_context():
        # Check if exists
        exists = Scenario.query.filter_by(scenario_type='IncidentResponse').first()
        if exists:
            print("Drill already exists.")
            return

        steps = [
            "Disconnect the infected device from the network",
            "Notify the Security Operations Center (SOC)",
            "Identify the ransomware variant",
            "Determine the scope of the infection",
            "Restore data from clean backups"
        ]

        drill = Scenario(
            scenario_type='IncidentResponse',
            difficulty_level='Intermediate',
            scenario_description='A user reports a red screen requesting Bitcoin payment. How do you proceed?',
            correct_answer='Ordered Steps', # Placeholder
            steps_json=json.dumps(steps),
            explanation='Immediate isolation prevents spread. Notification triggers broader response. Identification aids in remediation. Scoping ensures no remnants. Restoration recovers availability.'
        )

        db.session.add(drill)
        db.session.commit()
        print("Seeded Incident Response Drill.")

if __name__ == "__main__":
    seed_drill()
