import pymysql
from flask import Flask, render_template, request, redirect, url_for, flash
from db_config import DB_CONFIG

app = Flask(__name__)
app.secret_key = "HappyisaGreatGuy"  # NOTE DO NOT Change this!


def get_db_connection():
    """Establishes a database connection."""

    cursorclass = DB_CONFIG.get("cursorclass", pymysql.cursors.DictCursor)
    try:
        connection = pymysql.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database=DB_CONFIG["database"],
            port=DB_CONFIG["port"],
            charset=DB_CONFIG.get("charset", "utf8mb4"),
            cursorclass=cursorclass,
            ssl={"ssl_mode": "REQUIRED"},
        )
        return connection
    except pymysql.Error as e:
        flash(f"Database connection error: {e}", "error")
        return None


@app.route("/")
def index():
    """Homepage: Shows upcoming appointments."""
    conn = get_db_connection()
    if not conn:
        return render_template("index.html", appointments=[])
    try:
        with conn.cursor() as cursor:
            # Use the view to get upcoming appointments
            cursor.execute(
                "SELECT * FROM upcoming_appointments_view ORDER BY appointment_date ASC"
            )
            appointments = cursor.fetchall()
    except pymysql.Error as e:
        flash(f"Error fetching appointments: {e}", "error")
        appointments = []
    finally:
        conn.close()
    return render_template("index.html", appointments=appointments)


@app.route("/patients")
def list_patients():
    """Lists all patients."""
    conn = get_db_connection()
    if not conn:
        return render_template("patients.html", patients=[])
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT patient_id, name, calculate_age(dob) as age, gender, email FROM patient ORDER BY name"
            )
            patients = cursor.fetchall()
    except pymysql.Error as e:
        flash(f"Error fetching patients: {e}", "error")
        patients = []
    finally:
        conn.close()
    return render_template("patients.html", patients=patients)


@app.route("/doctors")
def list_doctors():
    """Lists active doctors using the view."""
    conn = get_db_connection()
    if not conn:
        return render_template("doctors.html", doctors=[])
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM active_doctors_view ORDER BY doctor_name")
            doctors = cursor.fetchall()
    except pymysql.Error as e:
        flash(f"Error fetching doctors: {e}", "error")
        doctors = []
    finally:
        conn.close()
    return render_template("doctors.html", doctors=doctors)


@app.route("/appointments")
def list_appointments():
    """Lists all appointments, including past and canceled."""
    conn = get_db_connection()
    if not conn:
        return render_template("appointments.html", appointments=[])
    try:
        with conn.cursor() as cursor:
            # Fetch details using joins
            sql = """
                SELECT a.appointment_id, a.appointment_date, a.status, a.reason,
                       p.name AS patient_name, d.name AS doctor_name, dep.name AS department_name
                FROM appointment a
                JOIN patient p ON a.patient_id = p.patient_id
                JOIN doctor d ON a.doctor_id = d.doctor_id
                JOIN department dep ON d.department_id = dep.department_id
                ORDER BY a.appointment_date DESC
            """
            cursor.execute(sql)
            appointments = cursor.fetchall()
    except pymysql.Error as e:
        flash(f"Error fetching appointments: {e}", "error")
        appointments = []
    finally:
        conn.close()
    return render_template("appointments.html", appointments=appointments)


