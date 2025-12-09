from flask import Flask, render_template, request, redirect, url_for
from db_connect import get_connection
from predict_weather import predict_temperature  # uses your existing prediction function

app = Flask(__name__)


# ---------- Helper functions ----------

def get_locations():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT location_id, city, state, country FROM Location ORDER BY location_id")
    locations = cur.fetchall()
    cur.close()
    conn.close()
    return locations


def get_weather_for_location(location_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT date, temperature, humidity, rainfall
        FROM Weather_Data
        WHERE location_id = %s
        ORDER BY date DESC
        LIMIT 7
    """, (location_id,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows


# ---------- Routes ----------

@app.route("/")
def home():
    locations = get_locations()
    selected_location_id = request.args.get("location_id", type=int)
    weather_rows = []
    predicted_temp = None
    error = None

    if selected_location_id:
        weather_rows = get_weather_for_location(selected_location_id)
        predicted_temp = predict_temperature(selected_location_id)
        if predicted_temp is None:
            error = "Not enough data to predict. Please add at least 3 days of weather data."

    return render_template(
        "predict.html",
        locations=locations,
        selected_location_id=selected_location_id,
        weather_rows=weather_rows,
        predicted_temp=predicted_temp,
        error=error
    )


@app.route("/add_location", methods=["POST"])
def add_location():
    city = request.form.get("city")
    state = request.form.get("state")
    country = request.form.get("country")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO Location (city, state, country) VALUES (%s, %s, %s)",
        (city, state, country)
    )
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("home"))


@app.route("/delete_location/<int:location_id>", methods=["POST"])
def delete_location(location_id):
    conn = get_connection()
    cur = conn.cursor()

    # delete children first (to avoid FK errors)
    cur.execute("DELETE FROM Weather_Data WHERE location_id = %s", (location_id,))
    cur.execute("DELETE FROM Prediction WHERE location_id = %s", (location_id,))
    cur.execute("DELETE FROM Location WHERE location_id = %s", (location_id,))

    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("home"))


@app.route("/edit_location/<int:location_id>", methods=["GET", "POST"])
def edit_location(location_id):
    if request.method == "POST":
        city = request.form.get("city")
        state = request.form.get("state")
        country = request.form.get("country")

        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE Location SET city = %s, state = %s, country = %s WHERE location_id = %s",
            (city, state, country, location_id)
        )
        conn.commit()
        cur.close()
        conn.close()
        return redirect(url_for("home"))

    # GET: show form with existing values
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT location_id, city, state, country FROM Location WHERE location_id = %s",
        (location_id,)
    )
    loc = cur.fetchone()
    cur.close()
    conn.close()

    if not loc:
        return "Location not found", 404

    return render_template("edit_location.html", location=loc)


@app.route("/add_weather", methods=["POST"])
def add_weather():
    location_id = request.form.get("location_id", type=int)
    date = request.form.get("date")
    temperature = request.form.get("temperature", type=float)
    humidity = request.form.get("humidity", type=float)
    rainfall = request.form.get("rainfall", type=float)
    wind_speed = request.form.get("wind_speed", type=float)

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO Weather_Data
        (location_id, date, temperature, humidity, rainfall, wind_speed)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (location_id, date, temperature, humidity, rainfall, wind_speed))
    conn.commit()
    cur.close()
    conn.close()

    # return to home with that location selected
    return redirect(url_for("home", location_id=location_id))


if __name__ == "__main__":
    app.run(debug=True)
