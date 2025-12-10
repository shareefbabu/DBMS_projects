"""
Seed script for Incident Response Drills
"""
import sys
import os
import json

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from app import create_app, db
from app.models import Scenario

app = create_app()
app.app_context().push()

scenarios_data = [
    {
        "type": "IncidentResponse",
        "difficulty": "Intermediate",
        "description": "Ransomware on a Workstation: User notices files renamed with strange extensions and a ransom note on their desktop demanding cryptocurrency.",
        "steps": [
            "Disconnect the affected device from the network (unplug cable / turn off Wi‑Fi).",
            "Inform the internal security team / SOC or IT helpdesk immediately.",
            "Preserve evidence: do not delete ransom notes or logs; take screenshots if allowed.",
            "Follow the incident reporting process (create a ticket / fill incident form).",
            "Await instructions; do not attempt to pay the ransom or run unapproved tools."
        ]
    },
    {
        "type": "IncidentResponse",
        "difficulty": "Intermediate",
        "description": "Suspicious Phishing Link Clicked: User accidentally clicks a phishing link in an email and briefly sees a fake login page, but closes it without entering credentials.",
        "steps": [
            "Stop interacting with the page and close the browser tab.",
            "Report the phishing email using the company’s reporting button or process.",
            "Inform the security/IT team that the link was clicked (even if no data was entered).",
            "Follow guidance from IT (e.g., run an approved scan or check the device).",
            "Review the email and training material to understand what made it suspicious."
        ]
    },
    {
        "type": "IncidentResponse",
        "difficulty": "Intermediate", 
        "description": "Lost or Stolen Work Laptop: User’s corporate laptop is stolen from a café or lost in transit.",
        "steps": [
            "As soon as the loss is noticed, contact the security/IT helpdesk to report the lost device.",
            "Provide details: time, place, device type, and any visible labels or asset tags.",
            "Follow instructions for remote wipe/lock and changing passwords.",
            "File a formal report according to company policy (and with local authorities if required).",
            "Cooperate with any follow‑up investigation and avoid storing work data on personal devices as a substitute."
        ]
    },
    {
        "type": "IncidentResponse",
        "difficulty": "Advanced",
        "description": "Suspected Internal Data Exfiltration: User sees a colleague copying large customer data files to a personal USB drive without a clear reason.",
        "steps": [
            "Do not confront or accuse the colleague directly in an aggressive way.",
            "Document what you observed (time, place, approximate data type).",
            "Report the behavior through the confidential security/ethics reporting channel.",
            "Provide additional information to security/HR if they request clarification.",
            "Do not discuss the incident widely with other coworkers or on social media."
        ]
    },
    {
        "type": "IncidentResponse",
        "difficulty": "Fundamentals",
        "description": "Malicious USB Found in Office: User finds an unlabelled or suspicious USB drive near the office entrance or parking lot.",
        "steps": [
            "Do not plug the USB drive into any device (work or personal).",
            "Inform security/IT that a suspicious device was found.",
            "Hand over the USB drive following the organization’s procedure (e.g., to security desk).",
            "Record the location and time it was found if requested.",
            "Complete any short awareness follow‑up or reminder from security."
        ]
    },
    {
        "type": "IncidentResponse",
        "difficulty": "Intermediate",
        "description": "Compromised Credentials (Phishing Submission): User realizes they entered their username and password into a fake site a few minutes ago.",
        "steps": [
            "Immediately go to the official corporate login page or password portal.",
            "Change the password for the compromised account (and any other accounts using the same password, if allowed by policy).",
            "Enable or re‑check multi‑factor authentication if available.",
            "Report the incident to security/IT, including the phishing email or URL.",
            "Cooperate with any additional steps (e.g., forced logout from other sessions, further scans)."
        ]
    },
    {
        "type": "IncidentResponse",
        "difficulty": "Advanced",
        "description": "Suspicious Network Activity on a Server: User (IT/admin role) sees unusual outbound connections or alerts on a critical server monitoring panel.",
        "steps": [
            "Follow runbook: notify the on‑call security/incident response or senior admin.",
            "Isolate or restrict the affected server according to policy (e.g., move to quarantine VLAN).",
            "Preserve logs and avoid rebooting or wiping systems unless instructed.",
            "Help collect initial evidence (logs, timestamps, IPs) as directed by IR team.",
            "Participate in post‑incident review and implement any recommended hardening steps."
        ]
    },
    {
        "type": "IncidentResponse",
        "difficulty": "Intermediate",
        "description": "Misdelivered Sensitive Email: User sends a sensitive spreadsheet to the wrong external email address and immediately realizes it.",
        "steps": [
            "If possible, recall the email using the mail system’s recall feature (if supported).",
            "Inform the security/privacy or compliance contact and your manager about the misdelivery.",
            "Provide details: data type, recipient address, time sent.",
            "Follow data‑breach or privacy incident procedures (e.g., logging, potential notification).",
            "Review and apply safer sharing methods (access‑controlled links, double‑check recipients, DLP tools)."
        ]
    }
]

print(f"Seeding {len(scenarios_data)} Incident Response scenarios...")

count = 0
for data in scenarios_data:
    # Check if exists (by description snippet)
    existing = Scenario.query.filter(Scenario.scenario_description.like(f"{data['description'][:20]}%")).first()
    
    if existing:
        print(f"Skipping existing: {data['description'][:30]}...")
        # Update steps anyway to be sure
        existing.steps_json = json.dumps(data['steps'])
        existing.scenario_type = 'IncidentResponse' # Ensure type is set
    else:
        scenario = Scenario(
            scenario_type='IncidentResponse',
            difficulty_level=data['difficulty'],
            scenario_description=data['description'],
            correct_answer='See steps_json', # Flexible placeholder
            steps_json=json.dumps(data['steps'])
        )
        db.session.add(scenario)
        count += 1
        print(f"Added: {data['description'][:30]}...")

db.session.commit()
print(f"Done! Added {count} new scenarios.")