@app.route("/appointments/schedule", methods=["GET", "POST"])
def schedule_appointment():
    """Handles scheduling a new appointment using the procedure."""
    conn = get_db_connection()
    if not conn:
        return redirect(url_for("index"))  # Or show an error page

    patients = []
    doctors = []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT patient_id, name FROM patient ORDER BY name")
            patients = cursor.fetchall()
            cursor.execute("SELECT doctor_id, name FROM doctor ORDER BY name")
            doctors = cursor.fetchall()
    except pymysql.Error as e:
        flash(f"Error fetching patients/doctors: {e}", "error")
        pass  # Keep empty lists

    if request.method == "POST":
        patient_id = request.form.get("patient_id")
        doctor_id = request.form.get("doctor_id")
        appointment_date = request.form.get("appointment_date")
        reason = request.form.get("reason", "")

        if not all([patient_id, doctor_id, appointment_date]):
            flash("Missing required fields for scheduling.", "warning")
            return render_template(
                "schedule_appointment.html",
                patients=patients,
                doctors=doctors,
                now=datetime.now(),
            )

        # Validate appointment date is in the future
        from datetime import datetime

        try:
            appointment_datetime = datetime.strptime(appointment_date, "%Y-%m-%dT%H:%M")
            if appointment_datetime <= datetime.now():
                flash(
                    "Appointment must be scheduled for a future date and time.", "error"
                )
                return render_template(
                    "schedule_appointment.html",
                    patients=patients,
                    doctors=doctors,
                    now=datetime.now(),
                )
            with conn.cursor() as cursor:
                cursor.callproc(
                    "schedule_appointment",
                    (patient_id, doctor_id, appointment_date, reason),
                )
                conn.commit()
                flash("Appointment scheduled successfully!", "success")
                return redirect(url_for("list_appointments"))
        except pymysql.Error as e:
            conn.rollback()
            # Check for specific trigger message
            if "45000" in str(e) and "already booked" in str(e):
                flash(
                    "Scheduling failed: Doctor is already booked around this time.",
                    "error",
                )
            else:
                flash(f"Error scheduling appointment: {e}", "error")
            return render_template(
                "schedule_appointment.html",
                patients=patients,
                doctors=doctors,
                now=datetime.now(),
            )
        finally:
            conn.close()

    # If GET request, just show the form
    from datetime import datetime
    from datetime import datetime

    return render_template(
        "schedule_appointment.html",
        patients=patients,
        doctors=doctors,
        now=datetime.now(),
    )


@app.route("/appointments/<int:appointment_id>/cancel", methods=["POST"])
def cancel_appointment(appointment_id):
    """Cancels an appointment using the procedure."""
    conn = get_db_connection()
    if not conn:
        return redirect(url_for("list_appointments"))
    try:
        with conn.cursor() as cursor:
            cursor.callproc("cancel_appointment", (appointment_id,))
        conn.commit()
        flash("Appointment canceled.", "info")
    except pymysql.Error as e:
        conn.rollback()
        flash(f"Error canceling appointment: {e}", "error")
    finally:
        conn.close()
    return redirect(url_for("list_appointments"))


# --- NOTE routes for completing appointments, viewing patient history etc. NOTE ---
@app.route("/patients/<int:patient_id>/history")
def patient_history(patient_id):
    conn = get_db_connection()
    if not conn:
        return render_template(
            "patient_history.html", history=[], patient_name="Unknown"
        )

    history = []
    patient_name = "Unknown"
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT name FROM patient WHERE patient_id = %s", (patient_id,)
            )
            patient_result = cursor.fetchone()
            if patient_result:
                patient_name = patient_result["name"]

            # Use the view for history
            cursor.execute(
                "SELECT * FROM patient_medical_history_view WHERE patient_id = %s ORDER BY visit_date DESC",
                (patient_id,),
            )
            history = cursor.fetchall()
    except pymysql.Error as e:
        flash(f"Error fetching patient history: {e}", "error")
    finally:
        conn.close()
    return render_template(
        "patient_history.html", history=history, patient_name=patient_name
    )


@app.route("/appointments/<int:appointment_id>/complete", methods=["GET", "POST"])
def complete_appointment(appointment_id):
    """Handles completing an appointment and generating a bill."""
    conn = get_db_connection()
    if not conn:
        return redirect(url_for("list_appointments"))

    try:
        with conn.cursor() as cursor:
            # Get appointment details first
            sql = """
                SELECT a.*, p.name as patient_name, d.name as doctor_name
                FROM appointment a
                JOIN patient p ON a.patient_id = p.patient_id
                JOIN doctor d ON a.doctor_id = d.doctor_id
                WHERE a.appointment_id = %s AND a.status = 'Scheduled'
            """
            cursor.execute(sql, (appointment_id,))
            appointment = cursor.fetchone()

            if not appointment:
                flash("Appointment not found or already completed/canceled.", "error")
                return redirect(url_for("list_appointments"))

            # Check if appointment date has arrived
            from datetime import datetime

            if appointment["appointment_date"] > datetime.now():
                flash(
                    "Cannot complete an appointment before its scheduled date.", "error"
                )
                return redirect(url_for("list_appointments"))

            if request.method == "POST":
                diagnosis = request.form.get("diagnosis")
                treatment = request.form.get("treatment")
                amount = request.form.get("amount")

                if not all([diagnosis, treatment, amount]):
                    flash("Please fill in all required fields.", "warning")
                else:
                    try:
                        cursor.callproc(
                            "complete_appointment_with_billing",
                            (appointment_id, diagnosis, treatment, float(amount)),
                        )
                        conn.commit()
                        flash(
                            "Appointment completed and bill generated successfully!",
                            "success",
                        )
                        return redirect(url_for("list_appointments"))
                    except pymysql.Error as e:
                        conn.rollback()
                        flash(f"Error completing appointment: {e}", "error")

    except pymysql.Error as e:
        flash(f"Database error: {e}", "error")
        return redirect(url_for("list_appointments"))
    finally:
        conn.close()

    return render_template("complete_appointment.html", appointment=appointment)


