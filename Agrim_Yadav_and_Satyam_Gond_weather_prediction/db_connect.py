import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="agrim0605",
        database="weather_prediction"
    )
