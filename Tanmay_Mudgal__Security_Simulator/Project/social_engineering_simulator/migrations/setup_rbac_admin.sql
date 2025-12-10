-- Update existing roles to match RBAC requirements
-- and create admin user

USE social_engineering_db;

-- Update existing roles to new naming convention
UPDATE roles SET role_name = 'GLOBAL_ADMIN', description = 'Full system access, manage all organizations' WHERE role_name = 'Admin';
UPDATE roles SET role_name = 'ORG_ADMIN', description = 'Manage users and campaigns within organization' WHERE role_name = 'Instructor';
UPDATE roles SET role_name = 'LEARNER', description = 'Regular user, access learning modules and simulations' WHERE role_name = 'Student';

-- Add missing permissions if they don't exist
INSERT IGNORE INTO permissions (permission_name, resource, action, description) VALUES
('manage_organizations', 'organizations', 'write', 'Create and manage organizations'),
('manage_campaigns', 'campaigns', 'write', 'Create and manage phishing campaigns'),
('view_org_analytics', 'analytics', 'read', 'View organization-level analytics'),
('access_learning', 'learning', 'read', 'Access learning modules'),
('take_assessments', 'assessments', 'write', 'Take phishing simulations');

-- Ensure GLOBAL_ADMIN has all permissions
INSERT IGNORE INTO role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id 
FROM roles r, permissions p 
WHERE r.role_name = 'GLOBAL_ADMIN';

-- Assign permissions to ORG_ADMIN
INSERT IGNORE INTO role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id 
FROM roles r, permissions p 
WHERE r.role_name = 'ORG_ADMIN'
AND p.permission_name IN ('manage_users', 'manage_campaigns',  'view_org_analytics', 'view_analytics', 'manage_scenarios');

-- Assign permissions to LEARNER
INSERT IGNORE INTO role_permissions (role_id, permission_id)
SELECT r.role_id, p.permission_id 
FROM roles r, permissions p 
WHERE r.role_name = 'LEARNER'
AND p.permission_name IN ('view_dashboard', 'access_learning', 'take_assessments');

-- Create admin user if doesn't exist
INSERT INTO users (username, password, email, organization, account_type, created_date, total_score, vulnerability_level)
SELECT 'admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYr5rzOKPJ.', 'admin@secsimulator.local', 'System', 'Admin', NOW(), 0, 'Low'
WHERE NOT EXISTS (SELECT 1 FROM users WHERE username = 'admin');

-- Assign GLOBAL_ADMIN role to admin user
INSERT INTO user_roles (user_id, role_id, assigned_date)
SELECT u.user_id, r.role_id, NOW()
FROM users u, roles r
WHERE u.username = 'admin' 
AND r.role_name = 'GLOBAL_ADMIN'
AND NOT EXISTS (
    SELECT 1 FROM user_roles ur 
    WHERE ur.user_id = u.user_id AND ur.role_id = r.role_id
);

-- Assign LEARNER role to all existing users who don't have a role
INSERT INTO user_roles (user_id, role_id, assigned_date)
SELECT u.user_id, r.role_id, NOW()
FROM users u
CROSS JOIN roles r
WHERE r.role_name = 'LEARNER'
AND u.username != 'admin'
AND NOT EXISTS (
    SELECT 1 FROM user_roles ur WHERE ur.user_id = u.user_id
);

-- Verify results
SELECT 'Roles:' as Info;
SELECT * FROM roles;

SELECT 'Admin User:' as Info;
SELECT u.username, u.email, r.role_name 
FROM users u
LEFT JOIN user_roles ur ON u.user_id = ur.user_id
LEFT JOIN roles r ON ur.role_id = r.role_id
WHERE u.username = 'admin';

SELECT 'Permissions Count:' as Info;
SELECT COUNT(*) as total_permissions FROM permissions;
