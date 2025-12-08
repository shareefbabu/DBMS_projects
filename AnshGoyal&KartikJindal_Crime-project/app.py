from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET", "dev_secret")


def get_db(dictionary=False):
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASS", ""),
        database=os.getenv("DB_NAME", "crime_analysis"),
        autocommit=False
    )


@app.route("/")
def index():
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    # Fetch all cases
    cur.execute("""
        SELECT 
            c.case_id, c.case_code, c.case_date, c.status,
            t.type_name,
            CONCAT(l.area, ', ', l.city, ', ', l.state) AS location,
            o.officer_name
        FROM crime_case c
        LEFT JOIN crime_type t ON c.type_id = t.type_id
        LEFT JOIN location l ON c.location_id = l.location_id
        LEFT JOIN officer o ON c.officer_id = o.officer_id
        ORDER BY c.case_id
    """)
    cases = cur.fetchall()

    # Crime types for dropdown
    cur.execute("SELECT type_id, type_name FROM crime_type")
    crime_types = cur.fetchall()

    conn.close()

    # Stats
    total_cases = len(cases)
    open_cases = sum(1 for c in cases if c["status"] == "Open")
    closed_cases = sum(1 for c in cases if c["status"] == "Closed")

    return render_template(
        "gui.html",
        cases=cases,
        crime_types=crime_types,
        total_cases=total_cases,
        open_cases=open_cases,
        closed_cases=closed_cases,
        detail=None
    )


# ADD CASE WITH MANUAL LOCATION + OFFICER
@app.route("/case/add", methods=["POST"])
def case_add():
    conn = get_db()
    cur = conn.cursor()

    case_code = request.form.get("case_code")
    case_date = request.form.get("case_date")
    type_id = request.form.get("type_id")
    description = request.form.get("description")
    status = request.form.get("status")

    # MANUAL LOCATION
    area = request.form.get("area")
    city = request.form.get("city")
    state = request.form.get("state")

    # Insert location
    cur.execute(
        "INSERT INTO location (area, city, state) VALUES (%s, %s, %s)",
        (area, city, state)
    )
    location_id = cur.lastrowid

    # MANUAL OFFICER NAME
    officer_name = request.form.get("officer_name")
    cur.execute(
        "INSERT INTO officer (officer_name) VALUES (%s)",
        (officer_name,)
    )
    officer_id = cur.lastrowid

    # Insert case
    cur.execute("""
        INSERT INTO crime_case 
        (case_code, case_date, type_id, location_id, officer_id, description, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (
        case_code, case_date, type_id,
        location_id, officer_id,
        description, status
    ))

    conn.commit()
    conn.close()
    return redirect(url_for("index"))


# Case Detail
@app.route("/case/<int:case_id>")
def case_detail(case_id):
    conn = get_db()
    cur = conn.cursor(dictionary=True)

    # Fetch the case detail
    cur.execute("""
        SELECT c.*, t.type_name,
               l.area, l.city, l.state,
               o.officer_name
        FROM crime_case c
        LEFT JOIN crime_type t ON c.type_id = t.type_id
        LEFT JOIN location l ON c.location_id = l.location_id
        LEFT JOIN officer o ON c.officer_id = o.officer_id
        WHERE c.case_id = %s
    """, (case_id,))
    detail = cur.fetchone()

    # Fetch case list again
    cur.execute("""
        SELECT 
            c.case_id, c.case_code, c.case_date, c.status,
            t.type_name,
            CONCAT(l.area, ', ', l.city, ', ', l.state) AS location,
            o.officer_name
        FROM crime_case c
        LEFT JOIN crime_type t ON c.type_id = t.type_id
        LEFT JOIN location l ON c.location_id = l.location_id
        LEFT JOIN officer o ON c.officer_id = o.officer_id
        ORDER BY c.case_id
    """)
    cases = cur.fetchall()

    # crime types for dropdown
    cur.execute("SELECT type_id, type_name FROM crime_type")
    crime_types = cur.fetchall()

    conn.close()

    open_cases = sum(1 for c in cases if c["status"] == "Open")
    closed_cases = sum(1 for c in cases if c["status"] == "Closed")

    return render_template(
        "gui.html",
        cases=cases,
        crime_types=crime_types,
        total_cases=len(cases),
        open_cases=open_cases,
        closed_cases=closed_cases,
        detail=detail
    )


    # load list again for UI
    return redirect(url_for('index', detail=detail))


# Close Case
@app.route("/case/close/<int:case_id>")
def close_case(case_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("UPDATE crime_case SET status='Closed' WHERE case_id=%s", (case_id,))
    conn.commit()
    conn.close()
    return redirect("/")


# Delete Case
@app.route("/case/delete/<int:case_id>", methods=["POST"])
def delete_case(case_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM crime_case WHERE case_id=%s", (case_id,))
    conn.commit()
    conn.close()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
