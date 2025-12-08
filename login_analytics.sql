-- ============================================================
-- LOGIN RECORDS ANALYTICS QUERIES
-- ============================================================
-- Comprehensive SQL queries for analyzing login data
-- Run these in MySQL Workbench or command line
-- ============================================================

USE FlightBookingDB;

-- ============================================================
-- 1. BASIC OVERVIEW
-- ============================================================

-- View all login records
SELECT 
    lr.record_id,
    lr.email,
    u.name AS user_name,
    lr.login_timestamp,
    lr.logout_timestamp,
    lr.login_status,
    lr.session_duration,
    lr.device_type,
    lr.ip_address
FROM login_records lr
LEFT JOIN Users u ON lr.user_id = u.user_id
ORDER BY lr.login_timestamp DESC
LIMIT 20;

-- Count total login records
SELECT COUNT(*) AS total_login_records FROM login_records;

-- ============================================================
-- 2. LOGIN STATUS ANALYSIS
-- ============================================================

-- Login success rate
SELECT 
    login_status,
    COUNT(*) AS count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM login_records), 2) AS percentage
FROM login_records
GROUP BY login_status
ORDER BY count DESC;

-- Failed login attempts (Security alert)
SELECT 
    email,
    COUNT(*) AS failed_attempts,
    MAX(login_timestamp) AS last_failed_attempt,
    GROUP_CONCAT(DISTINCT ip_address) AS ip_addresses
FROM login_records
WHERE login_status = 'Failed'
GROUP BY email
HAVING failed_attempts >= 2
ORDER BY failed_attempts DESC;

-- Recent failed logins (Last 24 hours)
SELECT 
    email,
    login_timestamp,
    ip_address,
    user_agent
FROM login_records
WHERE login_status = 'Failed'
  AND login_timestamp >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
ORDER BY login_timestamp DESC;

-- ============================================================
-- 3. USER ACTIVITY ANALYSIS
-- ============================================================

-- Most active users
SELECT 
    u.name,
    u.email,
    COUNT(*) AS total_logins,
    MAX(lr.login_timestamp) AS last_login,
    ROUND(AVG(lr.session_duration / 60), 2) AS avg_session_minutes
FROM login_records lr
JOIN Users u ON lr.user_id = u.user_id
WHERE lr.login_status = 'Success'
GROUP BY u.user_id, u.name, u.email
ORDER BY total_logins DESC
LIMIT 10;

-- Users who haven't logged in recently
SELECT 
    u.user_id,
    u.name,
    u.email,
    MAX(lr.login_timestamp) AS last_login,
    DATEDIFF(NOW(), MAX(lr.login_timestamp)) AS days_since_login
FROM Users u
LEFT JOIN login_records lr ON u.user_id = lr.user_id
GROUP BY u.user_id, u.name, u.email
HAVING last_login IS NULL OR days_since_login > 30
ORDER BY days_since_login DESC;

-- Currently active sessions
SELECT 
    lr.email,
    u.name,
    lr.login_timestamp,
    TIMESTAMPDIFF(MINUTE, lr.login_timestamp, NOW()) AS minutes_active,
    lr.device_type,
    lr.ip_address
FROM login_records lr
JOIN Users u ON lr.user_id = u.user_id
WHERE lr.logout_timestamp IS NULL
  AND lr.login_status = 'Success'
ORDER BY lr.login_timestamp DESC;

-- ============================================================
-- 4. TIME-BASED ANALYSIS
-- ============================================================

-- Login activity by date (Last 30 days)
SELECT 
    DATE(login_timestamp) AS login_date,
    COUNT(*) AS total_logins,
    SUM(CASE WHEN login_status = 'Success' THEN 1 ELSE 0 END) AS successful_logins,
    SUM(CASE WHEN login_status = 'Failed' THEN 1 ELSE 0 END) AS failed_logins,
    COUNT(DISTINCT user_id) AS unique_users
FROM login_records
WHERE login_timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
GROUP BY DATE(login_timestamp)
ORDER BY login_date DESC;

-- Login activity by hour of day
SELECT 
    HOUR(login_timestamp) AS hour_of_day,
    COUNT(*) AS login_count,
    ROUND(AVG(session_duration / 60), 2) AS avg_session_minutes
FROM login_records
WHERE login_status = 'Success'
GROUP BY HOUR(login_timestamp)
ORDER BY hour_of_day;

-- Login activity by day of week
SELECT 
    DAYNAME(login_timestamp) AS day_of_week,
    COUNT(*) AS login_count,
    ROUND(AVG(session_duration / 60), 2) AS avg_session_minutes
