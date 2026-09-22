from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/add-student", methods=["GET", "POST"])
def add_student():

    if request.method == "POST":

        name = request.form["name"]

        python = float(request.form["python"])
        dsa = float(request.form["dsa"])
        dbms = float(request.form["dbms"])
        web = float(request.form["web"])

        marks = {
            "Python": python,
            "DSA": dsa,
            "DBMS": dbms,
            "Web Development": web
        }

        # Calculate total marks
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
            lowest_subject=lowest_subject
        )

    return render_template("add_student.html")


if __name__ == "__main__":
    app.run(debug=True)