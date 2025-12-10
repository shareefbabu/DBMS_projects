-- Sample Learning Modules for Path to Mastery
-- Inserting realistic content across categories and levels

-- Get IDs for reference
SET @level1_id = (SELECT level_id FROM path_levels WHERE level_number = 1 LIMIT 1);
SET @level2_id = (SELECT level_id FROM path_levels WHERE level_number = 2 LIMIT 1);
SET @level3_id = (SELECT level_id FROM path_levels WHERE level_number = 3 LIMIT 1);
SET @level4_id = (SELECT level_id FROM path_levels WHERE level_number = 4 LIMIT 1);

SET @theory_id = (SELECT type_id FROM content_types WHERE type_name = 'theory' LIMIT 1);
SET @practical_id = (SELECT type_id FROM content_types WHERE type_name = 'practical' LIMIT 1);
SET @quiz_id = (SELECT type_id FROM content_types WHERE type_name = 'quiz' LIMIT 1);

SET @phishing_id = (SELECT category_id FROM categories WHERE category_name = 'Phishing' LIMIT 1);
SET @vishing_id = (SELECT category_id FROM categories WHERE category_name = 'Vishing' LIMIT 1);
SET @smishing_id = (SELECT category_id FROM categories WHERE category_name = 'Smishing' LIMIT 1);

-- LEVEL 1 MODULES (Fundamentals)

-- Module 1: Phishing Theory
INSERT INTO learning_modules (level_id, category_id, type_id, title, description, content_json, points_value, estimated_time_minutes, order_index) VALUES
(@level1_id, @phishing_id, @theory_id, 'What is Phishing?', 'Learn the basics of phishing attacks and how they work.', 
'{
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
}', 100, 10, 1);

-- Module 2: Phishing Practical
INSERT INTO learning_modules (level_id, category_id, type_id, title, description, content_json, points_value, estimated_time_minutes, order_index) VALUES
(@level1_id, @phishing_id, @practical_id, 'Spot the Phishing Email', 'Interactive exercise to identify phishing attempts.', 
'{
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
}', 150, 5, 2);

-- Module 3: Phishing Quiz
INSERT INTO learning_modules (level_id, category_id, type_id, title, description, content_json, points_value, estimated_time_minutes, order_index) VALUES
(@level1_id, @phishing_id, @quiz_id, 'Phishing Fundamentals Quiz', 'Test your understanding of phishing basics.', 
'{
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
            "options": ["Click all links to investigate", "Reply asking if its legitimate", "Report it and delete it", "Forward it to all contacts"],
            "correct_answer": "Report it and delete it"
        }
    ]
}', 120, 8, 3);

-- Module 4: Vishing Theory
INSERT INTO learning_modules (level_id, category_id, type_id, title, description, content_json, points_value, estimated_time_minutes, order_index) VALUES
(@level1_id, @vishing_id, @theory_id, 'Understanding Vishing', 'Voice phishing attacks explained.', 
'{
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
            "content": "Never share personal information over the phone unless you initiated the call. Verify the callers identity through official channels before providing any information."
        }
    ]
}', 100, 10, 4);

-- Module 5: Smishing Theory
INSERT INTO learning_modules (level_id, category_id, type_id, title, description, content_json, points_value, estimated_time_minutes, order_index) VALUES
(@level1_id, @smishing_id, @theory_id, 'SMS Phishing Awareness', 'Learn about text message-based attacks.', 
'{
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
}', 100, 10, 5);

-- LEVEL 2 MODULES (Intermediate)

-- Module 6: Advanced Phishing Techniques
INSERT INTO learning_modules (level_id, category_id, type_id, title, description, content_json, points_value, estimated_time_minutes, order_index) VALUES
(@level2_id, @phishing_id, @theory_id, 'Spear Phishing & Whaling', 'Advanced targeted phishing attacks.', 
'{
    "sections": [
        {
            "heading": "Spear Phishing",
            "content": "Unlike mass phishing, spear phishing targets specific individuals or organizations with personalized messages that appear highly legitimate."
        },
        {
            "heading": "Whaling Attacks",
            "content": "Whaling targets high-profile individuals like CEOs and executives. These attacks are sophisticated and often involve extensive research about the target."
        },
        {
            "heading": "Defense Strategies",
            "content": "Verify requests through secondary channels, be skeptical of urgent requests from executives, and implement multi-factor authentication."
        }
    ]
}', 200, 15, 1);

-- Module 7: Real-World Vishing Scenario
INSERT INTO learning_modules (level_id, category_id, type_id, title, description, content_json, points_value, estimated_time_minutes, order_index) VALUES
(@level2_id, @vishing_id, @practical_id, 'Tech Support Scam Simulation', 'Interactive vishing scenario.', 
'{
    "scenario": {
        "description": "You receive a call from someone claiming to be from Microsoft saying your computer has a virus.",
        "caller_says": "Hello, this is Microsoft Security. We have detected a critical virus on your computer. I need you to give me remote access to fix it immediately.",
        "question": "What should you do?",
        "options": [
            "Give them remote access immediately",
            "Hang up and report the scam",
            "Ask for their employee ID and call back",
            "Run antivirus software while on the call"
        ],
        "correct_answer": "Hang up and report the scam",
        "explanation": "Microsoft (and most legitimate companies) will never cold-call you about computer issues. This is a classic vishing scam. Hang up immediately and report it."
    }
}', 250, 10, 2);
