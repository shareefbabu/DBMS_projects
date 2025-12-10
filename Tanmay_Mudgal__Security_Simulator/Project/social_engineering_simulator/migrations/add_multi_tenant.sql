-- Multi-Tenant Organization System
-- All foreign keys are NULLABLE - organization membership is optional

USE social_engineering_db;

-- =============================================
-- Create Organizations Table
-- =============================================
CREATE TABLE IF NOT EXISTS organizations (
    org_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    logo_url VARCHAR(255),
    primary_color VARCHAR(7) DEFAULT '#06b6d4',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    INDEX idx_name (name),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- Create Departments Table
-- =============================================
CREATE TABLE IF NOT EXISTS departments (
    dept_id INT AUTO_INCREMENT PRIMARY KEY,
    org_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (org_id) REFERENCES organizations(org_id) ON DELETE CASCADE,
    UNIQUE KEY unique_dept_per_org (org_id, name),
    INDEX idx_org_id (org_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- Create Teams Table
-- =============================================
CREATE TABLE IF NOT EXISTS teams (
    team_id INT AUTO_INCREMENT PRIMARY KEY,
    dept_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    team_lead_user_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE CASCADE,
    FOREIGN KEY (team_lead_user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    UNIQUE KEY unique_team_per_dept (dept_id, name),
    INDEX idx_dept_id (dept_id),
    INDEX idx_team_lead (team_lead_user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =============================================
-- Add Columns to Users Table (NULLABLE)
-- =============================================
ALTER TABLE users
    ADD COLUMN org_id INT NULL,
    ADD COLUMN dept_id INT NULL,
    ADD COLUMN team_id INT NULL;

-- Add indexes for better query performance
ALTER TABLE users
    ADD INDEX idx_org_id (org_id),
    ADD INDEX idx_dept_id (dept_id),
    ADD INDEX idx_team_id (team_id);

-- Add foreign key constraints
ALTER TABLE users
    ADD CONSTRAINT fk_users_org FOREIGN KEY (org_id) REFERENCES organizations(org_id) ON DELETE SET NULL,
    ADD CONSTRAINT fk_users_dept FOREIGN KEY (dept_id) REFERENCES departments(dept_id) ON DELETE SET NULL,
    ADD CONSTRAINT fk_users_team FOREIGN KEY (team_id) REFERENCES teams(team_id) ON DELETE SET NULL;

-- =============================================
-- Optional: Migrate existing organization data
-- Comment out if you don't want to migrate old data
-- =============================================

-- Create organizations from existing unique organization names
INSERT IGNORE INTO organizations (name, created_at)
SELECT DISTINCT CAST(organization AS CHAR(100) CHARACTER SET utf8mb4), NOW()
FROM users
WHERE organization IS NOT NULL 
  AND organization != '';

-- Link users to created organizations  
UPDATE users u
INNER JOIN organizations o ON CAST(u.organization AS CHAR(100) CHARACTER SET utf8mb4) = o.name
SET u.org_id = o.org_id
WHERE u.organization IS NOT NULL AND u.organization != '';

-- =============================================
-- Insert Sample Data (Optional)
-- =============================================

-- Sample Organization
INSERT INTO organizations (name, primary_color, is_active) VALUES
('Demo Corporation', '#f59e0b', TRUE);

-- Sample Departments  
INSERT INTO departments (org_id, name, description) VALUES
(1, 'Engineering', 'Technology and Development'),
(1, 'Sales', 'Sales and Business Development'),
(1, 'HR', 'Human Resources');

-- Sample Teams
INSERT INTO teams (dept_id, name, description) VALUES
(1, 'Backend Team', 'Backend development team'),
(1, 'Frontend Team', 'Frontend development team'),
(2, 'Enterprise Sales', 'Enterprise sales team');

-- =============================================
-- Verification Queries
-- =============================================

SELECT 'Organizations Created:' as Info;
SELECT * FROM organizations;

SELECT 'Departments Created:' as Info;
SELECT d.dept_id, d.name, o.name as organization
FROM departments d
JOIN organizations o ON d.org_id = o.org_id;

SELECT 'Teams Created:' as Info;
SELECT t.team_id, t.name, d.name as department, o.name as organization
FROM teams t
JOIN departments d ON t.dept_id = d.dept_id
JOIN organizations o ON d.org_id = o.org_id;

SELECT 'User Organization Assignment:' as Info;
SELECT 
    COUNT(*) as total_users,
    SUM(CASE WHEN org_id IS NOT NULL THEN 1 ELSE 0 END) as users_with_org,
    SUM(CASE WHEN org_id IS NULL THEN 1 ELSE 0 END) as individual_users
FROM users;
