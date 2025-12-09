"""
Migration script to add activity tracking columns to user_progress table
Run this file: python migrations/migrate_add_tracking.py
"""

from app import app, db
from sqlalchemy import text

def migrate():
    with app.app_context():
        try:
            # Check if columns already exist
            result = db.session.execute(text("DESCRIBE user_progress"))
            columns = [row[0] for row in result]
            
            if 'first_viewed_at' in columns:
                print("✅ Columns already exist. Migration not needed.")
                return
            
            print("Adding tracking columns to user_progress table...")
            
            # Add the new columns
            db.session.execute(text("""
                ALTER TABLE user_progress 
                ADD COLUMN first_viewed_at DATETIME NULL AFTER completed_at,
                ADD COLUMN last_activity_at DATETIME NULL AFTER first_viewed_at,
                ADD COLUMN view_count INT DEFAULT 0 AFTER last_activity_at
            """))
            
            db.session.commit()
            print("✅ Migration completed successfully!")
            print("   - Added: first_viewed_at")
            print("   - Added: last_activity_at")
            print("   - Added: view_count")
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Migration failed: {e}")
            raise

if __name__ == '__main__':
    migrate()
