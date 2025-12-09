from db_connect import get_connection

def predict_temperature(location_id):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    SELECT AVG(temperature)
    FROM (
        SELECT temperature
        FROM Weather_Data
        WHERE location_id = %s
        ORDER BY date DESC
        LIMIT 3
    ) AS last3;
    """

    cursor.execute(sql, (location_id,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result[0] is None:
        print("Not enough data to predict.")
        return None

    predicted_temp = round(float(result[0]), 2)
    print("Predicted Temperature:", predicted_temp, "°C")
    return predicted_temp


# Only runs when you execute THIS file directly, not when imported
if __name__ == "__main__":
    predict_temperature(1)