@app.route("/doctors/workload")
def doctor_workload():
    """Shows doctors' schedules and appointment statistics."""
    conn = get_db_connection()
    if not conn:
        return render_template("doctor_workload.html", doctors=[])

    try:
        with conn.cursor() as cursor:
            doctors = []
            # Get all active doctors
            cursor.execute("SELECT * FROM active_doctors_view")
            all_doctors = cursor.fetchall()

            for doctor in all_doctors:
                # Get today's and this week's appointments
                cursor.execute(
                    """
                    SELECT 
                        SUM(CASE 
                            WHEN status = 'Scheduled' 
                            AND DATE(appointment_date) = CURDATE() 
                            THEN 1 ELSE 0 END) as today_scheduled,                        SUM(CASE 
                            WHEN status = 'Completed' 
                            THEN 1 ELSE 0 END) as today_completed,
                        SUM(CASE 
                            WHEN appointment_date BETWEEN DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND CURDATE()
                            AND status != 'Canceled'
                            THEN 1 ELSE 0 END) as week_total,
                        SUM(CASE 
                            WHEN status = 'Completed'
                            AND appointment_date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
                            THEN 1 ELSE 0 END) as week_completed
                    FROM appointment
                    WHERE doctor_id = %s
                """,
                    (doctor["doctor_id"],),
                )
                stats = cursor.fetchone()

                # Get upcoming appointments
                cursor.execute(
                    """
                    SELECT a.appointment_date, p.name as patient_name, a.status
                    FROM appointment a
                    JOIN patient p ON a.patient_id = p.patient_id
                    WHERE a.doctor_id = %s
                    AND a.appointment_date >= CURRENT_DATE
                    AND a.status != 'Canceled'
                    ORDER BY a.appointment_date
                    LIMIT 5
                """,
                    (doctor["doctor_id"],),
                )
                upcoming = cursor.fetchall()

                # Calculate completion rate for the week
                week_total = stats["week_total"] or 0
                week_completed = stats["week_completed"] or 0
                completion_rate = (
                    (week_completed / week_total * 100) if week_total > 0 else 0
                )

                doctor.update(
                    {
                        "today_scheduled": stats["today_scheduled"] or 0,
                        "today_completed": stats["today_completed"] or 0,
                        "week_total": week_total,
                        "completion_rate": completion_rate,
                        "upcoming_appointments": upcoming,
                    }
                )
                doctors.append(doctor)

    except pymysql.Error as e:
        flash(f"Error fetching doctor workload: {e}", "error")
        doctors = []
    finally:
        conn.close()

    return render_template("doctor_workload.html", doctors=doctors)


@app.route("/billing")
def billing_management():
    """Shows billing management interface."""
    conn = get_db_connection()
    if not conn:
        return render_template("billing.html", unpaid_bills=[], paid_bills=[])

    try:
        with conn.cursor() as cursor:
            # Get unpaid bills
            cursor.execute(
                """
                SELECT b.*, p.name as patient_name, d.name as doctor_name,
                       a.appointment_date as service_date
                FROM billing b
                JOIN appointment a ON b.appointment_id = a.appointment_id
                JOIN patient p ON b.patient_id = p.patient_id
                JOIN doctor d ON a.doctor_id = d.doctor_id
                WHERE b.status = 'Unpaid'
                ORDER BY b.bill_date DESC
            """
            )
            unpaid_bills = cursor.fetchall()

            # Get paid bills
            cursor.execute(
                """
                SELECT b.*, p.name as patient_name, d.name as doctor_name,
                       a.appointment_date as service_date
                FROM billing b
                JOIN appointment a ON b.appointment_id = a.appointment_id
                JOIN patient p ON b.patient_id = p.patient_id
                JOIN doctor d ON a.doctor_id = d.doctor_id
                WHERE b.status = 'Paid'
                ORDER BY b.bill_date DESC
                LIMIT 50
            """
            )
            paid_bills = cursor.fetchall()

    except pymysql.Error as e:
        flash(f"Error fetching bills: {e}", "error")
        unpaid_bills = []
        paid_bills = []
    finally:
        conn.close()

    return render_template(
        "billing.html", unpaid_bills=unpaid_bills, paid_bills=paid_bills
    )


