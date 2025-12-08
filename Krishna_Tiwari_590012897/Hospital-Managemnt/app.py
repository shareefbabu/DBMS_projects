from flask import Flask, render_template, request, redirect
import mysql.connector

app = Flask(__name__)

# ---------------------------
# DATABASE CONNECTION
# ---------------------------
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="766721",
    database="HospitalDB",
    auth_plugin="mysql_native_password"
)
cursor = db.cursor()


# ---------------------------
# HOME PAGE
# ---------------------------
@app.route('/')
def index():
    return render_template(
        "index.html",
        page_title="Welcome to Hospital Management System",
        page_subtitle="Manage patients, doctors, and appointments easily."
    )


# Contact form handler
@app.route('/send_message', methods=['POST'])
def send_message():
    name = request.form["name"]
    email = request.form["email"]
    message = request.form["message"]
    print("\nCONTACT MESSAGE RECEIVED:")
    print("Name:", name)
    print("Email:", email)
    print("Message:", message)
    return "<h2>Message Sent! Thank you.</h2><a href='/'>Return Home</a>"


# ---------------------------
# PATIENT MODULE (CRUD)
# ---------------------------

@app.route('/add_patient')
def add_patient():
    return render_template(
        "add_patient.html",
        page_title="Add Patient",
        page_subtitle="Fill the required information."
    )


@app.route('/save_patient', methods=['POST'])
def save_patient():
    q = "INSERT INTO Patient (Name, Age, Gender, Address, Phone, Disease) VALUES (%s,%s,%s,%s,%s,%s)"
    vals = (
        request.form["name"],
        request.form["age"],
        request.form["gender"],
        request.form["address"],
        request.form["phone"],
        request.form["disease"]
    )
    cursor.execute(q, vals)
    db.commit()
    return redirect('/view_patients')


@app.route('/view_patients')
def view_patients():
    cursor.execute("SELECT * FROM Patient")
    data = cursor.fetchall()
    return render_template(
        "view_patients.html",
        patients=data,
        page_title="Patient Records",
        page_subtitle="View and manage patient details."
    )


@app.route('/edit_patient/<int:id>')
def edit_patient(id):
    cursor.execute("SELECT * FROM Patient WHERE Patient_ID=%s", (id,))
    p = cursor.fetchone()
    return render_template(
        "edit_patient.html",
        patient=p,
        page_title="Edit Patient",
        page_subtitle="Update patient details."
    )


@app.route('/update_patient', methods=['POST'])
def update_patient():
    q = """UPDATE Patient SET 
            Name=%s, Age=%s, Gender=%s, Address=%s, Phone=%s, Disease=%s 
           WHERE Patient_ID=%s"""
    vals = (
        request.form["name"],
        request.form["age"],
        request.form["gender"],
        request.form["address"],
        request.form["phone"],
        request.form["disease"],
        request.form["id"]
    )
    cursor.execute(q, vals)
    db.commit()
    return redirect('/view_patients')


@app.route('/delete_patient/<int:id>')
def delete_patient(id):
    cursor.execute("DELETE FROM Patient WHERE Patient_ID=%s", (id,))
    db.commit()
    return redirect('/view_patients')


# ---------------------------
# DOCTOR MODULE (CRUD)
# ---------------------------

@app.route('/add_doctor')
def add_doctor():
    return render_template(
        "add_doctor.html",
        page_title="Add Doctor",
        page_subtitle="Register a new doctor."
    )


@app.route('/save_doctor', methods=['POST'])
def save_doctor():
    q = "INSERT INTO Doctor (Name, Specialization, Phone, Salary) VALUES (%s,%s,%s,%s)"
    vals = (
        request.form["name"],
        request.form["specialization"],
        request.form["phone"],
        request.form["salary"]
    )
    cursor.execute(q, vals)
    db.commit()
    return redirect('/view_doctors')


@app.route('/view_doctors')
def view_doctors():
    cursor.execute("SELECT * FROM Doctor")
    data = cursor.fetchall()
    return render_template(
        "view_doctors.html",
        doctors=data,
        page_title="Doctor Directory",
        page_subtitle="Manage doctor details."
    )

# EDIT DOCTOR
@app.route('/edit_doctor/<int:id>')
def edit_doctor(id):
    cursor.execute("SELECT * FROM Doctor WHERE Doctor_ID=%s", (id,))
    d = cursor.fetchone()
    return render_template(
        "edit_doctor.html",
        doctor=d,
        page_title="Edit Doctor",
        page_subtitle="Update doctor information."
    )

# UPDATE DOCTOR
@app.route('/update_doctor', methods=['POST'])
def update_doctor():
    q = """UPDATE Doctor SET 
            Name=%s, Specialization=%s, Phone=%s, Salary=%s 
           WHERE Doctor_ID=%s"""
    vals = (
        request.form["name"],
        request.form["specialization"],
        request.form["phone"],
        request.form["salary"],
        request.form["id"]
    )
    cursor.execute(q, vals)
    db.commit()
    return redirect('/view_doctors')


# DELETE DOCTOR
@app.route('/delete_doctor/<int:id>')
def delete_doctor(id):
    cursor.execute("DELETE FROM Doctor WHERE Doctor_ID=%s", (id,))
    db.commit()
    return redirect('/view_doctors')


# ---------------------------
# APPOINTMENT MODULE (CRUD)
# ---------------------------

@app.route('/add_appointment')
def add_appointment():
    return render_template(
        "add_appointment.html",
        page_title="Add Appointment",
        page_subtitle="Schedule a new appointment."
    )


@app.route('/save_appointment', methods=['POST'])
def save_appointment():
    q = "INSERT INTO Appointment (Patient_ID, Doctor_ID, Date, Time, Status) VALUES (%s,%s,%s,%s,%s)"
    vals = (
        request.form["patient_id"],
        request.form["doctor_id"],
        request.form["date"],
        request.form["time"],
        request.form["status"]
    )
    cursor.execute(q, vals)
    db.commit()
    return redirect('/view_appointments')


@app.route('/view_appointments')
def view_appointments():
    cursor.execute("SELECT * FROM Appointment")
    data = cursor.fetchall()
    return render_template(
        "view_appointments.html",
        appointments=data,
        page_title="Appointment Records",
        page_subtitle="View and manage appointments."
    )


@app.route('/edit_appointment/<int:id>')
def edit_appointment(id):
    cursor.execute("SELECT * FROM Appointment WHERE App_ID=%s", (id,))
    ap = cursor.fetchone()
    return render_template(
        "edit_appointment.html",
        appt=ap,
        page_title="Edit Appointment",
        page_subtitle="Modify appointment details."
    )


@app.route('/update_appointment', methods=['POST'])
def update_appointment():
    q = "UPDATE Appointment SET Status=%s WHERE App_ID=%s"
    vals = (request.form["status"], request.form["id"])
    cursor.execute(q, vals)
    db.commit()
    return redirect('/view_appointments')


# ---------------------------
# RUN APP
# ---------------------------
if __name__ == "__main__":
    app.run(debug=True)