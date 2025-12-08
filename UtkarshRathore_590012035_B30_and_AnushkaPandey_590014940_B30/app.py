from flask import Flask, render_template, request, redirect, url_for, flash
from db import query
import os

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev")

@app.route("/")
def index():
    counts = {
        "pets": query("SELECT COUNT(*) c FROM pets", fetchone=True)["c"],
        "adopters": query("SELECT COUNT(*) c FROM adopters", fetchone=True)["c"],
        "apps": query("SELECT COUNT(*) c FROM adoption_applications", fetchone=True)["c"],
        "medical": query("SELECT COUNT(*) c FROM medical_records", fetchone=True)["c"],
    }
    recent_joined = query(
        "SELECT COUNT(*) c FROM pets WHERE arrival_date >= CURDATE() - INTERVAL 30 DAY",
        fetchone=True
    )["c"]
    featured = query(
        "SELECT pet_id, name, species FROM pets ORDER BY arrival_date DESC LIMIT 6",
        fetchall=True
    )
    return render_template("index.html", counts=counts, recent_joined=recent_joined, featured=featured)

# ---------------------- PETS ----------------------

@app.route("/pets")
def pets_list():
    q = request.args.get("q", "").strip()
    species_filter = request.args.get("species")

    params = []
    where = []

    if q:
        where.append("(name LIKE %s OR species LIKE %s OR breed LIKE %s)")
        like = f"%{q}%"
        params.extend([like, like, like])

    if species_filter:
        where.append("species=%s")
        params.append(species_filter)

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    pets = query(
        f"SELECT * FROM pets {where_sql} ORDER BY pet_id DESC",
        params,
        fetchall=True,
    )

    species_summary = query(
        "SELECT species, COUNT(*) AS total FROM pets GROUP BY species",
        fetchall=True,
    )
    recent_joined = query(
        "SELECT COUNT(*) c FROM pets WHERE arrival_date >= CURDATE() - INTERVAL 30 DAY",
        fetchone=True
    )["c"]

    return render_template(
        "pets_list.html",
        pets=pets,
        species_summary=species_summary,
        recent_joined=recent_joined,
        q=q,
        species_filter=species_filter,
    )


