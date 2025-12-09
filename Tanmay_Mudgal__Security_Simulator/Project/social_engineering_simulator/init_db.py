"""
Database Initialization Script
Runs the schema.sql file to create tables and populate initial data
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def init_database():
    """Initialize the database with schema and seed data"""
    
    # Database connection parameters
    db_config = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'user': os.getenv('MYSQL_USER', 'root'),
        'password': os.getenv('MYSQL_PASSWORD', ''),
        'charset': 'utf8mb4',
        'cursorclass': pymysql.cursors.DictCursor
    }
    
    db_name = os.getenv('MYSQL_DB', 'social_engineering_db')
    
    try:
        # Connect to MySQL without specifying database
        print(f"Connecting to MySQL server at {db_config['host']}...")
        connection = pymysql.connect(**db_config)
        
        with connection.cursor() as cursor:
            # Read and execute schema.sql
            print(f"Reading schema.sql...")
            with open('schema.sql', 'r', encoding='utf-8') as f:
                sql_script = f.read()
            
            # Split by semicolon and execute each statement
            statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
            
            print(f"Executing {len(statements)} SQL statements...")
            for i, statement in enumerate(statements, 1):
                if statement:
                    try:
                        cursor.execute(statement)
                        print(f"  [{i}/{len(statements)}] Executed successfully")
                    except Exception as e:
                        print(f"  [{i}/{len(statements)}] Warning: {e}")
                        # Continue with other statements even if one fails
            
            connection.commit()
        
        print(f"\n✅ Database '{db_name}' initialized successfully!")
        
        # Verify data was inserted
        connection.select_db(db_name)
        with connection.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM scenarios")
            result = cursor.fetchone()
            scenario_count = result['count']
            
            cursor.execute("SELECT scenario_type, COUNT(*) as count FROM scenarios GROUP BY scenario_type")
            type_counts = cursor.fetchall()
            
        print(f"\n📊 Database Statistics:")
        print(f"  Total Scenarios: {scenario_count}")
        for row in type_counts:
            print(f"  - {row['scenario_type']}: {row['count']} scenarios")
        
        connection.close()
        print("\n✅ Database initialization complete!")
        return True
        
    except pymysql.Error as e:
        print(f"\n❌ Database Error: {e}")
        return False
    except FileNotFoundError:
        print(f"\n❌ Error: schema.sql file not found")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected Error: {e}")
        return False

if __name__ == '__main__':
    print("="*60)
    print("Social Engineering Simulator - Database Initialization")
    print("="*60)
    print()
    
    success = init_database()
    
    if success:
        print("\n" + "="*60)
        print("You can now run the application with: python run.py")
        print("="*60)
    else:
        print("\n" + "="*60)
        print("Please check your database configuration and try again")
        print("="*60)
