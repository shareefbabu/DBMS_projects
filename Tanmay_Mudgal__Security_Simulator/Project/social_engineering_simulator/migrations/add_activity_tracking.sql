-- Migration script to add activity tracking columns to existing user_progress table
-- Run this if the database already exists with the old schema

USE social_engineering_db;

ALTER TABLE user_progress 
ADD COLUMN first_viewed_at DATETIME NULL AFTER completed_at,
ADD COLUMN last_activity_at DATETIME NULL AFTER first_viewed_at,
ADD COLUMN view_count INT DEFAULT 0 AFTER last_activity_at;

-- Verify the changes
DESCRIBE user_progress;
