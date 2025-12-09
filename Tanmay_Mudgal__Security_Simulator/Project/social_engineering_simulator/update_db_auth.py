
import mysql.connector
from mysql.connector import Error

def update_db():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='password',
            database='social_engineering_db'
        )

        if connection.is_connected():
            cursor = connection.cursor()
            
            # Add organization column
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN organization VARCHAR(100);")
                print("Added organization column")
            except Error as e:
                print(f"Error adding organization: {e}")

            # Add account_type column
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN account_type VARCHAR(20) DEFAULT 'Individual';")
                print("Added account_type column")
            except Error as e:
                print(f"Error adding account_type: {e}")

            connection.commit()
            print("Database updated successfully")

    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    update_db()
