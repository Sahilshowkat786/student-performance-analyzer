from flask import Flask, render_template, request, redirect, url_for
import math
import re
import sqlite3

from ml_model import FEATURE_COLUMNS, MINIMUM_TRAINING_SAMPLES, train_linear_regression


app = Flask(__name__)

DATABASE = "students.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def validate_student_form(form):
    """Return converted student values and clear form validation errors."""
    text_fields = ("name", "roll", "email")
    score_fields = ("attendance", "assignment", "previous_marks", "python", "dsa", "dbms", "web")
    numeric_fields = ("age", "study_hours", *score_fields)
    values = {field: form.get(field, "").strip() for field in text_fields}
    errors = []

    for field, label in (("name", "Student name"), ("roll", "Roll number"), ("email", "Email")):
        if not values[field]:
            errors.append(f"{label} is required.")

    if values["email"] and not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", values["email"]):
        errors.append("Enter a valid email address.")

    for field in numeric_fields:
        raw_value = form.get(field, "").strip()
        if not raw_value:
            errors.append(f"{field.replace('_', ' ').title()} is required.")
            continue

        try:
            value = int(raw_value) if field == "age" else float(raw_value)
        except ValueError:
            errors.append(f"{field.replace('_', ' ').title()} must be a valid number.")
            continue

        if not math.isfinite(value):
            errors.append(f"{field.replace('_', ' ').title()} must be a finite number.")
            continue

        values[field] = value

        if field == "age" and not 10 <= value <= 100:
            errors.append("Age must be between 10 and 100.")
        elif field == "study_hours" and not 0 <= value <= 24:
            errors.append("Study hours must be between 0 and 24 per day.")
        elif field in score_fields and not 0 <= value <= 100:
            errors.append(f"{field.replace('_', ' ').title()} must be between 0 and 100.")

    return values, errors


def calculate_performance(marks):
    """Calculate derived results consistently from the four subject marks."""
    total = sum(marks.values())
    average = total / len(marks)
    percentage = (total / (len(marks) * 100)) * 100

    if percentage >= 90:
        grade = "A+"
    elif percentage >= 80:
        grade = "A"
    elif percentage >= 70:
        grade = "B"
    elif percentage >= 60:
        grade = "C"
    elif percentage >= 50:
        grade = "D"
    else:
        grade = "F"

    result = "Pass" if percentage >= 40 else "Fail"
    return total, average, percentage, grade, result


@app.errorhandler(404)
def page_not_found(_error):
    return render_template(
        "error.html",
        error_code=404,
        error_title="Page not found",
        error_message="The page or student record you requested could not be found."
    ), 404


@app.errorhandler(500)
def internal_server_error(_error):
    return render_template(
        "error.html",
        error_code=500,
        error_title="Something went wrong",
        error_message="We could not complete that request. Please try again."
    ), 500


# =========================================================
# CREATE DATABASE AND TABLE
# =========================================================

def create_database():
    connection = get_db_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            name TEXT NOT NULL,
            roll TEXT NOT NULL,
            email TEXT NOT NULL,
            age INTEGER NOT NULL,

            attendance REAL NOT NULL,
            study_hours REAL NOT NULL,
            assignment REAL NOT NULL,
            previous_marks REAL NOT NULL,

            python REAL NOT NULL,
            dsa REAL NOT NULL,
            dbms REAL NOT NULL,
            web REAL NOT NULL,

            total REAL NOT NULL,
            average REAL NOT NULL,
            percentage REAL NOT NULL,
            grade TEXT NOT NULL,
            result TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


# =========================================================
# HOME PAGE / DASHBOARD
# =========================================================

