-- Create database
CREATE DATABASE IF NOT EXISTS campus_lost_found CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE campus_lost_found;

-- ADMIN table
CREATE TABLE IF NOT EXISTS admin (
  admin_id INT AUTO_INCREMENT PRIMARY KEY,
  admin_name VARCHAR(150) NOT NULL,
  username VARCHAR(100) NOT NULL UNIQUE,
  password VARCHAR(255) NOT NULL,
  role VARCHAR(50) DEFAULT 'admin',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ITEMS table
CREATE TABLE IF NOT EXISTS items (
  item_id INT AUTO_INCREMENT PRIMARY KEY,
  item_name VARCHAR(200) NOT NULL,
  description TEXT,
  category VARCHAR(100),
  location_lost VARCHAR(255),
  date_lost DATE,
  image_path VARCHAR(500),
  status ENUM('lost','claimed','removed') DEFAULT 'lost',
  added_by_admin INT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (added_by_admin) REFERENCES admin(admin_id) ON DELETE SET NULL
);

-- CLAIMS table
CREATE TABLE IF NOT EXISTS claims (
  claim_id INT AUTO_INCREMENT PRIMARY KEY,
  item_id INT NOT NULL,
  claimer_name VARCHAR(200) NOT NULL,
  sap_id VARCHAR(50) NOT NULL,
  course VARCHAR(150),
  message TEXT,
  proof_path VARCHAR(500),
  date_claimed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  status ENUM('pending','approved','rejected') DEFAULT 'pending',
  FOREIGN KEY (item_id) REFERENCES items(item_id) ON DELETE CASCADE
);

-- AUDIT_LOG table
CREATE TABLE IF NOT EXISTS audit_log (
  log_id INT AUTO_INCREMENT PRIMARY KEY,
  action_type VARCHAR(100) NOT NULL,
  action_description TEXT,
  admin_id INT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (admin_id) REFERENCES admin(admin_id) ON DELETE SET NULL
);

-- Indexes for performance (suggested)
CREATE INDEX idx_items_category ON items(category);
CREATE INDEX idx_items_status ON items(status);
CREATE INDEX idx_claims_item ON claims(item_id);
CREATE INDEX idx_claims_status ON claims(status);
CREATE INDEX idx_audit_time ON audit_log(created_at);

-- Sample admin (temporary plain password: change later or replace with hashed password)
INSERT INTO admin (admin_name, username, password, role)
VALUES ('Campus Admin','admin','admin123','admin');

-- Sample items for testing
INSERT INTO items (item_name, description, category, location_lost, date_lost, image_path, added_by_admin)
VALUES
('Black Leather Wallet','Leather wallet with 2 cards; no cash','accessories','Library - 2nd floor','2025-11-10','assets/images/sample_wallet.jpg', 1),
('Samsung S24 Phone','Blue cover, cracked screen on bottom-right','electronics','Cafeteria table','2025-11-18','assets/images/sample_phone.jpg', 1),
('College ID Card','ID: 40001623, Name: Prashant Rawat','documents','Bus stop near gate','2025-11-20','assets/images/sample_id.jpg', 1);