FROM login_records
WHERE login_status = 'Success'
GROUP BY DAYOFWEEK(login_timestamp), DAYNAME(login_timestamp)
ORDER BY DAYOFWEEK(login_timestamp);

-- ============================================================
-- 5. DEVICE & PLATFORM ANALYSIS
-- ============================================================

-- Login distribution by device type
SELECT 
    device_type,
    COUNT(*) AS login_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM login_records), 2) AS percentage,
    ROUND(AVG(session_duration / 60), 2) AS avg_session_minutes
FROM login_records
WHERE login_status = 'Success'
GROUP BY device_type
ORDER BY login_count DESC;

-- Browser/Platform analysis (extracted from user_agent)
SELECT 
    CASE 
        WHEN user_agent LIKE '%Windows%' THEN 'Windows'
        WHEN user_agent LIKE '%Mac OS%' THEN 'macOS'
        WHEN user_agent LIKE '%Linux%' THEN 'Linux'
        WHEN user_agent LIKE '%Android%' THEN 'Android'
        WHEN user_agent LIKE '%iPhone%' OR user_agent LIKE '%iPad%' THEN 'iOS'
        ELSE 'Other'
    END AS platform,
    COUNT(*) AS login_count
FROM login_records
GROUP BY platform
ORDER BY login_count DESC;

-- ============================================================
-- 6. SESSION ANALYSIS
-- ============================================================

-- Average session duration by device
SELECT 
    device_type,
    COUNT(*) AS session_count,
    ROUND(AVG(session_duration / 60), 2) AS avg_minutes,
    ROUND(MIN(session_duration / 60), 2) AS min_minutes,
    ROUND(MAX(session_duration / 60), 2) AS max_minutes
FROM login_records
WHERE session_duration > 0 AND login_status = 'Success'
GROUP BY device_type
ORDER BY avg_minutes DESC;

-- Session duration distribution
SELECT 
    CASE 
        WHEN session_duration < 300 THEN '< 5 minutes'
        WHEN session_duration < 1800 THEN '5-30 minutes'
        WHEN session_duration < 3600 THEN '30-60 minutes'
        WHEN session_duration < 7200 THEN '1-2 hours'
        ELSE '> 2 hours'
    END AS duration_range,
    COUNT(*) AS session_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM login_records WHERE session_duration > 0), 2) AS percentage
FROM login_records
WHERE session_duration > 0
GROUP BY duration_range
ORDER BY MIN(session_duration);

-- Longest sessions
SELECT 
    u.name,
    lr.email,
    lr.login_timestamp,
    lr.logout_timestamp,
    ROUND(lr.session_duration / 3600, 2) AS hours,
    lr.device_type
FROM login_records lr
LEFT JOIN Users u ON lr.user_id = u.user_id
WHERE lr.session_duration > 0
ORDER BY lr.session_duration DESC
LIMIT 10;

-- ============================================================
-- 7. SECURITY & ANOMALY DETECTION
-- ============================================================

-- Multiple login attempts from different IPs (Suspicious)
SELECT 
    email,
    COUNT(DISTINCT ip_address) AS different_ips,
    COUNT(*) AS total_attempts,
    GROUP_CONCAT(DISTINCT ip_address) AS ip_list
FROM login_records
WHERE login_timestamp >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
GROUP BY email
HAVING different_ips > 3
ORDER BY different_ips DESC;

-- Login attempts outside business hours (Monitoring)
SELECT 
    email,
    login_timestamp,
    HOUR(login_timestamp) AS hour,
    login_status,
    ip_address
FROM login_records
WHERE (HOUR(login_timestamp) < 6 OR HOUR(login_timestamp) > 22)
  AND login_timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)
ORDER BY login_timestamp DESC;

-- Timeout sessions (May indicate issues)
SELECT 
    email,
    login_timestamp,
    device_type,
    user_agent
FROM login_records
WHERE login_status = 'Timeout'
ORDER BY login_timestamp DESC
LIMIT 20;

-- ============================================================
-- 8. GEOGRAPHIC ANALYSIS (by location field)
-- ============================================================

-- Login distribution by location
SELECT 
    location,
    COUNT(*) AS login_count,
    COUNT(DISTINCT email) AS unique_users
FROM login_records
WHERE location IS NOT NULL AND location != 'Unknown'
GROUP BY location
ORDER BY login_count DESC;

-- ============================================================
-- 9. USER ENGAGEMENT METRICS
-- ============================================================

-- User engagement score (Login frequency + session duration)
SELECT 
    u.name,
    u.email,
    COUNT(*) AS total_logins,
    ROUND(AVG(lr.session_duration / 60), 2) AS avg_session_minutes,
    MAX(lr.login_timestamp) AS last_login,
    DATEDIFF(NOW(), MIN(lr.login_timestamp)) AS days_as_user,
    ROUND(COUNT(*) / GREATEST(DATEDIFF(NOW(), MIN(lr.login_timestamp)), 1), 2) AS logins_per_day
