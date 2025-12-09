from db_connect import get_connection

conn = get_connection()
cursor = conn.cursor()

cursor.execute("SHOW TABLES")
print(cursor.fetchall())

cursor.close()
conn.close()
