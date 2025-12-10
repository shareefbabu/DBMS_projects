from app import create_app, db
from sqlalchemy import text

app = create_app()

def migrate():
    with app.app_context():
        print("Starting migration...")
        try:
            # Using raw connection for DDL
            with db.engine.connect() as conn:
                # Add steps_json to scenarios
                try:
                    print("Adding steps_json to scenarios...")
                    conn.execute(text("ALTER TABLE scenarios ADD COLUMN steps_json TEXT"))
                    print("Success.")
                except Exception as e:
                    print(f"scenarios error (maybe exists): {e}")

                # Add response_json to user_responses
                try:
                    print("Adding response_json to user_responses...")
                    conn.execute(text("ALTER TABLE user_responses ADD COLUMN response_json TEXT"))
                    print("Success.")
                except Exception as e:
                    print(f"user_responses error (maybe exists): {e}")
                
                conn.commit()
            print("Migration process completed.")
        except Exception as e:
            print(f"Migration critical failure: {e}")

if __name__ == "__main__":
    migrate()
