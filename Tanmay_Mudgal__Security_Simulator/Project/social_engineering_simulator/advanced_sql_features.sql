-- Advanced SQL Features: Triggers and Views
-- To be executed after schema.sql

USE social_engineering_db;

-- ==========================================
-- TRIGGERS FOR AUTO-UPDATING TIMESTAMPS
-- ==========================================

-- Trigger to update last_updated in learning_progress
DELIMITER //
CREATE TRIGGER update_learning_progress_timestamp
BEFORE UPDATE ON learning_progress
FOR EACH ROW
BEGIN
    SET NEW.last_updated = CURRENT_TIMESTAMP;
END//
DELIMITER ;

-- Trigger to update updated_date in roles
DELIMITER //
CREATE TRIGGER update_role_timestamp
BEFORE UPDATE ON roles
FOR EACH ROW
BEGIN
    SET NEW.updated_date = CURRENT_TIMESTAMP;
END//
DELIMITER ;

-- Trigger to auto-calculate accuracy when user_response is added
DELIMITER //
CREATE TRIGGER calculate_user_accuracy
AFTER INSERT ON user_responses
FOR EACH ROW
BEGIN
    DECLARE total_responses INT;
    DECLARE correct_responses INT;
    DECLARE new_accuracy FLOAT;
    
    -- Count total and correct responses
    SELECT COUNT(*), SUM(CASE WHEN is_correct = 1 THEN 1 ELSE 0 END)
    INTO total_responses, correct_responses
    FROM user_responses
    WHERE user_id = NEW.user_id;
    
    -- Update user vulnerability level based on accuracy
    SET new_accuracy = (correct_responses / total_responses) * 100;
    
    UPDATE users
    SET vulnerability_level = CASE
        WHEN new_accuracy >= 80 THEN 'Low'
        WHEN new_accuracy >= 50 THEN 'Medium'
        ELSE 'High'
    END
    WHERE user_id = NEW.user_id;
END//
DELIMITER ;

-- Trigger to update leaderboard automatically
DELIMITER //
CREATE TRIGGER update_leaderboard_on_module_completion
AFTER INSERT ON user_progress
FOR EACH ROW
BEGIN
    IF NEW.status = 'completed' THEN
        INSERT INTO leaderboards (user_id, path_id, total_score, modules_completed)
        VALUES (NEW.user_id, NEW.path_id, NEW.score, 1)
        ON DUPLICATE KEY UPDATE
            total_score = total_score + NEW.score,
            modules_completed = modules_completed + 1,
            last_updated = CURRENT_TIMESTAMP;
    END IF;
END//
DELIMITER ;

-- ==========================================
-- VIEWS FOR COMPLEX QUERIES
-- ==========================================

-- View: User Performance Summary
CREATE OR REPLACE VIEW user_performance_summary AS
SELECT 
    u.user_id,
    u.username,
    u.email,
    u.total_score,
    u.vulnerability_level,
    COUNT(ur.response_id) AS total_attempts,
    SUM(CASE WHEN ur.is_correct = 1 THEN 1 ELSE 0 END) AS correct_attempts,
    ROUND((SUM(CASE WHEN ur.is_correct = 1 THEN 1 ELSE 0 END) / COUNT(ur.response_id)) * 100, 2) AS accuracy_percentage,
    AVG(ur.response_time) AS avg_response_time,
    COUNT(DISTINCT a.achievement_id) AS total_achievements,
    u.created_date AS member_since
FROM users u
LEFT JOIN user_responses ur ON u.user_id = ur.user_id
LEFT JOIN achievements a ON u.user_id = a.user_id
GROUP BY u.user_id, u.username, u.email, u.total_score, u.vulnerability_level, u.created_date;

-- View: Scenario Difficulty Analysis
CREATE OR REPLACE VIEW scenario_difficulty_analysis AS
SELECT 
    s.scenario_type,
    s.difficulty_level,
    COUNT(DISTINCT s.scenario_id) AS total_scenarios,
    COUNT(ur.response_id) AS total_attempts,
    SUM(CASE WHEN ur.is_correct = 1 THEN 1 ELSE 0 END) AS correct_responses,
    ROUND((SUM(CASE WHEN ur.is_correct = 1 THEN 1 ELSE 0 END) / COUNT(ur.response_id)) * 100, 2) AS success_rate,
    AVG(ur.response_time) AS avg_response_time
