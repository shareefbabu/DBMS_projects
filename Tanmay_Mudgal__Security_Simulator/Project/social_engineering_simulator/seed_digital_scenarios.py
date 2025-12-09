import pymysql
import json
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = pymysql.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DB', 'social_engineering_db'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    scenarios = [
        {
            "type": "DigitalPayment",
            "diff": "Medium",
            "desc": "You receive a message on 'PayApp': 'Ref: 128383. You have received a cashback reward of ₹2000! Click 'Pay' to claim it in your bank account.'",
            "correct": "Reject / Report",
            "expl": "Scammers send 'Collect Requests' disguised as 'Receive Money'. Clicking 'Pay' and entering your PIN deducts money from YOUR account. You never need to enter a PIN to receive money.",
            "options": ["Click 'Pay' to claim", "Reject / Report", "Call Customer Support"]
        },
        {
            "type": "DigitalPayment",
            "diff": "Hard",
            "desc": "You are selling a sofa online. The buyer sends a QR code and says: 'Scan this to receive the advance payment of ₹5000'.",
            "correct": "Refuse to Scan",
            "expl": "QR Codes are ONLY for sending money, not receiving. If you scan this code and enter a PIN, you will lose ₹5000.",
            "options": ["Scan the QR Code", "Refuse to Scan", "Ask for a different QR code"]
        },
        {
            "type": "DigitalPayment",
            "diff": "Medium",
            "desc": "You get an SMS: 'Your Bank KYC has expired. Your account will be blocked in 24 hours. Click here to update KYC instantly: http://bit.ly/bank-kyc-update'.",
            "correct": "Ignore & Contact Bank Directly",
            "expl": "Banks never send threatening SMS with short-links (bit.ly) for KYC. Always visit your branch or official apps. This is a phishing text.",
            "options": ["Click the link", "Ignore & Contact Bank Directly", "Reply with Documents"]
        }
    ]

    with conn.cursor() as cursor:
        print("🌱 Seeding Digital Payment Scenarios...")
        
        for s in scenarios:
            # Check if exists
            cursor.execute("SELECT scenario_id FROM scenarios WHERE scenario_description LIKE %s", (s['desc'][:50] + '%',))
            if cursor.fetchone():
                print(f"Skipping existing scenario: {s['desc'][:20]}...")
                continue
                
            cursor.execute("""
                INSERT INTO scenarios 
                (scenario_type, difficulty_level, scenario_description, correct_answer, explanation, options_json)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (s['type'], s['diff'], s['desc'], s['correct'], s['expl'], json.dumps(s['options'])))
            print(f"Added: {s['desc'][:20]}...")
            
    conn.commit()
    print("✅ Seed complete.")

except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if 'conn' in locals() and conn.open:
        conn.close()
