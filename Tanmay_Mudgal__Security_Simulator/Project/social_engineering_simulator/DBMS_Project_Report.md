# Social Engineering Training Simulator - Database Management System Report

## Executive Summary

This report provides a comprehensive analysis of the Database Management System (DBMS) implementation for the Social Engineering Training Simulator. The project utilizes **MySQL 8.0** as its relational database management system, featuring a sophisticated schema design that supports advanced security training, adaptive learning, role-based access control, and comprehensive audit logging.

---

## 1. Database Architecture Overview

### 1.1 Technology Stack
- **DBMS**: MySQL 8.0 / MariaDB
- **Storage Engine**: InnoDB (ACID compliant, supports transactions and foreign keys)
- **Character Set**: UTF8MB4 with unicode_ci collation (full Unicode support including emojis)
- **ORM**: SQLAlchemy (Python-based Object-Relational Mapping)

### 1.2 Core Design Principles
1. **Data Integrity**: Enforced through foreign key constraints and CASCADE/SET NULL behaviors
2. **Normalization**: Follows 3NF (Third Normal Form) to minimize redundancy
3. **Scalability**: Indexed columns for optimized query performance
4. **Audit Trail**: Comprehensive logging of all user actions
5. **Security**: RBAC (Role-Based Access Control) implementation
6. **Adaptability**: JSON columns for flexible content storage

---

## 2. Database Schema Architecture

### 2.1 Schema Components (22 Tables)

The database consists of **22 interconnected tables** organized into functional modules:

#### **Module 1: Core User Management (5 tables)**
- `users` - User accounts and profiles
- `roles` - System and custom roles
- `permissions` - Granular access permissions
- `user_roles` - User-role mappings (many-to-many)
- `role_permissions` - Role-permission mappings (many-to-many)

#### **Module 2: Security Simulation Engine (3 tables)**
- `scenarios` - Training scenarios (Phishing, Vishing, Pretexting, Baiting)
- `user_responses` - User answers to scenarios
- `learning_progress` - Success rates by attack type

#### **Module 3: Structured Learning Path (7 tables)**
- `learning_paths` - Learning path definitions
- `path_levels` - Progressive difficulty levels
- `categories` - Attack vector categories (10 types)
- `content_types` - Module types (Theory, Practical, Quiz)
- `learning_modules` - Individual learning units
- `user_progress` - Module completion tracking
- `module_attempts` - Detailed attempt history

#### **Module 4: Adaptive Micro-Lessons (2 tables)**
- `micro_lessons` - Targeted remedial content
- `assigned_lessons` - Personalized lesson assignments

#### **Module 5: Gamification & Recognition (3 tables)**
- `achievements` - User achievements and badges
- `certificates` - Completion certificates
- `leaderboards` - Competitive rankings

#### **Module 6: Enterprise Features (7 tables)**
- `response_details` - Granular response logging
- `scenario_progress` - Partial completion tracking
- `notification_types` - Notification templates
- `notifications` - User notifications
- `notification_history` - Notification state changes
- `audit_logs` - Security audit trail

---

## 3. Advanced Database Features

### 3.1 JSON Column Usage

JSON columns provide schema flexibility for dynamic content storage:

**`content_json` in `learning_modules`:**
```json
{
  "sections": [
    {
      "heading": "What is Phishing?",
      "content": "Phishing is a social engineering attack..."
    }
  ]
}
```

**`quiz_json` in `micro_lessons`:**
```json
{
  "questions": [
    {
      "question": "What is a red flag in phishing emails?",
      "options": ["Professional tone", "Urgent deadlines", "Logo", "Grammar"],
      "correct_answer": "Urgent deadlines"
    }
  ]
}
```

**`meta_data` in `notifications`:**
Stores flexible notification metadata without schema changes.

**`session_data` in `scenario_progress`:**
Preserves user session state for resume functionality.

### 3.2 Indexing Strategy

**Primary Indexes:**
- All tables have AUTO_INCREMENT primary keys
- Composite indexes on frequently joined columns

**Secondary Indexes:**
```sql
-- Performance optimization examples
INDEX idx_username (username)                    -- User lookups
INDEX idx_total_score (total_score DESC)         -- Leaderboard queries
INDEX idx_timestamp (timestamp DESC)             -- Chronological queries
INDEX idx_user_status (user_id, status)         -- Filtered progress queries
INDEX idx_level_order (level_id, order_index)   -- Sequential content delivery
```

