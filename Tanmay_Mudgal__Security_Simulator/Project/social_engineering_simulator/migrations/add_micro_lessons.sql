-- Migration: Add Micro-Lessons Tables
USE social_engineering_db;

-- Create micro_lessons table
CREATE TABLE IF NOT EXISTS micro_lessons (
    lesson_id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content_text TEXT NOT NULL,
    est_time_minutes INT DEFAULT 5,
    quiz_json JSON NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    INDEX idx_category (category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create assigned_lessons table
CREATE TABLE IF NOT EXISTS assigned_lessons (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    lesson_id INT NOT NULL,
    scenario_id INT,
    assigned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    status ENUM('pending', 'in_progress', 'completed') DEFAULT 'pending',
    quiz_score INT DEFAULT 0,
    completed_at DATETIME,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (lesson_id) REFERENCES micro_lessons(lesson_id),
    FOREIGN KEY (scenario_id) REFERENCES scenarios(scenario_id) ON DELETE SET NULL,
    UNIQUE KEY unique_user_lesson (user_id, lesson_id),
    INDEX idx_user_status (user_id, status),
    INDEX idx_assigned_at (assigned_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Seed Data for Micro-Lessons
INSERT INTO micro_lessons (category_id, title, content_text, est_time_minutes, quiz_json) 
SELECT category_id, 'Recognizing Urgent Phishing Emails', 
 'Phishing emails often create a false sense of urgency to bypass critical thinking. Common tactics include: threats of account suspension, limited-time offers, security alerts, and unusual requests. Always verify through official channels before acting.',
 5,
 '{"questions": [
    {"question": "What is a red flag in phishing emails?", "options": ["Professional tone", "Urgent deadlines", "Company logo", "Proper grammar"], "correct_answer": "Urgent deadlines"},
    {"question": "How should you verify a suspicious email?", "options": ["Click the link", "Call official number", "Reply to email", "Forward to friends"], "correct_answer": "Call official number"},
    {"question": "What is email spoofing?", "options": ["Spam filter", "Fake sender address", "Email encryption", "Auto-reply"], "correct_answer": "Fake sender address"}
 ]}'
FROM categories WHERE category_name = 'Phishing'
LIMIT 1;

INSERT INTO micro_lessons (category_id, title, content_text, est_time_minutes, quiz_json)
SELECT category_id, 'Detecting Voice Phishing Scams',
 'Vishing (voice phishing) uses phone calls to trick victims. Warning signs: unsolicited calls, requests for sensitive info, pressure tactics, refusal to provide callback numbers. Always hang up and call back using official contact info.',
 5,
 '{"questions": [
    {"question": "What should you NEVER share over unsolicited calls?", "options": ["Name", "City", "Password", "Job title"], "correct_answer": "Password"},
    {"question": "Legitimate companies will:", "options": ["Ask for SSN", "Pressure immediately", "Allow callback", "Threaten legal action"], "correct_answer": "Allow callback"},
    {"question": "Caller ID shows bank name. Is it safe?", "options": ["Yes, caller ID proves it", "No, can be spoofed", "Only if they know my name", "Always trust it"], "correct_answer": "No, can be spoofed"}
 ]}'
FROM categories WHERE category_name = 'Vishing'
LIMIT 1;
