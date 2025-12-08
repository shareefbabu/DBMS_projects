-- =====================================================
-- Password Reset Tokens Table Schema
-- =====================================================
-- This table stores secure tokens for password reset functionality
-- Tokens expire after 1 hour and can only be used once

USE FlightBookingDB;

-- Drop table if it exists (for clean reinstallation)
DROP TABLE IF EXISTS password_reset_tokens;

-- Create password_reset_tokens table
CREATE TABLE password_reset_tokens (
    token_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    email VARCHAR(255) NOT NULL,
    reset_token VARCHAR(64) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    is_used BOOLEAN DEFAULT FALSE,
    used_at TIMESTAMP NULL,
    
    -- Foreign key constraint to Users table
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE,
    
    -- Index for faster lookups
    INDEX idx_reset_token (reset_token),
    INDEX idx_email (email),
    INDEX idx_expires_at (expires_at),
    INDEX idx_is_used (is_used)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =====================================================
-- Sample Usage Queries
-- =====================================================

-- Query to check active tokens for a user
-- SELECT * FROM password_reset_tokens 
-- WHERE email = 'user@example.com' 
-- AND is_used = FALSE 
-- AND expires_at > NOW()
-- ORDER BY created_at DESC;

-- Query to cleanup expired tokens
-- DELETE FROM password_reset_tokens 
-- WHERE expires_at < NOW() OR is_used = TRUE;

-- Query to get password reset statistics
-- SELECT 
--     DATE(created_at) as reset_date,
--     COUNT(*) as total_requests,
--     SUM(CASE WHEN is_used = TRUE THEN 1 ELSE 0 END) as successful_resets,
--     SUM(CASE WHEN is_used = FALSE AND expires_at < NOW() THEN 1 ELSE 0 END) as expired_tokens
-- FROM password_reset_tokens
-- GROUP BY DATE(created_at)
-- ORDER BY reset_date DESC;

-- =====================================================
-- Verification Query
-- =====================================================
-- Run this to verify the table was created successfully
DESCRIBE password_reset_tokens;

SELECT 'Password reset tokens table created successfully!' as status;
