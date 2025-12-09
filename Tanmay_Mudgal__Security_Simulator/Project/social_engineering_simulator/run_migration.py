from app import create_app, db
from sqlalchemy import text

app = create_app()

def migrate():
    with app.app_context():
        try:
            with open('migrations/add_incident_response.sql', 'r') as f:
                sql_commands = f.read().split(';')
            
            for command in sql_commands:
                if command.strip():
                    db.session.execute(text(command))
            
            db.session.commit()
            print("Migration successful!")
        except Exception as e:
            db.session.rollback()
            print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
