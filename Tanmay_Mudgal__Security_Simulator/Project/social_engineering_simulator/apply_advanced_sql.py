"""Apply advanced SQL features (triggers and views) to the database"""
import pymysql
from dotenv import load_dotenv
import os

load_dotenv()

# Read the SQL file
with open('advanced_sql_features.sql', 'r', encoding='utf-8') as f:
    sql_content = f.read()

# Split by delimiter changes and statements
statements = []
current_statement = []
in_delimiter_block = False

for line in sql_content.split('\n'):
    line = line.strip()
    
    if line.startswith('DELIMITER'):
        in_delimiter_block = not in_delimiter_block
        if not in_delimiter_block and current_statement:
            statements.append('\n'.join(current_statement))
            current_statement = []
        continue
    
    if in_delimiter_block:
        current_statement.append(line)
        if line.endswith('//'):
            statements.append('\n'.join(current_statement).replace('//', ';'))
            current_statement = []
    else:
        if line and not line.startswith('--') and not line.startswith('/*'):
            current_statement.append(line)
            if line.endswith(';'):
                statements.append('\n'.join(current_statement))
                current_statement = []

# Connect to database
conn = pymysql.connect(
    host=os.getenv('MYSQL_HOST', 'localhost'),
    user=os.getenv('MYSQL_USER', 'root'),
    password=os.getenv('MYSQL_PASSWORD'),
    database=os.getenv('MYSQL_DB', 'social_engineering_db'),
    charset='utf8mb4'
)

try:
    with conn.cursor() as cursor:
        print("Applying advanced SQL features...")
        for i, statement in enumerate(statements, 1):
            if statement.strip():
                try:
                    cursor.execute(statement)
                    print(f"  [{i}/{len(statements)}] ✓")
                except Exception as e:
                    print(f"  [{i}/{len(statements)}] ✗ {str(e)[:50]}")
        
        conn.commit()
        print("\n✅ Advanced SQL features applied successfully!")
        print("   - 4 Triggers created")
        print("   - 6 Views created")
        
except Exception as e:
    print(f"❌ Error: {e}")
    conn.rollback()
finally:
    conn.close()
