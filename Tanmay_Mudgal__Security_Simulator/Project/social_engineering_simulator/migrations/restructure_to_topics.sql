-- SQL Migration: Create topics and difficulty_levels tables
USE social_engineering_db;

-- Create topics table
CREATE TABLE IF NOT EXISTS topics (
    topic_id INT AUTO_INCREMENT PRIMARY KEY,
    topic_number INT NOT NULL,
    topic_name VARCHAR(100) NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_topic_number (topic_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Create difficulty_levels table  
CREATE TABLE IF NOT EXISTS difficulty_levels (
    difficulty_level_id INT AUTO_INCREMENT PRIMARY KEY,
    topic_id INT NOT NULL,
    level_number INT NOT NULL,
    level_name VARCHAR(50) NOT NULL,
    description TEXT,
    previous_level_id INT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE CASCADE,
    FOREIGN KEY (previous_level_id) REFERENCES difficulty_levels(difficulty_level_id) ON DELETE SET NULL,
    INDEX idx_topic_level (topic_id, level_number)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add new columns to learning_modules
ALTER TABLE learning_modules 
ADD COLUMN difficulty_level_id INT NULL AFTER level_id,
ADD FOREIGN KEY (difficulty_level_id) REFERENCES difficulty_levels(difficulty_level_id) ON DELETE SET NULL;

-- Make level_id nullable for backward compatibility
ALTER TABLE learning_modules MODIFY level_id INT NULL;

-- Add new columns to user_progress
ALTER TABLE user_progress
ADD COLUMN topic_id INT NULL AFTER level_id,
ADD COLUMN difficulty_level_id INT NULL AFTER topic_id,
ADD FOREIGN KEY (topic_id) REFERENCES topics(topic_id) ON DELETE SET NULL,
ADD FOREIGN KEY (difficulty_level_id) REFERENCES difficulty_levels(difficulty_level_id) ON DELETE SET NULL;

-- Make old foreign keys nullable
ALTER TABLE user_progress MODIFY path_id INT NULL;
ALTER TABLE user_progress MODIFY level_id INT NULL;

-- Insert 5 topics
INSERT INTO topics (topic_number, topic_name, description, icon) VALUES
(1, 'Phishing & Variations', 'Learn about phishing attacks, email scams, and social manipulation techniques.', '🎣'),
(2, 'Passwords', 'Password security, authentication best practices, and credential management.', '🔐'),
(3, 'Cloud Security', 'Securing cloud services, data protection, and cloud-based threats.', '☁️'),
(4, 'Ransomware', 'Understanding ransomware attacks, prevention, and response strategies.', '🔒'),
(5, 'Deepfakes', 'AI-generated deepfakes, manipulation detection, and digital forensics.', '🎭')
ON DUPLICATE KEY UPDATE topic_name=VALUES(topic_name);

-- For each topic, create 4 difficulty levels
-- Topic 1: Phishing & Variations
SET @topic1_id = (SELECT topic_id FROM topics WHERE topic_number = 1);
INSERT INTO difficulty_levels (topic_id, level_number, level_name, description, previous_level_id)
SELECT @topic1_id, 1, 'Fundamentals', 'Basic concepts and awareness', NULL
WHERE NOT EXISTS (SELECT 1 FROM difficulty_levels WHERE topic_id = @topic1_id AND level_number = 1);

SET @topic1_level1 = (SELECT difficulty_level_id FROM difficulty_levels WHERE topic_id = @topic1_id AND level_number = 1);
INSERT INTO difficulty_levels (topic_id, level_number, level_name, description, previous_level_id)
SELECT @topic1_id, 2, 'Intermediate', 'Pattern recognition and common attacks', @topic1_level1
WHERE NOT EXISTS (SELECT 1 FROM difficulty_levels WHERE topic_id = @topic1_id AND level_number = 2);

SET @topic1_level2 = (SELECT difficulty_level_id FROM difficulty_levels WHERE topic_id = @topic1_id AND level_number = 2);
INSERT INTO difficulty_levels (topic_id, level_number, level_name, description, previous_level_id)
SELECT @topic1_id, 3, 'Advanced', 'Decision making under pressure', @topic1_level2
WHERE NOT EXISTS (SELECT 1 FROM difficulty_levels WHERE topic_id = @topic1_id AND level_number = 3);

SET @topic1_level3 = (SELECT difficulty_level_id FROM difficulty_levels WHERE topic_id = @topic1_id AND level_number = 3);
INSERT INTO difficulty_levels (topic_id, level_number, level_name, description, previous_level_id)
SELECT @topic1_id, 4, 'Expert', 'Prevention strategies and incident response', @topic1_level3
WHERE NOT EXISTS (SELECT 1 FROM difficulty_levels WHERE topic_id = @topic1_id AND level_number = 4);

-- Topic 2: Passwords
SET @topic2_id = (SELECT topic_id FROM topics WHERE topic_number = 2);

SET @prev_level_id = NULL;
INSERT INTO difficulty_levels (topic_id, level_number, level_name, description, previous_level_id)
SELECT @topic2_id, 1, 'Fundamentals', 'Basic concepts and awareness', @prev_level_id
WHERE NOT EXISTS (SELECT 1 FROM difficulty_levels WHERE topic_id = @topic2_id AND level_number = 1);

SET @prev_level_id = (SELECT difficulty_level_id FROM difficulty_levels WHERE topic_id = @topic2_id AND level_number = 1);
INSERT INTO difficulty_levels (topic_id, level_number, level_name, description, previous_level_id)
SELECT @topic2_id, 2, 'Intermediate', 'Pattern recognition and common attacks', @prev_level_id
WHERE NOT EXISTS (SELECT 1 FROM difficulty_levels WHERE topic_id = @topic2_id AND level_number = 2);

SET @prev_level_id = (SELECT difficulty_level_id FROM difficulty_levels WHERE topic_id = @topic2_id AND level_number = 2);
INSERT INTO difficulty_levels (topic_id, level_number, level_name, description, previous_level_id)
SELECT @topic2_id, 3, 'Advanced', 'Decision making under pressure', @prev_level_id
WHERE NOT EXISTS (SELECT 1 FROM difficulty_levels WHERE topic_id = @topic2_id AND level_number = 3);

SET @prev_level_id = (SELECT difficulty_level_id FROM difficulty_levels WHERE topic_id = @topic2_id AND level_number = 3);
INSERT INTO difficulty_levels (topic_id, level_number, level_name, description, previous_level_id)
SELECT @topic2_id, 4, 'Expert', 'Prevention strategies and incident response', @prev_level_id
WHERE NOT EXISTS (SELECT 1 FROM difficulty_levels WHERE topic_id = @topic2_id AND level_number = 4);

-- Topic 3: Cloud Security
SET @topic3_id = (SELECT topic_id FROM topics WHERE topic_number = 3);

SET @prev_level_id = NULL;
INSERT INTO difficulty_levels (topic_id, level_number, level_name, description, previous_level_id)
SELECT @topic3_id, 1, 'Fundamentals', 'Basic concepts and awareness', @prev_level_id
WHERE NOT EXISTS (SELECT 1 FROM difficulty_levels WHERE topic_id = @topic3_id AND level_number = 1);

SET @prev_level_id = (SELECT difficulty_level_id FROM difficulty_levels WHERE topic_id = @topic3_id AND level_number = 1);
INSERT INTO difficulty_levels (topic_id, level_number, level_name, description, previous_level_id)
SELECT @topic3_id, 2, 'Intermediate', 'Pattern recognition and common attacks', @prev_level_id
WHERE NOT EXISTS (SELECT 1 FROM difficulty_levels WHERE topic_id = @topic3_id AND level_number = 2);

SET @prev_level_id = (SELECT difficulty_level_id FROM difficulty_levels WHERE topic_id = @topic3_id AND level_number = 2);
INSERT INTO difficulty_levels (topic_id, level_number, level_name, description, previous_level_id)
SELECT @topic3_id, 3, 'Advanced', 'Decision making under pressure', @prev_level_id
WHERE NOT EXISTS (SELECT 1 FROM difficulty_levels WHERE topic_id = @topic3_id AND level_number = 3);

SET @prev_level_id = (SELECT difficulty_level_id FROM difficulty_levels WHERE topic_id = @topic3_id AND level_number = 3);
INSERT INTO difficulty_levels (topic_id, level_number, level_name, description, previous_level_id)
SELECT @topic3_id, 4, 'Expert', 'Prevention strategies and incident response', @prev_level_id
WHERE NOT EXISTS (SELECT 1 FROM difficulty_levels WHERE topic_id = @topic3_id AND level_number = 4);

-- Topic 4: Ransomware
SET @topic4_id = (SELECT topic_id FROM topics WHERE topic_number = 4);

SET @prev_level_id = NULL;
INSERT INTO difficulty_levels (topic_id, level_number, level_name, description, previous_level_id)
SELECT @topic4_id, 1, 'Fundamentals', 'Basic concepts and awareness', @prev_level_id
WHERE NOT EXISTS (SELECT 1 FROM difficulty_levels WHERE topic_id = @topic4_id AND level_number = 1);

SET @prev_level_id = (SELECT difficulty_level_id FROM difficulty_levels WHERE topic_id = @topic4_id AND level_number = 1);
INSERT INTO difficulty_levels (topic_id, level_number, level_name, description, previous_level_id)
SELECT @topic4_id, 2, 'Intermediate', 'Pattern recognition and common attacks', @prev_level_id
WHERE NOT EXISTS (SELECT 1 FROM difficulty_levels WHERE topic_id = @topic4_id AND level_number = 2);

SET @prev_level_id = (SELECT difficulty_level_id FROM difficulty_levels WHERE topic_id = @topic4_id AND level_number = 2);
INSERT INTO difficulty_levels (topic_id, level_number, level_name, description, previous_level_id)
SELECT @topic4_id, 3, 'Advanced', 'Decision making under pressure', @prev_level_id
WHERE NOT EXISTS (SELECT 1 FROM difficulty_levels WHERE topic_id = @topic4_id AND level_number = 3);

SET @prev_level_id = (SELECT difficulty_level_id FROM difficulty_levels WHERE topic_id = @topic4_id AND level_number = 3);
INSERT INTO difficulty_levels (topic_id, level_number, level_name, description, previous_level_id)
SELECT @topic4_id, 4, 'Expert', 'Prevention strategies and incident response', @prev_level_id
WHERE NOT EXISTS (SELECT 1 FROM difficulty_levels WHERE topic_id = @topic4_id AND level_number = 4);

-- Topic 5: Deepfakes
SET @topic5_id = (SELECT topic_id FROM topics WHERE topic_number = 5);

SET @prev_level_id = NULL;
INSERT INTO difficulty_levels (topic_id, level_number, level_name, description, previous_level_id)
SELECT @topic5_id, 1, 'Fundamentals', 'Basic concepts and awareness', @prev_level_id
WHERE NOT EXISTS (SELECT 1 FROM difficulty_levels WHERE topic_id = @topic5_id AND level_number = 1);

SET @prev_level_id = (SELECT difficulty_level_id FROM difficulty_levels WHERE topic_id = @topic5_id AND level_number = 1);
INSERT INTO difficulty_levels (topic_id, level_number, level_name, description, previous_level_id)
SELECT @topic5_id, 2, 'Intermediate', 'Pattern recognition and common attacks', @prev_level_id
WHERE NOT EXISTS (SELECT 1 FROM difficulty_levels WHERE topic_id = @topic5_id AND level_number = 2);

SET @prev_level_id = (SELECT difficulty_level_id FROM difficulty_levels WHERE topic_id = @topic5_id AND level_number = 2);
INSERT INTO difficulty_levels (topic_id, level_number, level_name, description, previous_level_id)
SELECT @topic5_id, 3, 'Advanced', 'Decision making under pressure', @prev_level_id
WHERE NOT EXISTS (SELECT 1 FROM difficulty_levels WHERE topic_id = @topic5_id AND level_number = 3);

SET @prev_level_id = (SELECT difficulty_level_id FROM difficulty_levels WHERE topic_id = @topic5_id AND level_number = 3);
INSERT INTO difficulty_levels (topic_id, level_number, level_name, description, previous_level_id)
SELECT @topic5_id, 4, 'Expert', 'Prevention strategies and incident response', @prev_level_id
WHERE NOT EXISTS (SELECT 1 FROM difficulty_levels WHERE topic_id = @topic5_id AND level_number = 4);

-- Migrate existing modules to Fundamentals level of each topic
-- Topic 1 (Phishing) - from old level 1
UPDATE learning_modules lm
SET lm.difficulty_level_id = (
    SELECT dl.difficulty_level_id 
    FROM difficulty_levels dl 
    WHERE dl.topic_id = @topic1_id AND dl.level_number = 1
)
WHERE lm.level_id = 1 AND lm.difficulty_level_id IS NULL;

-- Topic 2 (Passwords) - from old level 2
UPDATE learning_modules lm
SET lm.difficulty_level_id = (
    SELECT dl.difficulty_level_id 
    FROM difficulty_levels dl 
    WHERE dl.topic_id = @topic2_id AND dl.level_number = 1
)
WHERE lm.level_id = 2 AND lm.difficulty_level_id IS NULL;

-- Topic 3 (Cloud Security) - from old level 3
UPDATE learning_modules lm
SET lm.difficulty_level_id = (
    SELECT dl.difficulty_level_id 
    FROM difficulty_levels dl 
    WHERE dl.topic_id = @topic3_id AND dl.level_number = 1
)
WHERE lm.level_id = 3 AND lm.difficulty_level_id IS NULL;

-- Topic 4 (Ransomware) - from old level 4
UPDATE learning_modules lm
SET lm.difficulty_level_id = (
    SELECT dl.difficulty_level_id 
    FROM difficulty_levels dl 
    WHERE dl.topic_id = @topic4_id AND dl.level_number = 1
)
WHERE lm.level_id = 4 AND lm.difficulty_level_id IS NULL;

-- Update user progress
UPDATE user_progress up
JOIN learning_modules lm ON up.module_id = lm.module_id
JOIN difficulty_levels dl ON lm.difficulty_level_id = dl.difficulty_level_id
SET up.difficulty_level_id = dl.difficulty_level_id,
    up.topic_id = dl.topic_id
WHERE lm.difficulty_level_id IS NOT NULL;

SELECT 'Migration complete!' AS status;
SELECT COUNT(*) AS topic_count FROM topics;
SELECT COUNT(*) AS difficulty_levels_count FROM difficulty_levels;
SELECT COUNT(*) AS migrated_modules FROM learning_modules WHERE difficulty_level_id IS NOT NULL;
