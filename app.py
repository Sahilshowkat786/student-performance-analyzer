from flask import Flask, render_template, request, redirect, url_for
import sqlite3


app = Flask(__name__)

DATABASE = "students.db"


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


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

    connection.close()

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
        attendance_performance_data=attendance_performance_data,
        study_hours_performance_data=study_hours_performance_data,
        assignment_performance_data=assignment_performance_data,
        previous_marks_performance_data=previous_marks_performance_data
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
        return "Student not found", 404

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

        return "Student not found", 404

    # -----------------------------------------------------
    # UPDATE STUDENT
    # -----------------------------------------------------

    if request.method == "POST":

        name = request.form["name"]
        roll = request.form["roll"]
        email = request.form["email"]

        age = int(
            request.form["age"]
        )

        attendance = float(
            request.form["attendance"]
        )

        study_hours = float(
            request.form["study_hours"]
        )

        assignment = float(
            request.form["assignment"]
        )

        previous_marks = float(
            request.form["previous_marks"]
        )

        python = float(
            request.form["python"]
        )

        dsa = float(
            request.form["dsa"]
        )

        dbms = float(
            request.form["dbms"]
        )

        web = float(
            request.form["web"]
        )

        # -------------------------------------------------
        # MARKS
        # -------------------------------------------------

        marks = {
            "Python": python,
            "DSA": dsa,
            "DBMS": dbms,
            "Web Development": web
        }

        # -------------------------------------------------
        # CALCULATIONS
        # -------------------------------------------------

        total = sum(
            marks.values()
        )

        average = total / len(marks)

        percentage = (
            total / 400
        ) * 100

        # -------------------------------------------------
        # GRADE
        # -------------------------------------------------

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

        # -------------------------------------------------
        # RESULT
        # -------------------------------------------------

        result = (
            "Pass"
            if percentage >= 40
            else "Fail"
        )

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
        student=student
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

        return "Student not found", 404

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

        name = request.form["name"]

        roll = request.form["roll"]

        email = request.form["email"]

        age = int(
            request.form["age"]
        )

        attendance = float(
            request.form["attendance"]
        )

        study_hours = float(
            request.form["study_hours"]
        )

        assignment = float(
            request.form["assignment"]
        )

        previous_marks = float(
            request.form["previous_marks"]
        )

        python = float(
            request.form["python"]
        )

        dsa = float(
            request.form["dsa"]
        )

        dbms = float(
            request.form["dbms"]
        )

        web = float(
            request.form["web"]
        )

        # -------------------------------------------------
        # MARKS
        # -------------------------------------------------

        marks = {
            "Python": python,
            "DSA": dsa,
            "DBMS": dbms,
            "Web Development": web
        }

        # -------------------------------------------------
        # CALCULATIONS
        # -------------------------------------------------

        total = sum(
            marks.values()
        )

        average = total / len(marks)

        percentage = (
            total / 400
        ) * 100

        # -------------------------------------------------
        # GRADE
        # -------------------------------------------------

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

        # -------------------------------------------------
        # RESULT
        # -------------------------------------------------

        result = (
            "Pass"
            if percentage >= 40
            else "Fail"
        )

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
        "add_student.html"
    )


# =========================================================
# START APPLICATION
# =========================================================

if __name__ == "__main__":

    create_database()

    app.run(
        debug=True
    )