@app.route("/pets/new", methods=["GET", "POST"])
def pets_new():
    if request.method == "POST":
        sql = """
            INSERT INTO pets (name, species, breed, age, gender, status, arrival_date, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        params = (
            request.form["name"],
            request.form["species"],
            request.form.get("breed"),
            request.form.get("age"),
            request.form.get("gender"),
            request.form.get("status"),
            request.form.get("arrival_date"),
            request.form.get("description"),
        )

        query(sql, params, commit=True)
        flash("Pet added.", "success")
        return redirect(url_for("pets_list"))

    return render_template("pets_form.html", pet=None)


@app.route("/pets/<int:pet_id>/delete", methods=["POST"])
def pets_delete(pet_id):
    query("DELETE FROM pets WHERE pet_id=%s", (pet_id,), commit=True)
    flash("Pet deleted.", "info")
    return redirect(url_for("pets_list"))


# ---------------------- ADOPTERS ----------------------

@app.route("/adopters")
def adopters_list():
    q = request.args.get("q", "").strip()

    if q:
        like = f"%{q}%"
        rows = query(
            "SELECT * FROM adopters WHERE full_name LIKE %s OR email LIKE %s OR address LIKE %s ORDER BY adopter_id DESC",
            (like, like, like),
            fetchall=True,
        )
    else:
        rows = query("SELECT * FROM adopters ORDER BY adopter_id DESC", fetchall=True)

    return render_template("adopters_list.html", adopters=rows, q=q)


@app.route("/adopters/new", methods=["GET", "POST"])
def adopters_new():
    if request.method == "POST":
        sql = "INSERT INTO adopters (full_name, email, phone, address) VALUES (%s, %s, %s, %s)"
        params = (
            request.form["full_name"],
            request.form["email"],
            request.form.get("phone"),
            request.form.get("address")
        )

        try:
            query(sql, params, commit=True)
            flash("Adopter added.", "success")
            return redirect(url_for("adopters_list"))
        except Exception as e:
            flash(f"Error: {e}", "danger")

    return render_template("adopters_form.html", adopter=None)


@app.route("/adopters/<int:adopter_id>/delete", methods=["POST"])
def adopters_delete(adopter_id):
    query("DELETE FROM adopters WHERE adopter_id=%s", (adopter_id,), commit=True)
    flash("Adopter deleted.", "info")
    return redirect(url_for("adopters_list"))


# ---------------------- APPLICATIONS ----------------------

@app.route("/applications")
def apps_list():
    rows = query(
        """
        SELECT a.application_id, a.application_date, a.status, a.notes,
               p.name AS pet_name, p.species AS pet_species,
               ad.full_name AS adopter_name
        FROM adoption_applications a
        JOIN pets p ON p.pet_id=a.pet_id
        JOIN adopters ad ON ad.adopter_id=a.adopter_id
        ORDER BY a.application_id DESC
        """,
        fetchall=True,
    )
    return render_template("apps_list.html", apps=rows)


@app.route("/applications/new", methods=["GET", "POST"])
def apps_new():
    if request.method == "POST":
        sql = """
            INSERT INTO adoption_applications (pet_id, adopter_id, status, notes)
            VALUES (%s, %s, %s, %s)
        """
        params = (
            int(request.form["pet_id"]),
            int(request.form["adopter_id"]),
            request.form.get("status", "Pending"),
            request.form.get("notes"),
        )

        try:
            query(sql, params, commit=True)
            flash("Application added.", "success")
            return redirect(url_for("apps_list"))
        except Exception as e:
            flash(f"Error: {e}", "danger")

    pets = query("SELECT pet_id, name, species FROM pets ORDER BY name", fetchall=True)
    adopters = query("SELECT adopter_id, full_name FROM adopters ORDER BY full_name", fetchall=True)

    return render_template("apps_form.html", pets=pets, adopters=adopters)


@app.route("/applications/<int:application_id>/status", methods=["POST"])
def apps_update_status(application_id):
    new_status = request.form.get("status", "Pending")
    query(
        "UPDATE adoption_applications SET status=%s WHERE application_id=%s",
        (new_status, application_id),
        commit=True,
    )
    flash("Status updated.", "success")
    return redirect(url_for("apps_list"))


@app.route("/applications/<int:application_id>/delete", methods=["POST"])
def apps_delete(application_id):
    query("DELETE FROM adoption_applications WHERE application_id=%s", (application_id,), commit=True)
    flash("Application deleted.", "info")
    return redirect(url_for("apps_list"))


# ---------------------- MEDICAL ----------------------

@app.route("/medical")
def medical_list():
    status = request.args.get("status")

    params = []
    where = []

    if status == "healthy":
        where.append("health_condition LIKE %s")
        params.append("%Healthy%")
    elif status == "unhealthy":
        where.append("NOT (health_condition LIKE %s)")
        params.append("%Healthy%")

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    rows = query(
        f"""
        SELECT m.*, p.name AS pet_name
        FROM medical_records m
        JOIN pets p ON p.pet_id=m.pet_id
        {where_sql}
        ORDER BY m.record_id DESC
        """,
        params,
        fetchall=True,
    )

    return render_template("medical_list.html", records=rows, status=status)


@app.route("/medical/new", methods=["GET", "POST"])
def medical_new():
    if request.method == "POST":
        sql = """
            INSERT INTO medical_records (pet_id, checkup_date, vaccination, health_condition, treatment, next_due)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            int(request.form["pet_id"]),
            request.form.get("checkup_date") or None,
            request.form.get("vaccination"),
            request.form.get("health_condition"),
            request.form.get("treatment"),
            request.form.get("next_due") or None,
        )

        try:
            query(sql, params, commit=True)
            flash("Medical record added.", "success")
            return redirect(url_for("medical_list"))
        except Exception as e:
            flash(f"Error: {e}", "danger")

    pets = query("SELECT pet_id, name FROM pets ORDER BY name", fetchall=True)
    return render_template("medical_form.html", pets=pets)


@app.route("/medical/<int:record_id>/delete", methods=["POST"])
def medical_delete(record_id):
    query("DELETE FROM medical_records WHERE record_id=%s", (record_id,), commit=True)
    flash("Record deleted.", "info")
    return redirect(url_for("medical_list"))


if __name__ == "__main__":
    app.run(debug=True)
