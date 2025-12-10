import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# Database Config
DB_HOST = os.getenv('MYSQL_HOST', 'localhost')
DB_USER = os.getenv('MYSQL_USER', 'root')
DB_PASSWORD = os.getenv('MYSQL_PASSWORD', 'your_password')
DB_NAME = os.getenv('MYSQL_DB', 'social_engineering_db')

SQL_FILE = 'migrations/add_suspicious_reports.sql'

def apply_migration():
    print(f"Connecting to {DB_HOST}...")
    try:
        connection = pymysql.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            cursorclass=pymysql.cursors.DictCursor
        )
        
        with connection.cursor() as cursor:
            # Read SQL file
            with open(SQL_FILE, 'r') as f:
                sql_content = f.read()
            
            # Split and execute statements
            statements = sql_content.split(';')
            for statement in statements:
                if statement.strip():
                    print(f"Executing: {statement[:50]}...")
                    cursor.execute(statement)
            
        connection.commit()
        print("Migration applied successfully!")
        
    except Exception as e:
        print(f"Error applying migration: {e}")
    finally:
        if 'connection' in locals() and connection.open:
            connection.close()

if __name__ == "__main__":
    apply_migration()
