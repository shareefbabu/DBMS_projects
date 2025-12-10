
from app import create_app, db
from sqlalchemy import text

def fix_schema():
    app = create_app()
    with app.app_context():
        print("Connected to database via Flask app context.")
        
        # SQL commands to add columns
        commands = [
            "ALTER TABLE users ADD COLUMN organization VARCHAR(100)",
            "ALTER TABLE users ADD COLUMN account_type VARCHAR(20) DEFAULT 'Individual'"
        ]
        
        with db.engine.connect() as conn:
            for cmd in commands:
                try:
                    conn.execute(text(cmd))
                    print(f"Executed: {cmd}")
                except Exception as e:
                    print(f"Error executing '{cmd}': {e}")
                    # Likely column already exists or other error, but we continue
                    
            conn.commit()
            print("Schema update completed.")

if __name__ == "__main__":
    fix_schema()
