-- Quick Launch Flow Migration

-- 1. Add details to Organizations
-- Using strict SQLite syntax (no multiple ADD COLUMN in one statement if older version, but assuming generic SQL support here or handling sequentially)
ALTER TABLE organizations ADD COLUMN sector VARCHAR(50);
ALTER TABLE organizations ADD COLUMN size_bucket VARCHAR(20);
ALTER TABLE organizations ADD COLUMN country VARCHAR(50);
ALTER TABLE organizations ADD COLUMN timezone VARCHAR(50);

-- 2. Create Campaigns Table
CREATE TABLE campaigns (
    campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
    org_id INTEGER NOT NULL,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL, -- e.g., 'Phishing', 'Baiting'
    status VARCHAR(20) DEFAULT 'Draft', -- 'Draft', 'Active', 'Completed'
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    launched_at DATETIME,
    FOREIGN KEY(org_id) REFERENCES organizations(org_id)
);

-- 3. Create Campaign Targets Table (Users targeted in a campaign)
CREATE TABLE campaign_targets (
    target_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    status VARCHAR(20) DEFAULT 'Pending', -- 'Pending', 'Sent', 'Opened', 'Clicked', 'Reported', 'Failed'
    sent_at DATETIME,
    interacted_at DATETIME,
    FOREIGN KEY(campaign_id) REFERENCES campaigns(campaign_id),
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);