@app.route("/")
def home():

    connection = get_db_connection()

    # -----------------------------------------------------
    # GET ALL STUDENTS
    # -----------------------------------------------------

    students = connection.execute("""
        SELECT *
        FROM students
        ORDER BY id DESC
    """).fetchall()

    top_performer = connection.execute("""
        SELECT id, name, percentage
        FROM students
        ORDER BY percentage DESC, id ASC
        LIMIT 1
    """).fetchone()

    # -----------------------------------------------------
    # CALCULATE SUBJECT AVERAGES
    # -----------------------------------------------------

    averages = connection.execute("""
        SELECT
            AVG(python) AS python_avg,
            AVG(dsa) AS dsa_avg,
            AVG(dbms) AS dbms_avg,
            AVG(web) AS web_avg
        FROM students
    """).fetchone()

    # -----------------------------------------------------
    # GRADE DISTRIBUTION
    # -----------------------------------------------------

    grade_counts = connection.execute("""
        SELECT
            grade,
            COUNT(*) AS count
        FROM students
        GROUP BY grade
        ORDER BY
            CASE grade
                WHEN 'A+' THEN 1
                WHEN 'A' THEN 2
                WHEN 'B' THEN 3
                WHEN 'C' THEN 4
                WHEN 'D' THEN 5
                WHEN 'F' THEN 6
                ELSE 7
            END
    """).fetchall()

    # -----------------------------------------------------
    # PASS / FAIL DISTRIBUTION
    # -----------------------------------------------------

    pass_fail = connection.execute("""
        SELECT
            result,
            COUNT(*) AS count
        FROM students
        GROUP BY result
    """).fetchall()

    connection.close()

    # -----------------------------------------------------
    # PREPARE SUBJECT CHART DATA
    # -----------------------------------------------------

    chart_data = [
        round(averages["python_avg"] or 0, 2),
        round(averages["dsa_avg"] or 0, 2),
        round(averages["dbms_avg"] or 0, 2),
        round(averages["web_avg"] or 0, 2)
    ]

    # -----------------------------------------------------
    # PREPARE GRADE CHART DATA
    # -----------------------------------------------------

    grade_labels = [
        row["grade"]
        for row in grade_counts
    ]

    grade_data = [
        row["count"]
        for row in grade_counts
    ]

    # -----------------------------------------------------
    # PREPARE PASS / FAIL CHART DATA
    # -----------------------------------------------------

    pass_fail_labels = [
        row["result"]
        for row in pass_fail
    ]

    pass_fail_data = [
        row["count"]
        for row in pass_fail
    ]

    # -----------------------------------------------------
    # SEND DATA TO DASHBOARD
    # -----------------------------------------------------

    return render_template(
        "index.html",
        students=students,
        top_performer=top_performer,
        chart_data=chart_data,
        grade_labels=grade_labels,
        grade_data=grade_data,
        pass_fail_labels=pass_fail_labels,
        pass_fail_data=pass_fail_data
    )


# =========================================================
# ATTENDANCE VS PERFORMANCE ANALYTICS
# =========================================================

@app.route("/analytics")
def analytics():

    connection = get_db_connection()

    students = connection.execute("""
        SELECT name, attendance, study_hours, assignment, previous_marks, percentage
        FROM students
        ORDER BY id DESC
    """).fetchall()

    summary = connection.execute("""
        SELECT
            COUNT(*) AS total_students,
            AVG(attendance) AS average_attendance,
            AVG(study_hours) AS average_study_hours,
            AVG(assignment) AS average_assignment,
            AVG(previous_marks) AS average_previous_marks,
            AVG(percentage) AS average_percentage,
            AVG(python) AS python_average,
            AVG(dsa) AS dsa_average,
            AVG(dbms) AS dbms_average,
            AVG(web) AS web_average
        FROM students
    """).fetchone()

    grade_counts = connection.execute("""
        SELECT grade, COUNT(*) AS count
        FROM students
        GROUP BY grade
        ORDER BY
            CASE grade
                WHEN 'A+' THEN 1
                WHEN 'A' THEN 2
                WHEN 'B' THEN 3
                WHEN 'C' THEN 4
                WHEN 'D' THEN 5
                WHEN 'F' THEN 6
                ELSE 7
            END
    """).fetchall()

    pass_fail_counts = connection.execute("""
        SELECT result, COUNT(*) AS count
        FROM students
        GROUP BY result
        ORDER BY CASE result WHEN 'Pass' THEN 1 WHEN 'Fail' THEN 2 ELSE 3 END
    """).fetchall()

    connection.close()

    subject_average_data = [
        round(summary["python_average"] or 0, 2),
        round(summary["dsa_average"] or 0, 2),
        round(summary["dbms_average"] or 0, 2),
        round(summary["web_average"] or 0, 2)
    ]

    grade_labels = [row["grade"] for row in grade_counts]
    grade_data = [row["count"] for row in grade_counts]
    pass_fail_labels = [row["result"] for row in pass_fail_counts]
    pass_fail_data = [row["count"] for row in pass_fail_counts]

    attendance_performance_data = [
        {
            "x": round(student["attendance"], 2),
            "y": round(student["percentage"], 2),
            "name": student["name"]
        }
        for student in students
    ]

    study_hours_performance_data = [
        {
            "x": round(student["study_hours"], 2),
            "y": round(student["percentage"], 2),
            "name": student["name"]
        }
        for student in students
    ]

    assignment_performance_data = [
        {
            "x": round(student["assignment"], 2),
            "y": round(student["percentage"], 2),
            "name": student["name"]
        }
        for student in students
    ]

    previous_marks_performance_data = [
        {
            "x": round(student["previous_marks"], 2),
            "y": round(student["percentage"], 2),
            "name": student["name"]
        }
        for student in students
    ]

    return render_template(
        "analytics.html",
        total_students=summary["total_students"],
        average_attendance=round(summary["average_attendance"] or 0, 2),
        average_study_hours=round(summary["average_study_hours"] or 0, 2),
        average_assignment=round(summary["average_assignment"] or 0, 2),
        average_previous_marks=round(summary["average_previous_marks"] or 0, 2),
        average_percentage=round(summary["average_percentage"] or 0, 2),
        subject_average_data=subject_average_data,
        grade_labels=grade_labels,
        grade_data=grade_data,
        pass_fail_labels=pass_fail_labels,
        pass_fail_data=pass_fail_data,
        attendance_performance_data=attendance_performance_data,
        study_hours_performance_data=study_hours_performance_data,
        assignment_performance_data=assignment_performance_data,
        previous_marks_performance_data=previous_marks_performance_data
    )