FROM scenarios s
LEFT JOIN user_responses ur ON s.scenario_id = ur.scenario_id
GROUP BY s.scenario_type, s.difficulty_level
ORDER BY s.scenario_type, s.difficulty_level;

-- View: Global Leaderboard (Top 50)
CREATE OR REPLACE VIEW global_leaderboard AS
SELECT 
    ROW_NUMBER() OVER (ORDER BY u.total_score DESC, u.created_date ASC) AS rank,
    u.user_id,
    u.username,
    u.total_score,
    u.vulnerability_level,
    COUNT(DISTINCT ur.response_id) AS scenarios_completed,
    ROUND((SUM(CASE WHEN ur.is_correct = 1 THEN 1 ELSE 0 END) / COUNT(ur.response_id)) * 100, 2) AS accuracy,
    COUNT(DISTINCT a.achievement_id) AS achievements_earned
FROM users u
LEFT JOIN user_responses ur ON u.user_id = ur.user_id
LEFT JOIN achievements a ON u.user_id = a.user_id
GROUP BY u.user_id, u.username, u.total_score, u.vulnerability_level, u.created_date
HAVING scenarios_completed > 0
ORDER BY u.total_score DESC
LIMIT 50;

-- View: Category Performance by User
CREATE OR REPLACE VIEW user_category_performance AS
SELECT 
    u.user_id,
    u.username,
    s.scenario_type AS category,
    COUNT(ur.response_id) AS attempts,
    SUM(CASE WHEN ur.is_correct = 1 THEN 1 ELSE 0 END) AS correct,
    ROUND((SUM(CASE WHEN ur.is_correct = 1 THEN 1 ELSE 0 END) / COUNT(ur.response_id)) * 100, 2) AS accuracy,
    AVG(ur.response_time) AS avg_time
FROM users u
JOIN user_responses ur ON u.user_id = ur.user_id
JOIN scenarios s ON ur.scenario_id = s.scenario_id
GROUP BY u.user_id, u.username, s.scenario_type;

-- View: Learning Path Progress
CREATE OR REPLACE VIEW learning_path_progress_view AS
SELECT 
    u.user_id,
    u.username,
    lp.path_name,
    pl.level_number,
    pl.level_name,
    COUNT(DISTINCT lm.module_id) AS total_modules,
    COUNT(DISTINCT CASE WHEN up.status = 'completed' THEN up.module_id END) AS completed_modules,
    ROUND((COUNT(DISTINCT CASE WHEN up.status = 'completed' THEN up.module_id END) / COUNT(DISTINCT lm.module_id)) * 100, 2) AS completion_percentage,
    SUM(CASE WHEN up.status = 'completed' THEN up.score ELSE 0 END) AS total_points_earned
FROM users u
CROSS JOIN learning_paths lp
CROSS JOIN path_levels pl ON pl.path_id = lp.path_id
LEFT JOIN learning_modules lm ON lm.level_id = pl.level_id
LEFT JOIN user_progress up ON up.module_id = lm.module_id AND up.user_id = u.user_id
GROUP BY u.user_id, u.username, lp.path_name, pl.level_number, pl.level_name
ORDER BY u.user_id, pl.level_number;

-- View: Audit Trail Summary
CREATE OR REPLACE VIEW audit_trail_summary AS
SELECT 
    DATE(al.timestamp) AS date,
    al.action_type,
    al.severity,
    al.status,
    COUNT(*) AS occurrences,
    COUNT(DISTINCT al.user_id) AS unique_users,
    COUNT(DISTINCT al.ip_address) AS unique_ips
FROM audit_logs al
GROUP BY DATE(al.timestamp), al.action_type, al.severity, al.status
ORDER BY date DESC, occurrences DESC;

-- ==========================================
-- DEMONSTRATION QUERIES FOR VIEWS
-- ==========================================

-- Example 1: Get top 10 performers
-- SELECT * FROM global_leaderboard LIMIT 10;

-- Example 2: Get user's weakest category
-- SELECT category, accuracy FROM user_category_performance 
-- WHERE user_id = 1 ORDER BY accuracy ASC LIMIT 1;

-- Example 3: See scenario difficulty vs success rates
-- SELECT * FROM scenario_difficulty_analysis 
-- WHERE scenario_type = 'Phishing' ORDER BY difficulty_level;

-- Example 4: Check user's path completion
-- SELECT * FROM learning_path_progress_view 
-- WHERE user_id = 1 AND path_name = 'Social Engineering Mastery';
