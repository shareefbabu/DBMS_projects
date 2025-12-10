import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def update_schema():
    db_config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'database': os.getenv('MYSQL_DB', 'social_engineering_db'),
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }

    try:
        conn = pymysql.connect(**db_config)
        with conn.cursor() as cursor:
            # Create achievement_definitions table
            print("Creating achievement_definitions table...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS achievement_definitions (
                    definition_id INT AUTO_INCREMENT PRIMARY KEY,
                    slug VARCHAR(50) UNIQUE NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    category VARCHAR(50),
                    tier VARCHAR(20),
                    icon VARCHAR(50),
                    condition_description VARCHAR(200),
                    target_value INT DEFAULT 1,
                    is_org_only BOOLEAN DEFAULT FALSE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
            """)

            # Alter achievements table
            print("Altering achievements table...")
            # Check if columns exist to avoid errors
            cursor.execute("DESCRIBE achievements")
            columns = [row['Field'] for row in cursor.fetchall()]

            if 'definition_id' not in columns:
                print("Adding definition_id column...")
                cursor.execute("ALTER TABLE achievements ADD COLUMN definition_id INT")
                cursor.execute("ALTER TABLE achievements ADD FOREIGN KEY (definition_id) REFERENCES achievement_definitions(definition_id)")
            
            if 'status' not in columns:
                print("Adding status column...")
                cursor.execute("ALTER TABLE achievements ADD COLUMN status VARCHAR(20) DEFAULT 'In Progress'")
            
            if 'current_value' not in columns:
                print("Adding current_value column...")
                cursor.execute("ALTER TABLE achievements ADD COLUMN current_value INT DEFAULT 0")

            if 'earned_date' in columns:
                print("Modifying earned_date column...")
                cursor.execute("ALTER TABLE achievements MODIFY COLUMN earned_date DATETIME NULL")

        conn.commit()
        print("Schema updated successfully.")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    update_schema()