# =========================================================
# ML PERFORMANCE PREDICTION
# =========================================================

@app.route("/prediction", methods=["GET", "POST"])
def prediction():

    connection = get_db_connection()

    training_records = connection.execute("""
        SELECT attendance, study_hours, assignment, previous_marks, percentage
        FROM students
        ORDER BY id
    """).fetchall()

    connection.close()

    model_report = train_linear_regression(training_records)
    form_values = {feature: "" for feature in FEATURE_COLUMNS}
    form_error = None
    prediction_message = None
    prediction_note = None
    predicted_percentage = None
    inputs_used = None

    if request.method == "POST":

        form_values = {
            feature: request.form.get(feature, "").strip()
            for feature in FEATURE_COLUMNS
        }

        try:
            inputs_used = {
                feature: float(form_values[feature])
                for feature in FEATURE_COLUMNS
            }
        except (TypeError, ValueError):
            form_error = "Enter a valid number for each field."
            inputs_used = None

        if inputs_used is not None:

            if not all(math.isfinite(value) for value in inputs_used.values()):
                form_error = "Enter finite numeric values for every field."

            elif not 0 <= inputs_used["attendance"] <= 100:
                form_error = "Attendance must be between 0 and 100 percent."

            elif inputs_used["study_hours"] < 0:
                form_error = "Study hours cannot be negative."

            elif not 0 <= inputs_used["assignment"] <= 100:
                form_error = "Assignment score must be between 0 and 100 percent."

            elif not 0 <= inputs_used["previous_marks"] <= 100:
                form_error = "Previous marks must be between 0 and 100 percent."

        if form_error is None:

            if not model_report["ready"]:
                prediction_message = (
                    "No prediction was generated. The model needs at least "
                    f"{MINIMUM_TRAINING_SAMPLES} saved student records; "
                    f"the database currently has {model_report['sample_count']}. "
                    "Your submitted values are shown below."
                )

            else:
                feature_row = [[
                    inputs_used[feature]
                    for feature in FEATURE_COLUMNS
                ]]

                raw_prediction = float(
                    model_report["model"].predict(feature_row)[0]
                )
                bounded_prediction = min(100.0, max(0.0, raw_prediction))
                predicted_percentage = round(bounded_prediction, 2)

                if bounded_prediction != raw_prediction:
                    prediction_note = (
                        "The linear model estimated a value outside the valid "
                        "0-100 range, so the displayed percentage is limited "
                        "to that range."
                    )

    return render_template(
        "prediction.html",
        model_report=model_report,
        form_values=form_values,
        form_error=form_error,
        prediction_message=prediction_message,
        prediction_note=prediction_note,
        predicted_percentage=predicted_percentage,
        inputs_used=inputs_used,
        feature_columns=FEATURE_COLUMNS
    )

