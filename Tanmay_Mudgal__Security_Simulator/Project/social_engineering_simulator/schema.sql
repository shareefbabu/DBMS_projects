-- Social Engineering Training Simulator Database Schema
-- Database: social_engineering_db

CREATE DATABASE IF NOT EXISTS social_engineering_db;
USE social_engineering_db;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(120),
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    total_score INT DEFAULT 0,
    vulnerability_level VARCHAR(32) DEFAULT 'Medium',
    organization VARCHAR(100),
    account_type VARCHAR(20) DEFAULT 'Individual',
    INDEX idx_username (username),
    INDEX idx_total_score (total_score DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Scenarios table
CREATE TABLE IF NOT EXISTS scenarios (
    scenario_id INT AUTO_INCREMENT PRIMARY KEY,
    scenario_type VARCHAR(50) NOT NULL,
    difficulty_level VARCHAR(32) NOT NULL,
    scenario_description TEXT NOT NULL,
    correct_answer VARCHAR(50) NOT NULL,
    keywords_to_identify TEXT,
    explanation TEXT,
    steps_json TEXT,
    INDEX idx_scenario_type (scenario_type),
    INDEX idx_difficulty (difficulty_level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- User responses table
CREATE TABLE IF NOT EXISTS user_responses (
    response_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    scenario_id INT NOT NULL,
    user_response VARCHAR(50),
    is_correct BOOLEAN,
    response_time INT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    response_json TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (scenario_id) REFERENCES scenarios(scenario_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_scenario_id (scenario_id),
    INDEX idx_timestamp (timestamp DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Learning progress table
CREATE TABLE IF NOT EXISTS learning_progress (
    progress_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    phishing_success_rate FLOAT DEFAULT 0.0,
    baiting_success_rate FLOAT DEFAULT 0.0,
    pretexting_success_rate FLOAT DEFAULT 0.0,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Achievements table
CREATE TABLE IF NOT EXISTS achievements (
    achievement_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    achievement_name VARCHAR(100),
    criteria_met VARCHAR(100),
    earned_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_earned_date (earned_date DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ==========================================
-- ADVANCED FEATURES (RBAC, Audit, Logs)
-- ==========================================

-- Roles Table
CREATE TABLE IF NOT EXISTS roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    is_system_role BOOLEAN DEFAULT FALSE,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_date DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_role_name (role_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Permissions Table
CREATE TABLE IF NOT EXISTS permissions (
    permission_id INT AUTO_INCREMENT PRIMARY KEY,
    permission_name VARCHAR(100) UNIQUE NOT NULL,
    resource VARCHAR(50) NOT NULL,
    action VARCHAR(50) NOT NULL,
    description TEXT,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_permission_name (permission_name),
    INDEX idx_resource (resource)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- User-Role Mapping
CREATE TABLE IF NOT EXISTS user_roles (
    user_role_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    assigned_by INT,
    assigned_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_date DATETIME NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE,
    FOREIGN KEY (assigned_by) REFERENCES users(user_id) ON DELETE SET NULL,
    UNIQUE KEY unique_user_role (user_id, role_id),
    INDEX idx_user_id (user_id),
    INDEX idx_role_id (role_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Role-Permission Mapping
CREATE TABLE IF NOT EXISTS role_permissions (
    role_permission_id INT AUTO_INCREMENT PRIMARY KEY,
    role_id INT NOT NULL,
    permission_id INT NOT NULL,
    granted_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE,
    FOREIGN KEY (permission_id) REFERENCES permissions(permission_id) ON DELETE CASCADE,
    UNIQUE KEY unique_role_permission (role_id, permission_id),
    INDEX idx_role_id (role_id),
    INDEX idx_permission_id (permission_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Response Details (Enhanced Logging)
CREATE TABLE IF NOT EXISTS response_details (
    detail_id INT AUTO_INCREMENT PRIMARY KEY,
    response_id INT NOT NULL,
    step_number INT DEFAULT 1,
    step_description TEXT,
    user_answer TEXT,
    expected_answer TEXT,
    is_correct BOOLEAN,
    confidence_level DECIMAL(3,2),
    time_spent INT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    flags JSON,
    FOREIGN KEY (response_id) REFERENCES user_responses(response_id) ON DELETE CASCADE,
    INDEX idx_response_id (response_id),
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Scenario Progress (Partial Completion)
CREATE TABLE IF NOT EXISTS scenario_progress (
    progress_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    scenario_id INT NOT NULL,
    current_step INT DEFAULT 1,
    total_steps INT,
    completion_percentage DECIMAL(5,2),
    last_interaction DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    status ENUM('in_progress', 'completed', 'abandoned') DEFAULT 'in_progress',
    session_data JSON,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (scenario_id) REFERENCES scenarios(scenario_id) ON DELETE CASCADE,
    INDEX idx_user_scenario (user_id, scenario_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Notification Types
CREATE TABLE IF NOT EXISTS notification_types (
    type_id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(50) UNIQUE NOT NULL,
    description TEXT,
    default_template TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    type_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    status ENUM('pending', 'sent', 'read', 'archived') DEFAULT 'pending',
    priority ENUM('low', 'medium', 'high', 'urgent') DEFAULT 'medium',
    scheduled_for DATETIME NULL,
    sent_at DATETIME NULL,
    read_at DATETIME NULL,
    expires_at DATETIME NULL,
    action_url VARCHAR(500),
    meta_data JSON,
    created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (type_id) REFERENCES notification_types(type_id),
    INDEX idx_user_id (user_id),
    INDEX idx_status (status),
    INDEX idx_scheduled (scheduled_for),
    INDEX idx_created (created_date DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Notification History
CREATE TABLE IF NOT EXISTS notification_history (
    history_id INT AUTO_INCREMENT PRIMARY KEY,
    notification_id INT NOT NULL,
    status_change VARCHAR(50) NOT NULL,
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    changed_by INT,
    notes TEXT,
    FOREIGN KEY (notification_id) REFERENCES notifications(notification_id) ON DELETE CASCADE,
    INDEX idx_notification_id (notification_id),
    INDEX idx_changed_at (changed_at DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    audit_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    username VARCHAR(80),
    action_type VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id INT,
    action_description TEXT NOT NULL,
    ip_address VARCHAR(45),
    user_agent TEXT,
    request_method VARCHAR(10),
    request_url VARCHAR(500),
    status ENUM('success', 'failure', 'error') NOT NULL,
    error_message TEXT,
    old_value JSON,
    new_value JSON,
    severity ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    session_id VARCHAR(100),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_user_id (user_id),
    INDEX idx_timestamp (timestamp DESC),
    INDEX idx_action_type (action_type),
    INDEX idx_status (status),
    INDEX idx_severity (severity),
    INDEX idx_ip_address (ip_address)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert comprehensive phishing scenarios
INSERT INTO scenarios (scenario_type, difficulty_level, scenario_description, correct_answer, keywords_to_identify, explanation) VALUES
-- PHISHING SCENARIOS
('Phishing', 'Easy', 'You receive an email from "support@paypa1.com" (note the number 1 instead of letter l) claiming your account has been suspended. The email asks you to click a link immediately to verify your identity and restore access.', 'Suspicious', 'misspelled domain, urgency, click link, verify identity', 'This is a classic phishing attempt. The domain uses a "1" instead of "l" (paypa1 vs paypal), creating urgency to bypass critical thinking, and requests credential verification through a link.'),

('Phishing', 'Easy', 'An email arrives claiming to be from your bank, asking you to confirm a large transaction you didn''t authorize by clicking a link. The sender email is "security@bankofamerica-verify.com".', 'Suspicious', 'suspicious subdomain, urgency, unauthorized transaction, click link', 'Legitimate banks never send emails with verification links for transactions. The subdomain "bankofamerica-verify.com" is not the official bank domain. This is phishing.'),

('Phishing', 'Easy', 'You get an email from "IT Department" with subject "Password Expiration Notice" saying your company password will expire in 24 hours and you must click a link to reset it.', 'Suspicious', 'generic sender, urgency, password reset link, 24 hours', 'IT departments rarely send password reset links via email. The generic sender name and artificial urgency are red flags. Legitimate password resets should be done through official company portals.'),

('Phishing', 'Medium', 'You receive a professional-looking email from "Amazon Customer Service" regarding an order you placed. The email has Amazon branding and asks you to review an attached invoice PDF. The sender is "no-reply@amazon.customer-service.com".', 'Suspicious', 'subdomain spoofing, unexpected attachment, mimics legitimate service', 'While the email looks professional, the domain "amazon.customer-service.com" is not Amazon''s official domain (should be @amazon.com). Legitimate order notifications come from verified Amazon addresses and don''t use suspicious subdomains.'),

('Phishing', 'Medium', 'An email arrives from your company CEO (correct name and photo in signature) asking you to urgently purchase gift cards for a client meeting and send the codes via email. The sender address is ceo@yourcompany.co instead of .com.', 'Suspicious', 'CEO fraud, urgency, gift cards, wrong TLD domain', 'This is CEO fraud/whaling. While it uses the correct name, the domain extension is wrong (.co vs .com), and executives don''t ask employees to purchase gift cards via email. Always verify unusual requests through other channels.'),

('Phishing', 'Medium', 'You receive a LinkedIn message from a recruiter at a well-known company offering a job opportunity. They ask you to download and fill out an application form from a Dropbox link.', 'Suspicious', 'unsolicited job offer, external download, Dropbox link', 'Legitimate recruiters from established companies use official application systems. Asking candidates to download forms from personal file-sharing services is suspicious and could contain malware.'),

('Phishing', 'Hard', 'You get an email from Microsoft Security Team using the correct domain @microsoft.com, informing you of suspicious login attempts. The email includes specific details about your recent logins (correct locations and times) and asks you to secure your account by updating your security questions through a link.', 'Suspicious', 'email spoofing with correct domain, specific personal details, security questions via link', 'Advanced phishing can spoof legitimate domains and use publicly available information about you to seem credible. Microsoft never asks users to update security questions via email links. Always access account security directly through the official website.'),

('Phishing', 'Hard', 'Your colleague sends you an email about a shared Google Doc with a View Document button. The email thread includes previous legitimate conversations you''ve received. The sender''s email address matches your colleague''s address exactly.', 'Suspicious', 'email account compromise, legitimate thread, familiar sender', 'This could indicate your colleague''s email was compromised. Even if the sender address looks correct, accounts can be hacked. Before clicking, verify through another communication channel (call, text, Slack) if they actually sent it.'),

('Phishing', 'Hard', 'You receive an automated notification from your company''s expense management system (which you actually use) about a rejected expense report. The email has correct branding, comes from the right domain, and includes a View Details link that goes to a URL resembling your company''s portal with HTTPS.', 'Suspicious', 'system spoofing, HTTPS doesn''t guarantee safety, hover over link reveals different destination', 'Sophisticated phishing can replicate internal systems. The link display text might show the correct URL, but hovering reveals the actual destination is different. HTTPS only means encrypted connection, not website legitimacy. Check the actual URL carefully.'),

-- BAITING SCENARIOS
('Baiting', 'Easy', 'You find a USB drive labeled "Executive Salary Information 2024" in your office parking lot. Your computer is asking if you want to open the removable drive.', 'Suspicious', 'found USB drive, unknown source, tempting label', 'This is classic baiting. USB drives found in public places can contain malware that auto-executes when connected. Attackers use enticing labels to encourage people to plug them in.'),

('Baiting', 'Easy', 'While browsing a website, a pop-up appears saying "Your computer has been infected! Download our FREE antivirus NOW to remove 27 viruses!" with a big Download button.', 'Suspicious', 'scare tactics, pop-up, free antivirus, urgent download', 'Legitimate antivirus software doesn''t advertise via pop-ups claiming your computer is infected. This is scareware/baiting designed to trick you into downloading malware disguised as antivirus software.'),

('Baiting', 'Easy', 'You receive a text message: "Congratulations! You''ve been selected to receive a FREE iPhone 15! Click here to claim your prize now!"', 'Suspicious', 'too good to be true, unsolicited prize, click link', 'Nobody gives away free expensive phones to random people. This is bait to get you to click a malicious link or provide personal information.'),

('Baiting', 'Medium', 'In your office break room, you find a branded USB drive with your company logo and label "Q4 Financial Results - Confidential". It looks professionally made.', 'Suspicious', 'professional looking USB, company branding, confidential label, found device', 'Even professional-looking USB drives found in your workplace can be baiting attacks. Attackers specifically target companies by leaving malware-infected drives on premises. Report found devices to IT security instead of plugging them in.'),

('Baiting', 'Medium', 'You''re on a legitimate software download site, and an ad banner offers "Free PDF Converter - No Email Required! Download Instantly!" The ad looks clean and professional.', 'Suspicious', 'free software offer, no registration, advertisement download', 'While the site itself may be legitimate, ad-based downloads are risky. Attackers often use malvertising (malicious advertising) to distribute malware through ads on legitimate sites. Download software only from official vendor websites.'),

('Baiting', 'Medium', 'At a conference, someone leaves promotional USB drives at each seat with the conference logo and "Presentation Materials Inside". Several colleagues are plugging them in.', 'Suspicious', 'conference USB, seems legitimate, social proof pressure', 'Conference USBs are a known attack vector. Even if others are using them, you should verify with conference organizers that these were official. Attackers exploit conference settings where USB distribution seems normal.'),

('Baiting', 'Hard', 'You''re in a coffee shop and see an unattended charging cable labeled "Free Charging Station - Courtesy of [Coffee Shop Name]." The cable has the coffee shop''s logo printed on it.', 'Suspicious', 'public charging cable, logo makes it seem official, USB data transfer risk', 'Public USB charging cables can be compromised with "juice jacking" - malware that transfers when you connect your device. Even if branded, these could be social engineering. Use your own cable with a wall adapter or power-only USB cables.'),

('Baiting', 'Hard', 'Your company''s IT department sends an email about new security training. The email includes a link to download a "Mandatory Security Awareness Certificate" as a .exe file to install on your computer for compliance tracking.', 'Suspicious', 'IT impersonation, .exe download, seems official but unusual method', 'While IT might send security training, legitimate compliance certificates are never .exe files you download and run. This is likely an attacker impersonating IT to distribute malware. Verify with IT through official channels before downloading executable files.'),

('Baiting', 'Hard', 'You get an email with subject "Your Amazon order has shipped" with a realistic Amazon HTML email template. There''s a "Track Package" button that downloads a .pdf.exe file when clicked. You did order something from Amazon recently.', 'Suspicious', '.exe disguised as PDF, timing matches real order, sophisticated mimicry', 'Attackers time phishing/baiting attacks with common activities like online shopping. The file extension ".pdf.exe" is a classic trick - it appears as PDF but is actually an executable. Amazon tracking links never download executable files.'),

-- PRETEXTING SCENARIOS  
('Pretexting', 'Easy', 'You receive a phone call from someone claiming to be from tech support saying they detected viruses on your computer and need remote access to fix it. They know your name and phone number.', 'Suspicious', 'unsolicited tech support, knows personal info, requests remote access', 'Legitimate tech companies don''t cold-call about virus infections. Knowing your name and number isn''t difficult (public records, data breaches). Never grant remote access to unsolicited callers.'),

('Pretexting', 'Easy', 'Someone calls claiming to be from your bank''s fraud department, mentioning a specific transaction and asking you to verify your account by providing the last 4 digits of your SSN and your PIN.', 'Suspicious', 'requests sensitive info, phone verification, mentions specific transaction', 'Banks never ask for PINs or SSN verification over the phone, even if they mention a real transaction. They can see your account information. This is pretexting to steal credentials.'),

('Pretexting', 'Easy', 'You get a call from "IRS" saying you owe back taxes and will be arrested if you don''t pay immediately via gift cards or wire transfer.', 'Suspicious', 'government impersonation, threats, immediate payment, gift cards', 'The IRS never threatens immediate arrest or requests payment via gift cards/wire transfers. They communicate via official mail first. This is a common pretexting scam using fear tactics.'),

('Pretexting', 'Medium', 'A person calls your office claiming to be from your company''s HR department (different office location) conducting an "employment verification audit." They ask for your employee ID and date of birth to "confirm your records".', 'Suspicious', 'internal department impersonation, requests personal info, verification pretext', 'Even if caller claims to be from your company, verify their identity through official channels before providing personal information. Call HR directly using the number from your company directory, not callback numbers provided by caller.'),

('Pretexting', 'Medium', 'You receive an email from your company''s IT Help Desk asking you to fill out a "Quarterly IT Equipment Survey" via an external Google Form, including questions about your computer specs, software installed, and username.', 'Suspicious', 'IT impersonation, external form, requests technical details', 'While IT might send security training, using external forms for sensitive company information is suspicious. Legitimate internal surveys use company systems. Attackers gather this info for targeted attacks.'),

('Pretexting', 'Medium', 'A LinkedIn connection request from someone claiming to be a recruiter at your dream company. After connecting, they message asking for your current salary information to "see if our opportunity would be a good fit".', 'Suspicious', 'recruiter pretext, requests salary info before job discussion, builds trust via LinkedIn', 'Legitimate recruiters discuss roles before asking salary information. This is information gathering that could be used for social engineering or sold to data brokers. Be cautious about what you share, even on professional networks.'),

('Pretexting', 'Hard', 'You receive a call from someone claiming to be your company''s new IT Security Officer (gives a name you can''t immediately verify). They''re conducting a "security audit" and need your password to "test the strength of our authentication system". They seem knowledgeable about your company structure.', 'Suspicious', 'authority pretext, password request, seems knowledgeable, new employee hard to verify', 'No legitimate security officer ever asks for passwords. Attackers research companies to sound credible and exploit uncertainty about new employees. Even if someone seems official, passwords should never be shared with anyone.'),

('Pretexting', 'Hard', 'A person arrives at your office with a vendor badge claiming to be here for "scheduled network maintenance". They ask to be let into the server room. They carry proper-looking equipment and mention your IT manager''s name.', 'Suspicious', 'physical social engineering, vendor impersonation, dropped names, appears prepared', 'Physical pretexting is dangerous. Even with legitimate-looking badges and equipment, verify all vendor visits with IT/facilities management before granting access. Attackers research staff names and wear convincing costumes.'),

('Pretexting', 'Hard', 'You get a call from your "bank''s fraud department" about suspicious charges. They mention your bank''s name, last 4 of your real account number, and recent legitimate transactions before asking you to verify your identity by providing the code they "just sent to your phone". You do receive a 2FA code text.', 'Suspicious', 'multiple verification factors, real account details, timing of real 2FA, sophisticated pretext', 'Advanced pretexting combines real information (from data breaches) with social engineering. The attacker triggered the real 2FA by trying to log into your account. They''re tricking you into giving them the code to access your account. Never share 2FA codes over phone calls.'),

-- ADDITIONAL SCENARIOS FOR VARIETY
('Phishing', 'Easy', 'Email from "Netflix" saying your payment failed and your account will be suspended unless you update your billing information via the attached link. Sender: billing@netflix-payments.net', 'Suspicious', 'payment failure urgency, wrong domain, suspension threat', 'Netflix uses @netflix.com email addresses. The "-payments.net" domain is fake. Legitimate services notify you through their app/website dashboard, not just email.'),

('Phishing', 'Medium', 'You receive a DocuSign notification to sign an important document. The email looks identical to real DocuSign emails you''ve received before, with correct branding and formatting.', 'Suspicious', 'service impersonation, professional appearance, verify sender domain', 'Always verify the sender domain matches the official service (@docusign.com or @docusign.net). Hover over links to check actual destination URLs. When in doubt, log into DocuSign directly rather than clicking email links.'),

('Baiting', 'Easy', 'A website pop-up offers a "Free VPN Service - Military Grade Encryption!" with immediate download. The site claims 5 million downloads and shows fake trust badges.', 'Suspicious', 'free VPN offer, pop-up, fake trust indicators, too good to be true', 'Free VPN services often contain malware or harvest your data. Fake download counters and trust badges are red flags. Research VPN providers thoroughly before installation.'),

('Pretexting', 'Medium', 'Someone calls claiming to be conducting a survey for your "recent purchase". They ask increasingly personal questions including your full address "to mail you a reward" and credit card type "for demographic research".', 'Suspicious', 'survey pretext, escalating requests, personal information gathering', 'Legitimate surveys don''t need credit card information or extensive personal details. This is pretexting to build a profile for identity theft or targeted attacks.');

-- Default Roles
INSERT INTO roles (role_name, description, is_system_role) VALUES
('Admin', 'Full system access', TRUE),
('Instructor', 'Manage scenarios and view all user progress', TRUE),
('Student', 'Take training scenarios', TRUE);

-- Default Permissions
INSERT INTO permissions (permission_name, resource, action, description) VALUES
('view_dashboard', 'dashboard', 'read', 'View own dashboard'),
('view_all_users', 'users', 'read', 'View all user accounts'),
('manage_users', 'users', 'write', 'Create/edit/delete users'),
('manage_scenarios', 'scenarios', 'write', 'Create/edit scenarios'),
('view_analytics', 'analytics', 'read', 'View analytics dashboard'),
('view_audit_logs', 'audit', 'read', 'View security audit logs');

-- Assign Permissions to Roles
-- Admin gets all permissions
INSERT INTO role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id 
FROM roles r, permissions p 
WHERE r.role_name = 'Admin';

-- Notification Types
INSERT INTO notification_types (type_name, description) VALUES
('achievement_earned', 'User earned an achievement'),
('training_reminder', 'Reminder to continue training'),
('system_alert', 'Important system notification'),
('admin_message', 'Message from administrator');

-- LEGITIMATE SCENARIOS (SAFE)
-- These scenarios are designed to test if users can identify safe communications vs attacks

-- Phishing (Safe)
INSERT INTO scenarios (scenario_type, difficulty_level, scenario_description, correct_answer, keywords_to_identify, explanation) VALUES
('Phishing', 'Easy', 'You requested a password reset for your company account. You receive an email from "noreply@yourcompany.com" immediately after. The email contains a link to "https://sso.yourcompany.com/reset".', 'Legitimate', 'requested action, correct domain, expected timing, https', 'This is a legitimate email because you initiated the action, it comes from the correct internal domain, and the link points to the official SSO portal.'),

('Phishing', 'Easy', 'You receive a monthly newsletter from a service you subscribed to. The sender is "newsletter@industry-news.com". It contains articles and no suspicious attachments or urgent requests.', 'Legitimate', 'subscribed service, no urgency, no suspicious links', 'Regular newsletters from known subscriptions are generally safe. There is no urgency, threats, or requests for sensitive information.'),

('Phishing', 'Medium', 'Your bank sends an email notification that your monthly statement is ready. The email says "Log in to your account to view your statement" and provides NO links, just instructions to go to the website.', 'Legitimate', 'no links, informational only, instructs to use official site', 'This is a security best practice used by many banks. They notify you but do not include clickable links, asking you to navigate to the site yourself. This is safe.'),

('Phishing', 'Medium', 'An email from your project manager (correct email address) asks for a status update on the "Q4 Report". The email references specific details discussed in yesterday''s meeting.', 'Legitimate', 'contextual accuracy, correct sender, normal business request', 'The email contains specific context that would be hard for an attacker to know (details from yesterday''s meeting) and comes from a verified internal address with a reasonable request.'),

('Phishing', 'Hard', 'You receive a security alert from Google saying a new device signed in. You did just sign in from a new tablet. The email comes from "no-reply@accounts.google.com" and details match your action.', 'Legitimate', 'matches user action, correct domain, security notification', 'Security alerts triggered immediately by your own actions are legitimate. Always verify the details (location, device, time) match your actual activity.');

-- Baiting (Safe)
INSERT INTO scenarios (scenario_type, difficulty_level, scenario_description, correct_answer, keywords_to_identify, explanation) VALUES
('Baiting', 'Easy', 'Your IT manager hands you a USB drive labeled "New Employee Handbook" during your orientation session.', 'Legitimate', 'trusted source, physical handover, expected context', 'A USB drive handed directly to you by a known trusted authority (IT Manager) during a specific relevant event (orientation) is generally safe.'),

('Baiting', 'Medium', 'A system notification pops up in the bottom right corner of your Windows desktop saying "Updates are ready to install". It opens the official Windows Update settings window when clicked.', 'Legitimate', 'system notification, opens system settings, no browser popup', 'Native system notifications that open official OS settings windows are legitimate. They are distinct from browser-based popups that mimic system alerts.'),

('Baiting', 'Hard', 'You receive a promotional package at your desk from a known vendor your company works with. It contains a branded power bank and a brochure. There is no USB connection, just power.', 'Legitimate', 'known vendor, physical gift, no data connection', 'Swag from known vendors is common. A power bank without data capabilities (pure charging) poses no digital threat, though physical security policies should always be followed.');

-- Pretexting (Safe)
INSERT INTO scenarios (scenario_type, difficulty_level, scenario_description, correct_answer, keywords_to_identify, explanation) VALUES
('Pretexting', 'Easy', 'HR calls you from the internal extension 5000 (which you recognize as HR). They ask to confirm your mailing address for the holiday gift. They do not ask for passwords or SSN.', 'Legitimate', 'internal extension, recognized number, non-sensitive request', 'Calls from known internal extensions asking for non-critical information (mailing address) are typically legitimate business operations.'),

('Pretexting', 'Medium', 'A vendor arrives at the front desk for a scheduled maintenance visit. Your calendar shows "Printer Maintenance - 2pm". The receptionist calls to confirm he has a valid badge and work order.', 'Legitimate', 'scheduled event, verified credentials, receptionist confirmation', 'The visit was scheduled in your calendar, and the visitor followed proper physical security protocols (checking in at reception, showing badge). This is a legitimate visit.'),

('Pretexting', 'Hard', 'Your manager calls you while on vacation. The caller ID shows their personal cell number (which you have saved). They ask where a specific file is stored on the shared drive.', 'Legitimate', 'known caller ID, reasonable request, context awareness', 'Calls from known contacts (saved in your phone) asking for work-related but non-sensitive information (file location) are legitimate interactions.');

-- ==========================================
-- PATH TO MASTERY - NEW TABLES
-- ==========================================

-- 1. Learning Paths & Levels
CREATE TABLE IF NOT EXISTS learning_paths (
    path_id INT AUTO_INCREMENT PRIMARY KEY,
    path_name VARCHAR(100) NOT NULL,
    description TEXT,
    total_levels INT DEFAULT 4,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS path_levels (
    level_id INT AUTO_INCREMENT PRIMARY KEY,
    path_id INT NOT NULL,
    level_number INT NOT NULL,
    level_name VARCHAR(100) NOT NULL,
    description TEXT,
    unlock_score INT DEFAULT 0,
    FOREIGN KEY (path_id) REFERENCES learning_paths(path_id) ON DELETE CASCADE,
    INDEX idx_path_level (path_id, level_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Categories & Content Types
CREATE TABLE IF NOT EXISTS categories (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(50) UNIQUE NOT NULL,
    icon VARCHAR(50),
    color_code VARCHAR(20),
    description TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS content_types (
    type_id INT AUTO_INCREMENT PRIMARY KEY,
    type_name VARCHAR(20) UNIQUE NOT NULL, -- 'theory', 'practical', 'quiz'
    difficulty_multiplier FLOAT DEFAULT 1.0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Learning Modules (The Core Content)
CREATE TABLE IF NOT EXISTS learning_modules (
    module_id INT AUTO_INCREMENT PRIMARY KEY,
    level_id INT NOT NULL,
    category_id INT NOT NULL,
    type_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    content_json JSON, -- Stores theory text, quiz questions, or scenario data
    points_value INT DEFAULT 100,
    estimated_time_minutes INT DEFAULT 5,
    order_index INT DEFAULT 0,
    FOREIGN KEY (level_id) REFERENCES path_levels(level_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    FOREIGN KEY (type_id) REFERENCES content_types(type_id),
    INDEX idx_level_order (level_id, order_index)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. User Progress Tracking
CREATE TABLE IF NOT EXISTS user_progress (
    progress_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    path_id INT NOT NULL,
    level_id INT NOT NULL,
    module_id INT NOT NULL,
    score INT DEFAULT 0,
    status ENUM('locked', 'unlocked', 'in_progress', 'completed') DEFAULT 'locked',
    completed_at DATETIME,
    first_viewed_at DATETIME,
    last_activity_at DATETIME,
    view_count INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (path_id) REFERENCES learning_paths(path_id),
    FOREIGN KEY (level_id) REFERENCES path_levels(level_id),
    FOREIGN KEY (module_id) REFERENCES learning_modules(module_id),
    UNIQUE KEY unique_user_module (user_id, module_id),
    INDEX idx_user_status (user_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS module_attempts (
    attempt_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    module_id INT NOT NULL,
    attempt_number INT DEFAULT 1,
    score INT,
    time_spent_seconds INT,
    answers_json JSON,
    attempt_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (module_id) REFERENCES learning_modules(module_id),
    INDEX idx_user_module (user_id, module_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 5. Certificates & Gamification
CREATE TABLE IF NOT EXISTS certificates (
    cert_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    path_id INT NOT NULL,
    certificate_code VARCHAR(50) UNIQUE NOT NULL,
    issued_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    verified_score FLOAT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (path_id) REFERENCES learning_paths(path_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS leaderboards (
    rank_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    path_id INT NOT NULL,
    total_score INT DEFAULT 0,
    modules_completed INT DEFAULT 0,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (path_id) REFERENCES learning_paths(path_id),
    UNIQUE KEY unique_user_path (user_id, path_id),
    INDEX idx_score (total_score DESC)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 6. Micro-Lessons & Adaptive Learning
CREATE TABLE IF NOT EXISTS micro_lessons (
    lesson_id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content_text TEXT NOT NULL,
    est_time_minutes INT DEFAULT 5,
    quiz_json JSON NOT NULL, -- Contains 3 MCQs with answers
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES categories(category_id),
    INDEX idx_category (category_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS assigned_lessons (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    lesson_id INT NOT NULL,
    scenario_id INT, -- Which failed scenario triggered this
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

-- SEED DATA FOR STRUCTURE
-- 1. Content Types
INSERT INTO content_types (type_name, difficulty_multiplier) VALUES 
('theory', 1.0),
('practical', 1.5),
('quiz', 1.2);

-- 2. Categories (10 Attack Vectors)
INSERT INTO categories (category_name, icon, color_code, description) VALUES
('Phishing', '🎣', '#FF6B6B', 'Deceptive emails to steal data'),
('Vishing', '📞', '#4ECDC4', 'Voice phishing over phone'),
('Smishing', '📱', '#45B7D1', 'SMS/Text message phishing'),
('Pretexting', '🎭', '#96CEB4', 'Fabricated scenarios to gain trust'),
('Baiting', '🍭', '#FFEEAD', 'False promises to lure victims'),
('Tailgating', '🚪', '#D4A5A5', 'Following authorized personnel'),
('Quid Pro Quo', '🎁', '#9B59B6', 'Service for information exchange'),
('WiFi Evil Twin', '📶', '#3498DB', 'Fake WiFi access points'),
('Honeytraps', '🍯', '#E67E22', 'Romantic/sexual inducement'),
('Insider Threats', '🏢', '#95A5A6', 'Malicious internal actors');

-- 3. Learning Path & Levels
INSERT INTO learning_paths (path_name, description) VALUES 
('Social Engineering Mastery', 'Complete path from novice to expert social engineering defense.');

SET @path_id = LAST_INSERT_ID();

INSERT INTO path_levels (path_id, level_number, level_name, description, unlock_score) VALUES
(@path_id, 1, 'Fundamentals', 'Basic awareness and terminology. (0-25%)', 0),
(@path_id, 2, 'Intermediate', 'Pattern recognition and common attacks. (25-50%)', 500),
(@path_id, 3, 'Advanced', 'Decision making under pressure. (50-75%)', 1500),
(@path_id, 4, 'Expert', 'Prevention strategies and response protocols. (75-100%)', 3000);

