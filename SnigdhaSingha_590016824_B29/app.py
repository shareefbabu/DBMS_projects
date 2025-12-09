import os
import re
from functools import wraps
from bson.objectid import ObjectId
from datetime import datetime, date, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, flash
from pymongo import MongoClient

load_dotenv()

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default_secret_key")

# Fine rules
FINE_PER_DAY = 20
LOAN_PERIOD_DAYS = 30
GRACE_PERIOD_DAYS = 7

# MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DATABASE_NAME", "library_db")]
books_collection = db["books"]
students_collection = db["students"]
issues_collection = db["issues"]


# ----------------------------
# DATE PARSING
# ----------------------------
def parse_date(date_str):
    for fmt in ("%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except:
            pass
    raise ValueError(f"Invalid date: {date_str}")


# ----------------------------
# FINE CALCULATION
# ----------------------------
def calculate_fine(issue_date_str, return_date_str=None):
    issue_date = parse_date(issue_date_str)

    if return_date_str:
        return_date = parse_date(return_date_str)
    else:
        return_date = date.today()

    due_date = issue_date + timedelta(days=LOAN_PERIOD_DAYS)

    if return_date <= due_date:
        return 0, 0

    overdue_days = (return_date - due_date).days

    if overdue_days <= GRACE_PERIOD_DAYS:
        return 0, overdue_days

    billable_days = overdue_days - GRACE_PERIOD_DAYS
    fine = billable_days * FINE_PER_DAY
    return fine, overdue_days


# ----------------------------
# ROUTES
# ----------------------------

@app.route("/")
def index():
    books = list(books_collection.find().sort("title", 1))
    return render_template("index.html", books=books)


# --- PAGE 1: STUDENT RECORDS ---
@app.route("/students")
def students_page():
    students = list(students_collection.find().sort("student_id", 1))
    return render_template("students.html", students=students)


# --- PAGE 2: ISSUES PAGE ---
@app.route("/issues")
def issues_page():
    issues = list(issues_collection.find().sort("issue_date", -1))

    for issue in issues:
        fine, overdue = calculate_fine(issue["issue_date"], issue.get("return_date"))
        issue["fine_due"] = fine
        issue["overdue_days"] = overdue

    return render_template("issues.html", issues=issues)


# --- ISSUE A BOOK ---
@app.route("/issue", methods=["POST"])
def issue_book():
    student_id = request.form.get("student_id")
    book_isbn10 = request.form.get("book_isbn10")

    student = students_collection.find_one({"student_id": student_id})
    book = books_collection.find_one({"isbn10": book_isbn10})

    if not student or not book:
        flash("Invalid student or book.", "error")
        return redirect(url_for("issues_page"))

    issues_collection.insert_one({
        "student_id": student_id,
        "student_name": student["name"],
        "book_isbn10": book_isbn10,
        "book_title": book["title"],
        "issue_date": str(date.today()),
        "return_date": None,
        "fine_due": 0,
        "fine_paid": 0
    })

    flash("Book issued!", "success")
    return redirect(url_for("issues_page"))


# --- RETURN BOOK ---
@app.route("/return", methods=["POST"])
def return_book():
    issue_id = request.form.get("issue_id")
    issue = issues_collection.find_one({"_id": ObjectId(issue_id)})

    today = str(date.today())
    fine, overdue = calculate_fine(issue["issue_date"], today)

    issues_collection.update_one(
        {"_id": ObjectId(issue_id)},
        {"$set": {"return_date": today, "fine_due": fine}}
    )

    flash(f"Returned. Fine: Rs {fine}", "info")
    return redirect(url_for("issues_page"))


# --- PAY FINE ---
@app.route("/pay_fine", methods=["POST"])
def pay_fine():
    issue_id = request.form.get("issue_id")
    issue = issues_collection.find_one({"_id": ObjectId(issue_id)})
    fine_due = issue.get("fine_due", 0)

    issues_collection.update_one(
        {"_id": ObjectId(issue_id)},
        {"$set": {"fine_due": 0, "fine_paid": fine_due}}
    )

    flash("Fine paid!", "success")
    return redirect(url_for("issues_page"))


# ----------------------------
# START SERVER
# ----------------------------
if __name__ == "__main__":
    app.run(debug=True, port=5000)
