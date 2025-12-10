"""
Migration: Add Subscription Fields to User Table
"""
import sys
import os
from sqlalchemy import text

# Add parent directory to path to import app
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + '/..')

from app import create_app, db

app = create_app()
app.app_context().push()

print("=" * 80)
print("DATABASE MIGRATION: Adding Subscription Fields")
print("=" * 80)

def column_exists(table, column):
    result = db.session.execute(text(f"SHOW COLUMNS FROM {table} LIKE '{column}'"))
    return result.fetchone() is not None

try:
    # 1. subscription_tier
    if not column_exists('users', 'subscription_tier'):
        print("Adding 'subscription_tier' column...")
        db.session.execute(text("ALTER TABLE users ADD COLUMN subscription_tier VARCHAR(20) DEFAULT 'free'"))
    else:
        print("'subscription_tier' already exists.")

    # 2. weekly_scenario_count
    if not column_exists('users', 'weekly_scenario_count'):
        print("Adding 'weekly_scenario_count' column...")
        db.session.execute(text("ALTER TABLE users ADD COLUMN weekly_scenario_count INTEGER DEFAULT 0"))
    else:
        print("'weekly_scenario_count' already exists.")

    # 3. last_week_reset
    if not column_exists('users', 'last_week_reset'):
        print("Adding 'last_week_reset' column...")
        db.session.execute(text("ALTER TABLE users ADD COLUMN last_week_reset DATETIME"))
    else:
        print("'last_week_reset' already exists.")

    db.session.commit()
    print("\n✓ Migration successful!")

except Exception as e:
    print(f"\n❌ Error: {e}")
    db.session.rollback()