# =========================================================
# STUDENTS PAGE
# SEARCH + SORT + PAGINATION
# =========================================================

@app.route("/students")
def students():

    search = request.args.get(
        "search",
        ""
    ).strip()

    sort = request.args.get(
        "sort",
        "latest"
    )

    page = request.args.get(
        "page",
        1,
        type=int
    )

    per_page = 10

    if page < 1:
        page = 1

    offset = (page - 1) * per_page

    connection = get_db_connection()

    # -----------------------------------------------------
    # SEARCH
    # -----------------------------------------------------

    if search:

        query = """
            SELECT *
            FROM students
            WHERE name LIKE ?
            OR roll LIKE ?
        """

        params = (
            f"%{search}%",
            f"%{search}%"
        )

    else:

        query = """
            SELECT *
            FROM students
        """

        params = ()

    # -----------------------------------------------------
    # SORTING
    # -----------------------------------------------------

    if sort == "highest":

        query += """
            ORDER BY percentage DESC
        """

    elif sort == "lowest":

        query += """
            ORDER BY percentage ASC
        """

    elif sort == "name_asc":

        query += """
            ORDER BY name ASC
        """

    elif sort == "name_desc":

        query += """
            ORDER BY name DESC
        """

    else:

        query += """
            ORDER BY id DESC
        """

    # -----------------------------------------------------
    # COUNT TOTAL STUDENTS
    # -----------------------------------------------------

    if search:

        total_students = connection.execute(
            """
            SELECT COUNT(*)
            FROM students
            WHERE name LIKE ?
            OR roll LIKE ?
            """,
            params
        ).fetchone()[0]

    else:

        total_students = connection.execute(
            """
            SELECT COUNT(*)
            FROM students
            """
        ).fetchone()[0]

    # -----------------------------------------------------
    # PAGINATION
    # -----------------------------------------------------

    query += """
        LIMIT ? OFFSET ?
    """

    students = connection.execute(
        query,
        params + (
            per_page,
            offset
        )
    ).fetchall()

    connection.close()

    # -----------------------------------------------------
    # CALCULATE TOTAL PAGES
    # -----------------------------------------------------

    total_pages = (
        total_students + per_page - 1
    ) // per_page

    # -----------------------------------------------------
    # HANDLE INVALID PAGE
    # -----------------------------------------------------

    if total_pages > 0 and page > total_pages:

        return redirect(
            url_for(
                "students",
                page=total_pages,
                search=search,
                sort=sort
            )
        )

    return render_template(
        "students.html",
        students=students,
        search=search,
        sort=sort,
        page=page,
        total_pages=total_pages,
        total_students=total_students
    )


# =========================================================
# STUDENT DETAILS
# =========================================================

@app.route("/student/<int:student_id>")
def student_details(student_id):

    connection = get_db_connection()

    student = connection.execute(
        """
        SELECT *
        FROM students
        WHERE id = ?
        """,
        (student_id,)
    ).fetchone()

    connection.close()

    if student is None:
        return page_not_found(None)

    return render_template(
        "student_details.html",
        student=student
    )


# =========================================================
# EDIT STUDENT
# =========================================================

