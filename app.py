from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/add-student")
def add_student():
    return render_template("add_student.html")


if __name__ == "__main__":
    app.run(debug=True)