"""
Script to populate sample learning modules into the database
"""
import pymysql
import json
from dotenv import load_dotenv
import os

load_dotenv()

# Database connection
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
        # Get level IDs
        cursor.execute("SELECT level_id FROM path_levels WHERE level_number = 1")
        level1_id = cursor.fetchone()['level_id']
        
        cursor.execute("SELECT level_id FROM path_levels WHERE level_number = 2")
        level2_id = cursor.fetchone()['level_id']
        
        # Get type IDs
        cursor.execute("SELECT type_id FROM content_types WHERE type_name = 'theory'")
        theory_id = cursor.fetchone()['type_id']
        
        cursor.execute("SELECT type_id FROM content_types WHERE type_name = 'practical'")
        practical_id = cursor.fetchone()['type_id']
        
        cursor.execute("SELECT type_id FROM content_types WHERE type_name = 'quiz'")
        quiz_id = cursor.fetchone()['type_id']
        
        # Get category IDs
        cursor.execute("SELECT category_id FROM categories WHERE category_name = 'Phishing'")
        phishing_id = cursor.fetchone()['category_id']
        
        cursor.execute("SELECT category_id FROM categories WHERE category_name = 'Vishing'")
        vishing_id = cursor.fetchone()['category_id']
        
        cursor.execute("SELECT category_id FROM categories WHERE category_name = 'Smishing'")
        smishing_id = cursor.fetchone()['category_id']
        
        # Define modules
        modules = [
            # Level 1 - Phishing Theory
            {
                'level_id': level1_id,
                'category_id': phishing_id,
                'type_id': theory_id,
                'title': 'What is Phishing?',
                'description': 'Learn the basics of phishing attacks and how they work.',
                'content_json': json.dumps({
                    "sections": [
                        {
                            "heading": "Introduction",
                            "content": "Phishing is a type of social engineering attack where attackers impersonate legitimate organizations to steal sensitive information such as usernames, passwords, and credit card details."
                        },
                        {
                            "heading": "How It Works",
                            "content": "Attackers send fraudulent emails that appear to come from reputable sources. These emails often contain links to fake websites designed to capture your credentials."
                        },
                        {
                            "heading": "Red Flags",
                            "content": "Common signs include: urgent language, spelling errors, suspicious sender addresses, requests for sensitive information, and unexpected attachments."
                        }
                    ]
                }),
                'points_value': 100,
                'estimated_time_minutes': 10,
                'order_index': 1
            },
            # Level 1 - Phishing Practical
            {
                'level_id': level1_id,
                'category_id': phishing_id,
                'type_id': practical_id,
                'title': 'Spot the Phishing Email',
                'description': 'Interactive exercise to identify phishing attempts.',
                'content_json': json.dumps({
                    "scenario": {
                        "description": "You receive an email claiming to be from your bank asking you to verify your account by clicking a link.",
                        "email_from": "security@paypa1-verify.com",
                        "email_subject": "URGENT: Verify Your Account Now!",
                        "email_body": "Dear Customer, We have detected unusual activity on your account. Click here immediately to verify your identity or your account will be suspended within 24 hours.",
                        "question": "Is this email legitimate or a phishing attempt?",
                        "options": ["Legitimate", "Phishing"],
                        "correct_answer": "Phishing",
                        "explanation": "This is a phishing email. Red flags: misspelled domain (paypa1 instead of paypal), urgent threatening language, and request to click a link."
                    }
                }),
                'points_value': 150,
                'estimated_time_minutes': 5,
                'order_index': 2
            },
            # Level 1 - Phishing Quiz
            {
                'level_id': level1_id,
                'category_id': phishing_id,
                'type_id': quiz_id,
                'title': 'Phishing Fundamentals Quiz',
                'description': 'Test your understanding of phishing basics.',
                'content_json': json.dumps({
                    "questions": [
                        {
                            "question": "What is the primary goal of a phishing attack?",
                            "options": ["To damage computer hardware", "To steal sensitive information", "To improve email security", "To test network speed"],
                            "correct_answer": "To steal sensitive information"
                        },
                        {
                            "question": "Which of these is a common phishing red flag?",
                            "options": ["Professional email signature", "Correct company logo", "Urgent threatening language", "Personalized greeting"],
                            "correct_answer": "Urgent threatening language"
                        },
                        {
                            "question": "What should you do if you receive a suspicious email?",
                            "options": ["Click all links to investigate", "Reply asking if it's legitimate", "Report it and delete it", "Forward it to all contacts"],
                            "correct_answer": "Report it and delete it"
                        }
                    ]
                }),
                'points_value': 120,
                'estimated_time_minutes': 8,
                'order_index': 3
            },
            # Level 1 - Vishing Theory
            {
                'level_id': level1_id,
                'category_id': vishing_id,
                'type_id': theory_id,
                'title': 'Understanding Vishing',
                'description': 'Voice phishing attacks explained.',
                'content_json': json.dumps({
                    "sections": [
                        {
                            "heading": "What is Vishing?",
                            "content": "Vishing (voice phishing) is a form of social engineering where attackers use phone calls to trick victims into revealing personal information."
                        },
                        {
                            "heading": "Common Tactics",
                            "content": "Attackers often impersonate bank representatives, tech support, or government officials. They create urgency and use fear tactics to pressure victims."
                        },
                        {
                            "heading": "Protection",
                            "content": "Never share personal information over the phone unless you initiated the call. Verify the caller's identity through official channels before providing any information."
                        }
                    ]
                }),
                'points_value': 100,
                'estimated_time_minutes': 10,
                'order_index': 4
            },
            # Level 1 - Smishing Theory
            {
                'level_id': level1_id,
                'category_id': smishing_id,
                'type_id': theory_id,
                'title': 'SMS Phishing Awareness',
                'description': 'Learn about text message-based attacks.',
                'content_json': json.dumps({
                    "sections": [
                        {
                            "heading": "Smishing Explained",
                            "content": "Smishing combines SMS and phishing. Attackers send fraudulent text messages to trick recipients into clicking malicious links or sharing sensitive data."
                        },
                        {
                            "heading": "Common Examples",
                            "content": "Fake delivery notifications, prize winnings, bank alerts, and COVID-19 related scams are common smishing tactics."
                        },
                        {
                            "heading": "Stay Safe",
                            "content": "Be suspicious of unexpected texts, verify through official apps or websites, and never click links from unknown numbers."
                        }
                    ]
                }),
                'points_value': 100,
                'estimated_time_minutes': 10,
                'order_index': 5
            }
        ]
        
        # Insert modules
        for module in modules:
            cursor.execute("""
                INSERT INTO learning_modules 
                (level_id, category_id, type_id, title, description, content_json, points_value, estimated_time_minutes, order_index)
                VALUES (%(level_id)s, %(category_id)s, %(type_id)s, %(title)s, %(description)s, %(content_json)s, %(points_value)s, %(estimated_time_minutes)s, %(order_index)s)
            """, module)
        
        conn.commit()
        print("✅ Successfully inserted sample modules!")
        print(f"   Total modules added: {len(modules)}")

except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    conn.close()
