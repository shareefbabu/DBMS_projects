import sys
import os
from sqlalchemy import text

# Add root directory to path to allow importing app
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))

from app import create_app, db

app = create_app()

def run_fix():
    with app.app_context():
        print("Starting MySQL Fix Migration...")
        
        with db.engine.connect() as conn:
            # 1. Add Columns to Organizations
            # We'll try to add them one by one. If it fails (Duplicate column), we ignore.
            columns = [
                ('sector', 'VARCHAR(50)'),
                ('size_bucket', 'VARCHAR(20)'),
                ('country', 'VARCHAR(50)'),
                ('timezone', 'VARCHAR(50)')
            ]
            
            for col, dtype in columns:
                try:
                    print(f"Attempting to add {col}...")
                    conn.execute(text(f"ALTER TABLE organizations ADD COLUMN {col} {dtype}"))
                    print(f"-> Added {col}")
                except Exception as e:
                    # Check for typical MySQL "Duplicate column" error codes (1060) or message
                    # Also handle generic sqlalchemy wrapper exceptions
                    err_str = str(e).lower()
                    if "duplicate column" in err_str:
                        print(f"-> Column {col} already exists (skipping).")
                    else:
                        print(f"-> Error adding {col}: {e}")

            # 2. Create Campaigns Table
            # MySQL 'IF NOT EXISTS' is standard
            print("Creating campaigns table...")
            try:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS campaigns (
                        campaign_id INT AUTO_INCREMENT PRIMARY KEY,
                        org_id INT NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        type VARCHAR(50) NOT NULL,
                        status VARCHAR(20) DEFAULT 'Draft',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        launched_at DATETIME,
                        FOREIGN KEY(org_id) REFERENCES organizations(org_id)
                    ) ENGINE=InnoDB;
                """))
            except Exception as e:
                print(f"Error creating campaigns: {e}")

            # 3. Create Campaign Targets Table
            print("Creating campaign_targets table...")
            try:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS campaign_targets (
                        target_id INT AUTO_INCREMENT PRIMARY KEY,
                        campaign_id INT NOT NULL,
                        user_id INT NOT NULL,
                        status VARCHAR(20) DEFAULT 'Pending',
                        sent_at DATETIME,
                        interacted_at DATETIME,
                        FOREIGN KEY(campaign_id) REFERENCES campaigns(campaign_id),
                        FOREIGN KEY(user_id) REFERENCES users(user_id)
                    ) ENGINE=InnoDB;
                """))
            except Exception as e:
                print(f"Error creating campaign_targets: {e}")

            conn.commit()
            print("Migration fix completed. Please check if error persists.")

if __name__ == '__main__':
    run_fix()