### 3.3 Referential Integrity

**Cascade Deletion:**
```sql
FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
```
When a user is deleted, all related records (responses, progress, achievements) are automatically removed.

**Set NULL on Deletion:**
```sql
FOREIGN KEY (assigned_by) REFERENCES users(user_id) ON DELETE SET NULL
```
Preserves audit trail even if the assigning user is deleted.

### 3.4 Data Type Optimization

| Data Type | Usage | Justification |
|-----------|-------|---------------|
| `INT` | IDs, scores | 4-byte integer for reasonable range |
| `BIGINT` | `audit_logs.audit_id` | Anticipates high-volume logging |
| `VARCHAR(n)` | Constrained text | Enforces length limits |
| `TEXT` | Descriptions, content | Unlimited length for rich content |
| `FLOAT` | Success rates | Decimal precision for percentages |
| `DECIMAL(3,2)` | Confidence levels | Fixed precision (0.00-9.99) |
| `BOOLEAN` | Flags | True/False values |
| `ENUM` | Status fields | Predefined set of values |
| `JSON` | Dynamic content | Schema-less flexible storage |
| `DATETIME` | Timestamps | Date and time precision |

---

## 4. Normalization Analysis

### 4.1 Third Normal Form (3NF) Compliance

**1NF (First Normal Form):**
- ✅ All columns contain atomic values
- ✅ No repeating groups
- ✅ Each row is unique (primary key)

**2NF (Second Normal Form):**
- ✅ No partial dependencies
- ✅ All non-key attributes depend on entire primary key

**3NF (Third Normal Form):**
- ✅ No transitive dependencies
- ✅ Non-key attributes depend only on primary key

**Example: User-Role-Permission Structure**

Instead of:
```sql
-- BAD: Denormalized (causes update anomalies)
users (user_id, username, role_name, permissions_list)
```

We use:
```sql
-- GOOD: Normalized (3NF)
users (user_id, username)
roles (role_id, role_name)
permissions (permission_id, permission_name)
user_roles (user_role_id, user_id, role_id)      -- Junction table
role_permissions (role_permission_id, role_id, permission_id)  -- Junction table
```

Benefits:
- Eliminates data redundancy
- Prevents update anomalies
- Flexible permission management
- Easy role modification

### 4.2 Denormalization Decisions

Strategic denormalization for performance:

**`users.total_score`:**
- Denormalized aggregate of all earned points
- Alternative: `SUM(achievements.points) + SUM(modules.score)`
- Justification: Frequently accessed, updated via triggers/application logic

**`user_progress.score`:**
- Stores best score per module
- Avoids expensive `MAX()` aggregation on every query

**Rationale:** Read-heavy queries benefit from precalculated values at the cost of slight write complexity.

---

## 5. Advanced SQL Queries Implementation

### 5.1 Complex Joins

**User Dashboard Statistics:**
```sql
SELECT 
    u.user_id,
    u.username,
    u.total_score,
    COUNT(DISTINCT ur.response_id) as total_attempts,
    SUM(CASE WHEN ur.is_correct THEN 1 ELSE 0 END) as correct_answers,
    ROUND((SUM(CASE WHEN ur.is_correct THEN 1 ELSE 0 END) / 
           COUNT(ur.response_id)) * 100, 2) as accuracy_percentage,
    GROUP_CONCAT(DISTINCT a.achievement_name) as achievements
FROM users u
LEFT JOIN user_responses ur ON u.user_id = ur.user_id
LEFT JOIN achievements a ON u.user_id = a.user_id
WHERE u.user_id = ?
GROUP BY u.user_id;
```

### 5.2 Subqueries

**Leaderboard Ranking:**
```sql
SELECT 
    user_id,
    username,
    total_score,
    (SELECT COUNT(*) + 1 
     FROM users u2 
     WHERE u2.total_score > u1.total_score) as rank
FROM users u1
ORDER BY total_score DESC
LIMIT 10;
```

### 5.3 Window Functions

**Learning Progress Trend:**
```sql
SELECT 
    user_id,
    module_id,
    score,
    attempt_date,
    ROW_NUMBER() OVER (PARTITION BY user_id, module_id 
                       ORDER BY attempt_date DESC) as attempt_rank,
    AVG(score) OVER (PARTITION BY user_id 
                     ORDER BY attempt_date 
                     ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) as moving_avg_score
FROM module_attempts
ORDER BY user_id, attempt_date DESC;
```