@app.route("/billing/<int:bill_id>/mark-paid", methods=["POST"])
def mark_bill_paid(bill_id):
    """Marks a bill as paid."""
    conn = get_db_connection()
    if not conn:
        return redirect(url_for("billing_management"))

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                UPDATE billing 
                SET status = 'Paid',
                    paid_date = CURRENT_TIMESTAMP
                WHERE bill_id = %s
            """,
                (bill_id,),
            )
            conn.commit()
            flash("Bill marked as paid successfully!", "success")
    except pymysql.Error as e:
        conn.rollback()
        flash(f"Error updating bill: {e}", "error")
    finally:
        conn.close()

    return redirect(url_for("billing_management"))


@app.route("/patients/register", methods=["GET", "POST"])
def register_patient():
    """Handles new patient registration."""
    from datetime import datetime

    # Pass the current datetime for the date input's max attribute
    now = datetime.now()

    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        dob = request.form.get("dob")
        gender = request.form.get("gender")
        address = request.form.get("address")

        if not all([name, dob, gender]):
            flash("Please fill in all required fields.", "warning")
            return render_template("register_patient.html", now=now)

        conn = get_db_connection()
        if not conn:
            return redirect(url_for("list_patients"))

        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO patient (name, email, dob, gender, address)
                    VALUES (%s, %s, %s, %s, %s)
                """,
                    (name, email, dob, gender, address),
                )
                conn.commit()
                flash("Patient registered successfully!", "success")
                return redirect(url_for("list_patients"))
        except pymysql.Error as e:
            conn.rollback()
            if "Duplicate entry" in str(e):
                flash("A patient with this email already exists.", "error")
            else:
                flash(f"Error registering patient: {e}", "error")
        finally:
            conn.close()

    return render_template("register_patient.html", now=now)


@app.route("/patients/<int:patient_id>/delete", methods=["POST"])
def delete_patient(patient_id):
    """Deletes a patient and their related records."""
    conn = get_db_connection()
    if not conn:
        return redirect(url_for("list_patients"))

    try:
        with conn.cursor() as cursor:
            # First check if patient has any active appointments
            cursor.execute(
                """
                SELECT COUNT(*) as count 
                FROM appointment 
                WHERE patient_id = %s 
                AND status = 'Scheduled'
                """,
                (patient_id,),
            )
            result = cursor.fetchone()
            if result["count"] > 0:
                # Cancel all scheduled appointments first
                cursor.execute(
                    """
                    UPDATE appointment 
                    SET status = 'Canceled' 
                    WHERE patient_id = %s 
                    AND status = 'Scheduled'
                    """,
                    (patient_id,),
                )

            # Delete related records in correct order due to foreign key constraints
            cursor.execute("DELETE FROM billing WHERE patient_id = %s", (patient_id,))
            cursor.execute(
                "DELETE FROM medical_record WHERE patient_id = %s", (patient_id,)
            )
            cursor.execute(
                "DELETE FROM appointment WHERE patient_id = %s", (patient_id,)
            )
            cursor.execute("DELETE FROM patient WHERE patient_id = %s", (patient_id,))

            conn.commit()
            flash("Patient deleted successfully.", "success")
    except pymysql.Error as e:
        conn.rollback()
        flash(f"Error deleting patient: {e}", "error")
    finally:
        conn.close()

    return redirect(url_for("list_patients"))


if __name__ == "__main__":
    app.run(debug=True)


# Happy Sharma
# 23BCS10596
# DBMS

