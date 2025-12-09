-- ================================================
-- Migration: Add Activity Tracking Columns
-- Database: social_engineering_db
-- Table: user_progress
-- ================================================

USE social_engineering_db;

-- Add the three new columns for tracking user activity
ALTER TABLE user_progress 
ADD COLUMN IF NOT EXISTS first_viewed_at DATETIME NULL COMMENT 'Timestamp when user first viewed this module',
ADD COLUMN IF NOT EXISTS last_activity_at DATETIME NULL COMMENT 'Timestamp of last interaction with this module',
ADD COLUMN IF NOT EXISTS view_count INT DEFAULT 0 COMMENT 'Number of times user has viewed this module';

-- Verify the changes
SELECT 'Migration completed successfully!' AS status;
DESCRIBE user_progress;
