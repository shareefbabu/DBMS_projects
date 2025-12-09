import sqlite3
from sqlalchemy import text
import sys
import os

# Add root directory to path to allow importing app
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/..'))

from app import create_app, db

app = create_app()

def run_migration():
    with app.app_context():
        print("Starting Quick Launch Migration...")
        
        # 1. Add columns to Organizations
        columns_to_add = [
            ('sector', 'VARCHAR(50)'),
            ('size_bucket', 'VARCHAR(20)'),
            ('country', 'VARCHAR(50)'),
            ('timezone', 'VARCHAR(50)')
        ]
        
        # Check existing columns
        with db.engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(organizations)"))
            existing_cols = [row[1] for row in result.fetchall()]
            
            for col_name, col_type in columns_to_add:
                if col_name not in existing_cols:
                    try:
                        print(f"Adding column {col_name} to organizations...")
                        conn.execute(text(f"ALTER TABLE organizations ADD COLUMN {col_name} {col_type}"))
                        conn.commit()
                    except Exception as e:
                        print(f"Error adding {col_name}: {e}")
                else:
                    print(f"Column {col_name} already exists.")

            # 2. Create Campaigns Table
            print("Creating campaigns table...")
            try:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS campaigns (
                        campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        org_id INTEGER NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        type VARCHAR(50) NOT NULL,
                        status VARCHAR(20) DEFAULT 'Draft',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                        launched_at DATETIME,
                        FOREIGN KEY(org_id) REFERENCES organizations(org_id)
                    )
                """))
                conn.commit()
            except Exception as e:
                print(f"Error creating campaigns table: {e}")

            # 3. Create Campaign Targets Table
            print("Creating campaign_targets table...")
            try:
                conn.execute(text("""
                    CREATE TABLE IF NOT EXISTS campaign_targets (
                        target_id INTEGER PRIMARY KEY AUTOINCREMENT,
                        campaign_id INTEGER NOT NULL,
                        user_id INTEGER NOT NULL,
                        status VARCHAR(20) DEFAULT 'Pending',
                        sent_at DATETIME,
                        interacted_at DATETIME,
                        FOREIGN KEY(campaign_id) REFERENCES campaigns(campaign_id),
                        FOREIGN KEY(user_id) REFERENCES users(user_id)
                    )
                """))
                conn.commit()
            except Exception as e:
                print(f"Error creating campaign_targets table: {e}")

        print("Migration completed.")

if __name__ == '__main__':
    run_migration()
