import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

try:
    conn = pymysql.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DB', 'social_engineering_db'),
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )

    with conn.cursor() as cursor:
        # Update the icon for Digital Payments to an emoji
        sql = "UPDATE topics SET icon = %s WHERE topic_name LIKE %s"
        cursor.execute(sql, ('📱', '%Digital Payments%'))
        row_count = cursor.rowcount
    
    conn.commit()
    print(f"✅ Successfully updated {row_count} topic(s) with new icon '📱'")

except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if 'conn' in locals() and conn.open:
        conn.close()
