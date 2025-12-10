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
        cursor.execute("SELECT topic_id, topic_name FROM topics WHERE topic_name LIKE '%Digital Payments%'")
        print("\nDigital Payment Topic:")
        print(cursor.fetchone())
finally:
    conn.close()
