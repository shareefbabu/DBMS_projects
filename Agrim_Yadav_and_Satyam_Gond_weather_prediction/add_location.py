from db_connect import get_connection

def add_location(city, state, country):
    conn = get_connection()
    cursor = conn.cursor()

    sql = "INSERT INTO Location (city, state, country) VALUES (%s, %s, %s)"
    values = (city, state, country)

    cursor.execute(sql, values)
    conn.commit()

    print("Location added successfully!")
    cursor.close()
    conn.close()


# Example run:
add_location("Dehradun", "Uttarakhand", "India")