FROM login_records lr
JOIN Users u ON lr.user_id = u.user_id
WHERE lr.login_status = 'Success'
GROUP BY u.user_id, u.name, u.email
ORDER BY logins_per_day DESC
LIMIT 20;

-- First vs Recent login comparison
SELECT 
    u.name,
    u.email,
    MIN(lr.login_timestamp) AS first_login,
    MAX(lr.login_timestamp) AS last_login,
    COUNT(*) AS total_logins,
    DATEDIFF(MAX(lr.login_timestamp), MIN(lr.login_timestamp)) AS active_days
FROM login_records lr
JOIN Users u ON lr.user_id = u.user_id
WHERE lr.login_status = 'Success'
GROUP BY u.user_id, u.name, u.email
HAVING total_logins > 1
ORDER BY last_login DESC;

-- ============================================================
-- 10. QUICK STATS DASHBOARD
-- ============================================================

-- Complete overview (run this for quick dashboard)
SELECT 
    (SELECT COUNT(*) FROM login_records) AS total_records,
    (SELECT COUNT(*) FROM login_records WHERE login_status = 'Success') AS successful_logins,
    (SELECT COUNT(*) FROM login_records WHERE login_status = 'Failed') AS failed_logins,
    (SELECT COUNT(*) FROM login_records WHERE login_status = 'Timeout') AS timeout_sessions,
    (SELECT COUNT(DISTINCT user_id) FROM login_records WHERE user_id IS NOT NULL) AS unique_users,
    (SELECT COUNT(*) FROM login_records WHERE logout_timestamp IS NULL AND login_status = 'Success') AS active_sessions,
    (SELECT ROUND(AVG(session_duration / 60), 2) FROM login_records WHERE session_duration > 0) AS avg_session_minutes,
    (SELECT COUNT(*) FROM login_records WHERE DATE(login_timestamp) = CURDATE()) AS logins_today,
    (SELECT COUNT(*) FROM login_records WHERE login_timestamp >= DATE_SUB(NOW(), INTERVAL 7 DAY)) AS logins_this_week,
    (SELECT COUNT(*) FROM login_records WHERE login_timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)) AS logins_this_month;

-- ============================================================
-- 11. MAINTENANCE QUERIES
-- ============================================================

-- Delete records older than 90 days
-- DELETE FROM login_records WHERE login_timestamp < DATE_SUB(NOW(), INTERVAL 90 DAY);

-- Delete all failed login attempts older than 30 days
-- DELETE FROM login_records WHERE login_status = 'Failed' AND login_timestamp < DATE_SUB(NOW(), INTERVAL 30 DAY);

-- Update logout timestamp for stale sessions (older than 24 hours)
-- UPDATE login_records 
-- SET logout_timestamp = DATE_ADD(login_timestamp, INTERVAL 24 HOUR),
--     session_duration = 86400
-- WHERE logout_timestamp IS NULL 
--   AND login_timestamp < DATE_SUB(NOW(), INTERVAL 24 HOUR);

-- ============================================================
-- 12. EXPORT QUERIES (For Reports)
-- ============================================================

-- Monthly login report
SELECT 
    DATE_FORMAT(login_timestamp, '%Y-%m') AS month,
    COUNT(*) AS total_logins,
    COUNT(DISTINCT user_id) AS unique_users,
    ROUND(AVG(session_duration / 60), 2) AS avg_session_minutes,
    SUM(CASE WHEN login_status = 'Success' THEN 1 ELSE 0 END) AS successful,
    SUM(CASE WHEN login_status = 'Failed' THEN 1 ELSE 0 END) AS failed
FROM login_records
GROUP BY DATE_FORMAT(login_timestamp, '%Y-%m')
ORDER BY month DESC;

-- User activity report (Last 30 days)
SELECT 
    u.user_id,
    u.name,
    u.email,
    COUNT(*) AS login_count,
    MAX(lr.login_timestamp) AS last_login,
    ROUND(AVG(lr.session_duration / 60), 2) AS avg_session_minutes,
    GROUP_CONCAT(DISTINCT lr.device_type) AS devices_used
FROM Users u
LEFT JOIN login_records lr ON u.user_id = lr.user_id 
    AND lr.login_timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
    AND lr.login_status = 'Success'
GROUP BY u.user_id, u.name, u.email
ORDER BY login_count DESC;

-- ============================================================
-- END OF ANALYTICS QUERIES
-- ============================================================
