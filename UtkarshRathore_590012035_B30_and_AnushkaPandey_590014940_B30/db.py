import os
from mysql.connector import pooling
from dotenv import load_dotenv
load_dotenv()

config = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASS", ""),
    "database": os.getenv("DB_NAME", "pet_adoption"),
    "charset": "utf8mb4"
}

pool = pooling.MySQLConnectionPool(pool_name="pet_pool_v3", pool_size=5, **config)

def get_conn():
    return pool.get_connection()

def query(sql, params=None, fetchone=False, fetchall=False, commit=False):
    conn = get_conn()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(sql, params or ())
        data = None
        if fetchone:
            data = cur.fetchone()
        elif fetchall:
            data = cur.fetchall()
        if commit:
            conn.commit()
        cur.close()
        return data
    finally:
        conn.close()
