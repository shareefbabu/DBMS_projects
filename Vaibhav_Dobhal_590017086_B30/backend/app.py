from flask import Flask, request, jsonify
from flask_cors import CORS
import db

app = Flask(__name__)
CORS(app)

# -----------------------------
# ADD STUDENT
# -----------------------------
@app.route("/add_student", methods=["POST"])
def add_student():
    data = request.form
    name = data["name"]
    roll_no = data["roll_no"]
    contact = data.get("contact", "")
    email = data.get("email", "")
    room_no = data.get("room_no", None)

    conn = db.get_connection()
    cursor = conn.cursor()

    query = "INSERT INTO students(name, roll_no, contact, email, room_no) VALUES (%s,%s,%s,%s,%s)"
    cursor.execute(query, (name, roll_no, contact, email, room_no))
    conn.commit()

    return jsonify({"message": "Student Added Successfully!"})


# -----------------------------
# ROOM ALLOCATION
# -----------------------------
@app.route("/allocate_room", methods=["POST"])
def allocate_room():
    roll_no = request.form["roll_no"]
    room_no = request.form["room_no"]

    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE students SET room_no=%s WHERE roll_no=%s", (room_no, roll_no))
    conn.commit()

    return jsonify({"message": "Room allocated successfully!"})


# -----------------------------
# MESS ATTENDANCE
# -----------------------------
@app.route("/record_attendance", methods=["POST"])
def record_attendance():
    roll_no = request.form["roll_no"]
    date = request.form["date"]
    status = request.form["status"]

    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT student_id FROM students WHERE roll_no=%s", (roll_no,))
    student_id = cursor.fetchone()

    if student_id:
        cursor.execute(
            "INSERT INTO mess_attendance(student_id, attendance_date, status) VALUES (%s,%s,%s)",
            (student_id[0], date, status)
        )
        conn.commit()
        return jsonify({"message": "Attendance Recorded!"})
    else:
        return jsonify({"error": "Student not found"})


# -----------------------------
# COMPLAINT SUBMISSION
# -----------------------------
@app.route("/submit_complaint", methods=["POST"])
def submit_complaint():
    roll_no = request.form["roll_no"]
    complaint_text = request.form["complaint_text"]

    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT student_id FROM students WHERE roll_no=%s", (roll_no,))
    student = cursor.fetchone()

    if student:
        cursor.execute(
            "INSERT INTO complaints(student_id, complaint_text) VALUES (%s,%s)",
            (student[0], complaint_text)
        )
        conn.commit()
        return jsonify({"message": "Complaint Submitted!"})
    else:
        return jsonify({"error": "Invalid Roll Number"})


# -----------------------------
# FEE MANAGEMENT
# -----------------------------
@app.route("/fee_update", methods=["POST"])
def fee_update():
    roll_no = request.form["roll_no"]
    hostel_fee = int(request.form["hostel_fee"])
    mess_fee = int(request.form["mess_fee"])

    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT student_id FROM students WHERE roll_no=%s", (roll_no,))
    student_id = cursor.fetchone()

    total_fee = hostel_fee + mess_fee

    if student_id:
        cursor.execute(
            "INSERT INTO fee(student_id, hostel_fee, mess_fee, total_fee, pending_fee) VALUES (%s,%s,%s,%s,%s)",
            (student_id[0], hostel_fee, mess_fee, total_fee, total_fee)
        )
        conn.commit()
        return jsonify({"message": "Fee Record Saved!"})
    else:
        return jsonify({"error": "Student not found"})
# -----------------------------
# ADMIN LOGIN
# -----------------------------
@app.route("/admin_login", methods=["POST"])
def admin_login():
    username = request.form["username"]
    password = request.form["password"]

    conn = db.get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (username, password))
    admin = cursor.fetchone()

    if admin:
        return jsonify({"login": "success", "redirect": "/admin_dashboard"})
    else:
        return jsonify({"login": "failed", "message": "Invalid username or password"})
# -----------------------------
# VIEW STUDENTS
# -----------------------------
@app.route("/get_students", methods=["GET"])
def get_students():
    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM students")
    result = cursor.fetchall()
    return jsonify(result)

@app.route("/get_rooms", methods=["GET"])
def get_rooms():
    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT room_no, capacity, occupied, (capacity - occupied) AS vacancy FROM rooms")
    result = cursor.fetchall()
    return jsonify(result)

@app.route("/get_mess_attendance", methods=["GET"])
def get_mess_attendance():
    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT a.attendance_date, s.name, s.roll_no, a.status 
        FROM mess_attendance a 
        JOIN students s ON s.student_id = a.student_id
    """)
    result = cursor.fetchall()
    return jsonify(result)

@app.route("/get_fees", methods=["GET"])
def get_fees():
    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.name, s.roll_no, f.total_fee, f.paid_fee, f.pending_fee
        FROM fee f
        JOIN students s ON s.student_id = f.student_id
    """)
    return jsonify(cursor.fetchall())

@app.route("/get_complaints", methods=["GET"])
def get_complaints():
    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT c.complaint_id, s.name, s.roll_no, c.complaint_text, c.status 
        FROM complaints c
        JOIN students s ON s.student_id = c.student_id
    """)
    return jsonify(cursor.fetchall())


@app.route("/search_student", methods=["GET"])
def search_student():
    q = request.args.get("q")
    conn = db.get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT * FROM students 
        WHERE name LIKE %s OR roll_no LIKE %s OR room_no LIKE %s
    """, (f"%{q}%", f"%{q}%", f"%{q}%"))
    return jsonify(cursor.fetchall())




# -----------------------------
# RUN SERVER
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
