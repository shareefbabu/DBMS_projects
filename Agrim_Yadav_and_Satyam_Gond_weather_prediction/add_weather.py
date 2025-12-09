from db_connect import get_connection

def add_weather(location_id, date, temperature, humidity, rainfall, wind_speed):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO Weather_Data (location_id, date, temperature, humidity, rainfall, wind_speed)
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (location_id, date, temperature, humidity, rainfall, wind_speed)

    cursor.execute(sql, values)
    conn.commit()

    print("Weather data added!")
    cursor.close()
    conn.close()


# Example run:
add_weather(1, "2025-11-23", 25.4, 60, 1.2, 5.3)
