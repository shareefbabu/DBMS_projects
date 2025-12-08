import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

def clean_data():
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME', 'FlightBookingDB')
        )
        cursor = conn.cursor()

        print("Executing cleanup...")
        
        # Delete the specific user causing issues
        query = "DELETE FROM users WHERE email = 'giandeep.sgrl@gmail.com'"
        cursor.execute(query)
        deleted_count = cursor.rowcount
        
        conn.commit()
        print(f"Deleted {deleted_count} test users.")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Cleanup failed: {e}")

if __name__ == "__main__":
    clean_data()
