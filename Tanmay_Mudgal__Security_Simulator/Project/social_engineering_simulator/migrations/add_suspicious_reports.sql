USE social_engineering_db;

CREATE TABLE IF NOT EXISTS suspicious_reports (
    report_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    org_id INT,
    content_text TEXT,
    screenshot_path VARCHAR(255),
    category VARCHAR(50) NOT NULL,
    status ENUM('Pending', 'Approved', 'Rejected', 'Converted') DEFAULT 'Pending',
    admin_notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (org_id) REFERENCES organizations(org_id) ON DELETE SET NULL,
    INDEX idx_status (status),
    INDEX idx_org (org_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