### 5.4 Recursive CTEs

**Learning Path Progression:**
```sql
WITH RECURSIVE module_sequence AS (
    -- Base case: First module
    SELECT 
        module_id, 
        level_id, 
        order_index,
        title,
        1 as depth
    FROM learning_modules
    WHERE level_id = (SELECT level_id FROM path_levels 
                      WHERE level_number = 1 LIMIT 1)
      AND order_index = 1
    
    UNION ALL
    
    -- Recursive case: Next modules
    SELECT 
        lm.module_id,
        lm.level_id,
        lm.order_index,
        lm.title,
        ms.depth + 1
    FROM learning_modules lm
    INNER JOIN module_sequence ms 
        ON lm.level_id = ms.level_id AND lm.order_index = ms.order_index + 1
        OR (lm.level_id > ms.level_id AND lm.order_index = 1)
    WHERE ms.depth < 100  -- Safety limit
)
SELECT * FROM module_sequence;
```

### 5.5 Aggregate Functions with HAVING

**Vulnerable Users Identification:**
```sql
SELECT 
    u.user_id,
    u.username,
    s.scenario_type,
    COUNT(ur.response_id) as attempts,
    SUM(CASE WHEN ur.is_correct = 0 THEN 1 ELSE 0 END) as failures,
    ROUND((SUM(CASE WHEN ur.is_correct = 0 THEN 1 ELSE 0 END) / 
           COUNT(ur.response_id)) * 100, 2) as failure_rate
FROM users u
INNER JOIN user_responses ur ON u.user_id = ur.user_id
INNER JOIN scenarios s ON ur.scenario_id = s.scenario_id
GROUP BY u.user_id, s.scenario_type
HAVING failure_rate > 50  -- More than 50% failure rate
ORDER BY failure_rate DESC;
```

### 5.6 Conditional Aggregation

**Category Performance Matrix:**
```sql
SELECT 
    u.username,
    SUM(CASE WHEN c.category_name = 'Phishing' THEN 1 ELSE 0 END) as phishing_attempts,
    SUM(CASE WHEN c.category_name = 'Phishing' AND up.status = 'completed' 
        THEN 1 ELSE 0 END) as phishing_completed,
    SUM(CASE WHEN c.category_name = 'Vishing' THEN 1 ELSE 0 END) as vishing_attempts,
    SUM(CASE WHEN c.category_name = 'Vishing' AND up.status = 'completed' 
        THEN 1 ELSE 0 END) as vishing_completed
FROM users u
LEFT JOIN user_progress up ON u.user_id = up.user_id
LEFT JOIN learning_modules lm ON up.module_id = lm.module_id
LEFT JOIN categories c ON lm.category_id = c.category_id
GROUP BY u.user_id;
```

---

## 6. Role-Based Access Control (RBAC)

### 6.1 Permission Model

**Three-Tier Architecture:**
1. **Users** → Many-to-Many → **Roles**
2. **Roles** → Many-to-Many → **Permissions**
3. **Permissions** → Resource + Action pairs

**Permission Check Query:**
```sql
SELECT p.*
FROM permissions p
INNER JOIN role_permissions rp ON p.permission_id = rp.permission_id
INNER JOIN roles r ON rp.role_id = r.role_id
INNER JOIN user_roles ur ON r.role_id = ur.role_id
WHERE ur.user_id = ? 
  AND p.resource = 'scenarios' 
  AND p.action = 'write';
```

### 6.2 Dynamic Role Assignment

**Time-Based Role Expiration:**
```sql
SELECT ur.*, r.role_name
FROM user_roles ur
INNER JOIN roles r ON ur.role_id = r.role_id
WHERE ur.user_id = ?
  AND (ur.expires_date IS NULL OR ur.expires_date > NOW());
```

---

## 7. Audit and Compliance

### 7.1 Comprehensive Audit Trail

The `audit_logs` table captures:
- User actions (login, logout, data modifications)
- IP addresses and user agents
- Old and new values (JSON format)
- Severity levels
- Request metadata

**Audit Query Example:**
```sql
SELECT 
    al.*,
    u.username,
    DATE_FORMAT(al.timestamp, '%Y-%m-%d %H:%i:%s') as formatted_time
FROM audit_logs al
LEFT JOIN users u ON al.user_id = u.user_id
WHERE al.severity IN ('high', 'critical')
  AND al.timestamp >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY al.timestamp DESC;
```

### 7.2 Data Retention Policy

**Notification Cleanup:**
```sql
DELETE FROM notifications
WHERE status = 'archived'
  AND expires_at < DATE_SUB(NOW(), INTERVAL 90 DAY);
```

---

## 8. Performance Optimization

### 8.1 Query Optimization Techniques

**1. Index Usage:**
```sql
EXPLAIN SELECT * FROM user_responses 
WHERE user_id = 5 
ORDER BY timestamp DESC;
-- Uses idx_user_id and idx_timestamp
```

**2. Query Caching:**
Application-level caching for frequently accessed data:
- User profiles
- Scenario lists
- Category metadata

**3. Connection Pooling:**
SQLAlchemy pool configuration:
```python
pool_size=10, max_overflow=20, pool_timeout=30
```

### 8.2 Database Scalability

**Horizontal Partitioning (Future Enhancement):**
```sql
-- Partition audit_logs by month
ALTER TABLE audit_logs
PARTITION BY RANGE (YEAR(timestamp)*100 + MONTH(timestamp)) (
    PARTITION p_2024_01 VALUES LESS THAN (202402),
    PARTITION p_2024_02 VALUES LESS THAN (202403),
    ...
);
```

---

## 9. Data Security Measures

### 9.1 Sensitive Data Protection

**Password Hashing:**
- Werkzeug `generate_password_hash()` with salt
- Never stored in plaintext

**SQL Injection Prevention:**
- Parameterized queries via SQLAlchemy ORM
- Input validation and sanitization

### 9.2 Database User Permissions

**Principle of Least Privilege:**
```sql
-- Application user (limited permissions)
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'password';
GRANT SELECT, INSERT, UPDATE, DELETE 
ON social_engineering_db.* 
TO 'app_user'@'localhost';

-- Read-only analytics user
CREATE USER 'analytics_user'@'localhost' IDENTIFIED BY 'password';
GRANT SELECT ON social_engineering_db.* 
TO 'analytics_user'@'localhost';
```

---

## 10. Backup and Recovery Strategy

### 10.1 Backup Procedures

**Daily Full Backup:**
```bash
mysqldump -u root -p social_engineering_db \
  --single-transaction \
  --routines \
  --triggers \
  > backup_$(date +%Y%m%d).sql
```

**Point-in-Time Recovery:**
Enable binary logging:
```sql
SET GLOBAL binlog_format = 'ROW';
```

### 10.2 Disaster Recovery

**Recovery Process:**
1. Restore from most recent full backup
2. Apply binary logs from backup time to incident time
3. Verify data integrity
4. Resume operations

---

## 11. Transaction Management

### 11.1 ACID Properties

**Atomicity Example:**
```python
try:
    # Start transaction
    user.total_score += points
    achievement = Achievement(user_id=user.user_id, ...)
    db.session.add(achievement)
    db.session.commit()  # All or nothing
except Exception:
    db.session.rollback()  # Undo all changes
```

**Isolation Levels:**
- Default: `REPEATABLE READ`
- Prevents dirty reads and non-repeatable reads

---

## 12. Future Enhancements

### 12.1 Planned Improvements

1. **Materialized Views:** For complex analytics queries
2. **Full-Text Search:** For scenario content searching
3. **Time-Series Optimization:** Partitioning for historical data
4. **Sharding:** User-based horizontal scaling
5. **NoSQL Integration:** Redis for session management

---

## 13. Conclusion

The Social Engineering Training Simulator employs a robust, well-architected MySQL database that balances:
- **Data Integrity** through rigorous referential constraints
- **Performance** via strategic indexing and query optimization
- **Security** through RBAC and comprehensive audit logging
- **Flexibility** with JSON columns for dynamic content
- **Scalability** with normalization and future partitioning strategies

The database design adheres to industry best practices and provides a solid foundation for an enterprise-grade security training platform.

---

## Appendix: Table Row Count Estimates

| Table | Estimated Rows (1000 users, 1 year) |
|-------|-------------------------------------|
| `users` | 1,000 |
| `scenarios` | 50 |
| `user_responses` | 500,000 |
| `learning_modules` | 120 |
| `user_progress` | 120,000 |
| `audit_logs` | 2,000,000+ |
| `notifications` | 10,000 |
| `achievements` | 5,000 |

**Total Database Size Projection:** ~500 MB - 1 GB annually
