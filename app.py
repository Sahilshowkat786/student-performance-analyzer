from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

DATABASE = "students.db"


# Connect to database
def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# Create database and table
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


# Home page
@app.route("/")
def home():

    connection = get_db_connection()

    students = connection.execute(
        "SELECT * FROM students ORDER BY id DESC"
    ).fetchall()

    connection.close()

    return render_template("index.html", students=students)


# Students page
@app.route("/students")
def students():

    # Get search text from URL
    search = request.args.get("search", "").strip()

    # Get sorting option from URL
    sort = request.args.get("sort", "latest")

    connection = get_db_connection()

    # Search
    if search:

        query = """
            SELECT * FROM students
            WHERE name LIKE ? OR roll LIKE ?
        """

        params = (
            f"%{search}%",
            f"%{search}%"
        )

    else:

        query = "SELECT * FROM students"

        params = ()

    # Sorting
    if sort == "highest":

        query += " ORDER BY percentage DESC"

    elif sort == "lowest":

        query += " ORDER BY percentage ASC"

    elif sort == "name_asc":

        query += " ORDER BY name ASC"

    elif sort == "name_desc":

        query += " ORDER BY name DESC"

    else:

        query += " ORDER BY id DESC"

    students = connection.execute(
        query,
        params
    ).fetchall()

    connection.close()

    return render_template(
        "students.html",
        students=students,
        search=search,
        sort=sort
    )


# Student details
@app.route("/student/<int:student_id>")
def student_details(student_id):

    connection = get_db_connection()

    student = connection.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()

    connection.close()

    if student is None:
        return "Student not found", 404

    return render_template(
        "student_details.html",
        student=student
    )


# Edit student
@app.route("/student/<int:student_id>/edit", methods=["GET", "POST"])
def edit_student(student_id):

    connection = get_db_connection()

    student = connection.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()

    if student is None:
        connection.close()
        return "Student not found", 404

    if request.method == "POST":

        name = request.form["name"]
        roll = request.form["roll"]
        email = request.form["email"]
        age = int(request.form["age"])

        attendance = float(request.form["attendance"])
        study_hours = float(request.form["study_hours"])
        assignment = float(request.form["assignment"])
        previous_marks = float(request.form["previous_marks"])

        python = float(request.form["python"])
        dsa = float(request.form["dsa"])
        dbms = float(request.form["dbms"])
        web = float(request.form["web"])

        # Subject marks
        marks = {
            "Python": python,
            "DSA": dsa,
            "DBMS": dbms,
            "Web Development": web
        }

        # Calculate total
        total = sum(marks.values())

        # Calculate average
        average = total / len(marks)

        # Calculate percentage
        percentage = (total / 400) * 100

        # Calculate grade
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

        # Pass / Fail
        result = "Pass" if percentage >= 40 else "Fail"

        # Update student
        connection.execute("""
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
        """, (
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
        ))

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


# Delete student
@app.route("/student/<int:student_id>/delete", methods=["POST"])
def delete_student(student_id):

    connection = get_db_connection()

    student = connection.execute(
        "SELECT * FROM students WHERE id = ?",
        (student_id,)
    ).fetchone()

    if student is None:
        connection.close()
        return "Student not found", 404

    connection.execute(
        "DELETE FROM students WHERE id = ?",
        (student_id,)
    )

    connection.commit()
    connection.close()

    return redirect(url_for("students"))


# Add student
@app.route("/add-student", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        name = request.form["name"]
        roll = request.form["roll"]
        email = request.form["email"]
        age = int(request.form["age"])

        attendance = float(request.form["attendance"])
        study_hours = float(request.form["study_hours"])
        assignment = float(request.form["assignment"])
        previous_marks = float(request.form["previous_marks"])

        python = float(request.form["python"])
        dsa = float(request.form["dsa"])
        dbms = float(request.form["dbms"])
        web = float(request.form["web"])

        # Subject marks
        marks = {
            "Python": python,
            "DSA": dsa,
            "DBMS": dbms,
            "Web Development": web
        }

        # Calculate total
        total = sum(marks.values())

        # Calculate average
        average = total / len(marks)

        # Calculate percentage
        percentage = (total / 400) * 100

        # Calculate grade
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

        # Pass / Fail
        result = "Pass" if percentage >= 40 else "Fail"

        # Highest and lowest subject
        highest_subject = max(marks, key=marks.get)
        lowest_subject = min(marks, key=marks.get)

        # Save student to database
        connection = get_db_connection()

        cursor = connection.execute("""
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

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
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
        ))

        student_id = cursor.lastrowid

        connection.commit()
        connection.close()

        # Show result
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

    return render_template("add_student.html")


# Start application
if __name__ == "__main__":

    create_database()

    app.run(debug=True)