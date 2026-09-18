
from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "campuscare"


def db():
    return sqlite3.connect("campuscare.db")


def create_table():
    con = db()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        password TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS complaints(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        title TEXT,
        description TEXT,
        status TEXT
    )
    """)

    con.commit()
    con.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        con = db()
        con.execute(
            "INSERT INTO users(name,email,password) VALUES(?,?,?)",
            (name, email, password)
        )
        con.commit()
        con.close()

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        con = db()
        user = con.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        ).fetchone()
        con.close()

        if user:
            session["email"] = email
            return redirect("/student")

        return "Wrong email or password"

    return render_template("login.html")


@app.route("/student")
def student():
    if "email" not in session:
        return redirect("/login")

    con = db()
    complaints = con.execute(
        "SELECT * FROM complaints WHERE email=?",
        (session["email"],)
    ).fetchall()
    con.close()

    return render_template("student.html", complaints=complaints)


@app.route("/complaint", methods=["GET", "POST"])
def complaint():
    if "email" not in session:
        return redirect("/login")

    if request.method == "POST":
        title = request.form["title"]
        description = request.form["description"]

        con = db()
        con.execute(
            """INSERT INTO complaints
            (email,title,description,status)
            VALUES(?,?,?,?)""",
            (session["email"], title, description, "Pending")
        )
        con.commit()
        con.close()

        return redirect("/student")

    return render_template("complaint.html")


# ADMIN LOGIN
@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        if email == "admin@gmail.com" and password == "admin123":
            session["admin"] = True
            return redirect("/admin_d")

        return "Wrong admin login"

    return render_template("admin.html")


# ADMIN DASHBOARD
@app.route("/admin_d")
def admin_dashboard():
    if "admin" not in session:
        return redirect("/admin.")

    con = db()
    complaints = con.execute(
        "SELECT * FROM complaints"
    ).fetchall()
    con.close()

    return render_template(
        "/admin_d.html",
        complaints=complaints
    )


# UPDATE COMPLAINT STATUS
@app.route("/update/<int:id>", methods=["POST"])
def update(id):
    if "admin" not in session:
        return redirect("/admin")

    status = request.form["status"]

    con = db()
    con.execute(
        "UPDATE complaints SET status=? WHERE id=?",
        (status, id)
    )
    con.commit()
    con.close()

    return redirect("/admin_d")


# LOGOUT
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    create_table()

    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )