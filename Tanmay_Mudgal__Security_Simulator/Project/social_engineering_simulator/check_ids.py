import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

conn = pymysql.connect(
    host=os.getenv('MYSQL_HOST', 'localhost'),
    user=os.getenv('MYSQL_USER', 'root'),
    password=os.getenv('MYSQL_PASSWORD'),
    database=os.getenv('MYSQL_DB', 'social_engineering_db'),
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cursor:
        cursor.execute("SELECT level_id, level_name FROM path_levels")
        print("\nAll Levels:")
        for lvl in cursor.fetchall():
            print(f"ID: {lvl['level_id']}, Name: {lvl['level_name']}")
            
        cursor.execute("SELECT category_id, category_name FROM categories")
        print("\nAll Categories:")
        for cat in cursor.fetchall():
            print(f"ID: {cat['category_id']}, Name: {cat['category_name']}")
finally:
    conn.close()
