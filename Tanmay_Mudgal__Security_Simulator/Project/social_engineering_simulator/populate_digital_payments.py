import pymysql
import json
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

conn = pymysql.connect(
    host=os.getenv('MYSQL_HOST', 'localhost'),
    user=os.getenv('MYSQL_USER', 'root'),
    password=os.getenv('MYSQL_PASSWORD'),
    database=os.getenv('MYSQL_DB', 'social_engineering_db'),
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cursor:
        print("🚀 Starting Digital Payments Module population...")

        # 1. Get 'theory' Type ID
        cursor.execute("SELECT type_id FROM content_types WHERE type_name = 'theory'")
        res = cursor.fetchone()
        if not res:
            print("Creating 'theory' type...")
            cursor.execute("INSERT INTO content_types (type_name) VALUES ('theory')")
            theory_id = cursor.lastrowid
        else:
            theory_id = res['type_id']

        # 2. Create/Get 'Digital Payments' Category
        cat_name = "Digital Payments"
        cursor.execute("SELECT category_id FROM categories WHERE category_name = %s", (cat_name,))
        res = cursor.fetchone()
        if not res:
            print(f"Creating category: {cat_name}")
            cursor.execute("INSERT INTO categories (category_name, icon, color_code, description) VALUES (%s, '💳', '#10b981', 'Safe digital transaction practices')", (cat_name,))
            category_id = cursor.lastrowid
        else:
            category_id = res['category_id']

        # 3. Create 'Digital Payments' Topic
        topic_name = "Digital Payments & Mobile Scams (India‑focused)"
        cursor.execute("SELECT topic_id FROM topics WHERE topic_name = %s", (topic_name,))
        res = cursor.fetchone()
        
        if res:
            print("Topic already exists. Skipping insertion to avoid duplicates.")
            topic_id = res['topic_id']
        else:
            print(f"Creating topic: {topic_name}")
            # Identify max topic number to append
            cursor.execute("SELECT MAX(topic_number) as max_num FROM topics")
            max_num = cursor.fetchone()['max_num'] or 0
            
            cursor.execute("""
                INSERT INTO topics (topic_number, topic_name, description, icon)
                VALUES (%s, %s, 'Master UPI safety, avoid QR scams, and secure mobile payments.', 'mobile-alt')
            """, (max_num + 1, topic_name))
            topic_id = cursor.lastrowid

            # 4. Create Difficulty Levels & Modules for this Topic
            levels_data = [
                {
                    "num": 1, "name": "Fundamentals", "desc": "UPI, QR codes and OTP basics",
                    "module": {
                        "title": "UPI & Payment Basics",
                        "desc": "Understand how UPI, QR codes, and OTPs work securely.",
                        "content": {
                            "sections": [
                                {"heading": "What is UPI?", "content": "Unified Payments Interface (UPI) allows instant money transfer between valid bank accounts using a mobile phone. Always verify the VPA (Virtual Payment Address)."},
                                {"heading": "QR Codes (Quick Response)", "content": "QR codes are scannable barcodes. IMPORTANT: You only scan a QR code to PAY money, never to receive money. If someone asks you to scan to receive a prize, it is a scam."},
                                {"heading": "OTP Secrecy", "content": "One-Time Password (OTP) is the final key. Never share your OTP with anyone, even if they claim to be from the bank."}
                            ]
                        }
                    }
                },
                {
                    "num": 2, "name": "Intermediate", "desc": "Common UPI, QR and KYC scam patterns",
                    "module": {
                        "title": "Spotting Payment Scams",
                        "desc": "Learn to identify fake KYC alerts and money request frauds.",
                        "content": {
                            "sections": [
                                {"heading": "The 'Money Request' Scam", "content": "Fraudsters send a 'Collect Request' on UPI apps but claim they are sending you money. Accepting the request deducts money from YOUR account."},
                                {"heading": "Fake KYC Updates", "content": "SMS claiming 'Your Paytm/Bank KYC is expired' are fake. Banks never ask you to install 3rd party support apps for KYC."},
                                {"heading": "Cashback Scams", "content": "Fake scratch cards on Google Pay/PhonePe that promise rewards but ask for your PIN are scams."}
                            ]
                        }
                    }
                },
                {
                    "num": 3, "name": "Advanced", "desc": "Remote‑access & SIM‑swap frauds",
                    "module": {
                        "title": "Complex Fraud Tactics",
                        "desc": "Deep dive into screen-sharing and SIM swapping attacks.",
                        "content": {
                            "sections": [
                                {"heading": "Screen Sharing Apps", "content": "Scammers ask you to install apps like AnyDesk, TeamViewer, or QuickSupport. These apps give them full control of your phone to see your OTPs."},
                                {"heading": "SIM Swap Fraud", "content": "Attackers duplicate your SIM card to intercept OTPs. If your phone loses signal unexpectedly for a long time, contact your carrier immediately."},
                                {"heading": "Forwarding Scams", "content": "Attackers may ask you to dial a code (like *401*...) which forwards your calls (and OTPs) to their number."}
                            ]
                        }
                    }
                },
                {
                    "num": 4, "name": "Expert", "desc": "Safe recovery & Reporting (1930)",
                    "module": {
                        "title": "Incident Response & Recovery",
                        "desc": "How to report cybercrime and assist potential victims.",
                        "content": {
                            "sections": [
                                {"heading": "Golden Hour", "content": "Reporting fraud within the first hour increases chances of recovery. Immediate action is critical."},
                                {"heading": "Dial 1930", "content": "In India, dial 1930 to report financial cyber fraud immediately. It connects to the National Cyber Crime Reporting Portal."},
                                {"heading": "Cybercrime Portal", "content": "File a formal complaint at cybercrime.gov.in. Keep transaction IDs and screenshots as evidence."},
                                {"heading": "Coaching Others", "content": "Help elderly family members set transaction limits and identify red flags."}
                            ]
                        }
                    }
                }
            ]

            print("Creating Levels and Modules...")
            previous_level_id = None
            
            for lvl in levels_data:
                # Create Level
                cursor.execute("""
                    INSERT INTO difficulty_levels 
                    (topic_id, level_number, level_name, description, previous_level_id)
                    VALUES (%s, %s, %s, %s, %s)
                """, (topic_id, lvl['num'], lvl['name'], lvl['desc'], previous_level_id))
                
                diff_lvl_id = cursor.lastrowid
                previous_level_id = diff_lvl_id
                
                # Create Module
                mod = lvl['module']
                cursor.execute("""
                    INSERT INTO learning_modules
                    (difficulty_level_id, category_id, type_id, title, description, content_json, points_value, estimated_time_minutes, order_index)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    diff_lvl_id, 
                    category_id, 
                    theory_id, 
                    mod['title'], 
                    mod['desc'], 
                    json.dumps(mod['content']),
                    100 * lvl['num'], # Increasing points
                    5 + (lvl['num'] * 2), # TIME
                    1
                ))

        conn.commit()
        print("✅ Digital Payments module populated successfully!")

except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    conn.close()