@app.route(
    "/student/<int:student_id>/edit",
    methods=["GET", "POST"]
)
def edit_student(student_id):

    connection = get_db_connection()

    student = connection.execute(
        """
        SELECT *
        FROM students
        WHERE id = ?
        """,
        (student_id,)
    ).fetchone()

    if student is None:

        connection.close()

        return page_not_found(None)

    # -----------------------------------------------------
    # UPDATE STUDENT
    # -----------------------------------------------------

    if request.method == "POST":
        values, errors = validate_student_form(request.form)
        if errors:
            connection.close()
            return render_template(
                "edit_student.html",
                student=student,
                form_values=request.form.to_dict(),
                errors=errors
            ), 400

        name = values["name"]
        roll = values["roll"]
        email = values["email"]
        age = values["age"]
        attendance = values["attendance"]
        study_hours = values["study_hours"]
        assignment = values["assignment"]
        previous_marks = values["previous_marks"]
        python = values["python"]
        dsa = values["dsa"]
        dbms = values["dbms"]
        web = values["web"]
        marks = {
            "Python": python,
            "DSA": dsa,
            "DBMS": dbms,
            "Web Development": web
        }

        # -------------------------------------------------
        # CALCULATIONS
        # -------------------------------------------------

        total, average, percentage, grade, result = calculate_performance(marks)

        # -------------------------------------------------
        # UPDATE DATABASE
        # -------------------------------------------------

        connection.execute(
            """
            UPDATE students

            SET
                name = ?,
                roll = ?,
                email = ?,
                age = ?,

                attendance = ?,
                study_hours = ?,
                assignment = ?,
                previous_marks = ?,

                python = ?,
                dsa = ?,
                dbms = ?,
                web = ?,

                total = ?,
                average = ?,
                percentage = ?,
                grade = ?,
                result = ?

            WHERE id = ?
            """,
            (
                name,
                roll,
                email,
                age,

                attendance,
                study_hours,
                assignment,
                previous_marks,

                python,
                dsa,
                dbms,
                web,

                total,
                average,
                percentage,
                grade,
                result,

                student_id
            )
        )

        connection.commit()
        connection.close()

        return redirect(
            url_for(
                "student_details",
                student_id=student_id
            )
        )

    connection.close()

    return render_template(
        "edit_student.html",
        student=student,
        form_values={},
        errors=[]
    )


# =========================================================
# DELETE STUDENT
# =========================================================

@app.route(
    "/student/<int:student_id>/delete",
    methods=["POST"]
)
def delete_student(student_id):

    connection = get_db_connection()

    student = connection.execute(
        """
        SELECT *
        FROM students
        WHERE id = ?
        """,
        (student_id,)
    ).fetchone()

    if student is None:

        connection.close()

        return page_not_found(None)

    connection.execute(
        """
        DELETE FROM students
        WHERE id = ?
        """,
        (student_id,)
    )

    connection.commit()
    connection.close()

    return redirect(
        url_for("students")
    )


# =========================================================
# ADD STUDENT
# =========================================================

@app.route(
    "/add-student",
    methods=["GET", "POST"]
)
def add_student():

    if request.method == "POST":
        values, errors = validate_student_form(request.form)
        if errors:
            return render_template(
                "add_student.html",
                form_values=request.form.to_dict(),
                errors=errors
            ), 400

        name = values["name"]
        roll = values["roll"]
        email = values["email"]
        age = values["age"]
        attendance = values["attendance"]
        study_hours = values["study_hours"]
        assignment = values["assignment"]
        previous_marks = values["previous_marks"]
        python = values["python"]
        dsa = values["dsa"]
        dbms = values["dbms"]
        web = values["web"]
        marks = {
            "Python": python,
            "DSA": dsa,
            "DBMS": dbms,
            "Web Development": web
        }

        # -------------------------------------------------
        # CALCULATIONS
        # -------------------------------------------------

        total, average, percentage, grade, result = calculate_performance(marks)

        # -------------------------------------------------
        # HIGHEST / LOWEST SUBJECT
        # -------------------------------------------------

        highest_subject = max(
            marks,
            key=marks.get
        )

        lowest_subject = min(
            marks,
            key=marks.get
        )

        # -------------------------------------------------
        # INSERT INTO DATABASE
        # -------------------------------------------------

        connection = get_db_connection()

        cursor = connection.execute(
            """
            INSERT INTO students (

                name,
                roll,
                email,
                age,

                attendance,
                study_hours,
                assignment,
                previous_marks,

                python,
                dsa,
                dbms,
                web,

                total,
                average,
                percentage,
                grade,
                result
            )

            VALUES (
                ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?,
                ?, ?, ?, ?, ?
            )
            """,
            (
                name,
                roll,
                email,
                age,

                attendance,
                study_hours,
                assignment,
                previous_marks,

                python,
                dsa,
                dbms,
                web,

                total,
                average,
                percentage,
                grade,
                result
            )
        )

        student_id = cursor.lastrowid

        connection.commit()
        connection.close()

        return render_template(
            "result.html",
            name=name,
            marks=marks,
            total=total,
            average=average,
            percentage=percentage,
            grade=grade,
            result=result,
            highest_subject=highest_subject,
            lowest_subject=lowest_subject,
            student_id=student_id
        )

    return render_template(
        "add_student.html",
        form_values={},
        errors=[]
    )


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    create_database()

    app.run(
        debug=False
    )
