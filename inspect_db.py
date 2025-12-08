import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def inspect_data():
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME', 'FlightBookingDB')
        )
        cursor = conn.cursor(dictionary=True)

        print("--- Users Table ---")
        cursor.execute("SELECT user_id, name, email, registration_date FROM users")
        users = cursor.fetchall()
        for user in users:
            print(user)
        
        print("\n--- Login Records Table ---")
        try:
            cursor.execute("SELECT record_id, user_id, login_timestamp, login_status FROM login_records LIMIT 10")
            records = cursor.fetchall()
            for record in records:
                print(record)
            
            cursor.execute("SELECT count(*) as count FROM login_records")
            count = cursor.fetchone()
            print(f"Total Login Records: {count['count']}")
        except mysql.connector.Error as e:
            print(f"Error reading login_records: {e}")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    inspect_data()
