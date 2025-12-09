-- Fix admin user password hash
-- Update the admin user with correct werkzeug password hash

USE social_engineering_db;

-- Update admin user password with correct werkzeug hash  
-- Password: Admin@2025!
UPDATE users 
SET password = 'scrypt:32768:8:1$v8a1F9Epm97GIsEr$6bd5debca2e09bfa24206fe0aed416a2a53368edf0b57afd035252fc32d7e9edc51b23e60ac5e8555ff2ce7efcc0c43f033c40e4dc37cd48b59050fceac03643'
WHERE username = 'admin';

-- Verify the update
SELECT username, email, LEFT(password, 50) as password_preview 
FROM users 
WHERE username = 'admin';
