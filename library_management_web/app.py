from datetime import date
import os
import sqlite3
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for

from db import (
    add_book,
    add_student,
    delete_book,
    delete_student,
    get_available_books,
    get_books,
    get_issued_books,
    get_students,
    init_db,
    issue_book,
    return_book,
)

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "change-this-in-render")

# Create tables before first request.
init_db()


# Simple decorator to protect pages after login.
def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapper


@app.route("/")
def home():
    if session.get("is_admin"):
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == "admin" and password == "admin123":
            session["is_admin"] = True
            flash("Login successful", "success")
            return redirect(url_for("dashboard"))

        flash("Invalid username or password", "danger")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out", "info")
    return redirect(url_for("login"))


@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")


@app.route("/books", methods=["GET", "POST"])
@login_required
def books():
    if request.method == "POST":
        book_id = request.form.get("book_id", "").strip()
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        quantity_text = request.form.get("quantity", "").strip()

        if not book_id or not title or not author or not quantity_text:
            flash("Please fill all book fields", "danger")
            return redirect(url_for("books"))

        try:
            quantity = int(quantity_text)
            if quantity < 0:
                flash("Quantity cannot be negative", "danger")
                return redirect(url_for("books"))

            add_book(book_id, title, author, quantity)
            flash("Book added", "success")
        except ValueError:
            flash("Quantity must be a number", "danger")
        except sqlite3.IntegrityError:
            flash("Book ID already exists", "danger")
        except Exception as exc:
            flash(str(exc), "danger")

        return redirect(url_for("books"))

    search = request.args.get("search", "").strip()
    rows = get_books(search)
    return render_template("books.html", books=rows, search=search)


@app.post("/books/delete/<book_id>")
@login_required
def delete_book_route(book_id):
    try:
        deleted = delete_book(book_id)
        if deleted:
            flash("Book deleted", "success")
        else:
            flash("Book not found", "warning")
    except sqlite3.IntegrityError:
        flash("Cannot delete this book. It is currently issued.", "danger")
    return redirect(url_for("books"))


@app.route("/students", methods=["GET", "POST"])
@login_required
def students():
    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip()
        name = request.form.get("name", "").strip()
        department = request.form.get("department", "").strip()

        if not student_id or not name or not department:
            flash("Please fill all student fields", "danger")
            return redirect(url_for("students"))

        try:
            add_student(student_id, name, department)
            flash("Student added", "success")
        except sqlite3.IntegrityError:
            flash("Student ID already exists", "danger")
        except Exception as exc:
            flash(str(exc), "danger")

        return redirect(url_for("students"))

    rows = get_students()
    return render_template("students.html", students=rows)


@app.post("/students/delete/<student_id>")
@login_required
def delete_student_route(student_id):
    try:
        deleted = delete_student(student_id)
        if deleted:
            flash("Student deleted", "success")
        else:
            flash("Student not found", "warning")
    except sqlite3.IntegrityError:
        flash("Cannot delete this student. The student has issued books.", "danger")
    return redirect(url_for("students"))


@app.route("/issue", methods=["GET", "POST"])
@login_required
def issue():
    if request.method == "POST":
        student_id = request.form.get("student_id", "").strip()
        book_id = request.form.get("book_id", "").strip()
        issue_date = request.form.get("issue_date", "").strip()

        if not student_id or not book_id or not issue_date:
            flash("Please fill all issue fields", "danger")
            return redirect(url_for("issue"))

        try:
            issue_book(student_id, book_id, issue_date)
            flash("Book issued successfully", "success")
        except Exception as exc:
            flash(str(exc), "danger")

        return redirect(url_for("issue"))

    return render_template(
        "issue.html",
        students=get_students(),
        books=get_available_books(),
        default_date=str(date.today()),
    )


@app.route("/return")
@login_required
def return_page():
    rows = get_issued_books()
    return render_template("return.html", issued=rows)


@app.post("/return/<int:issue_id>")
@login_required
def return_book_route(issue_id):
    try:
        return_book(issue_id)
        flash("Book returned successfully", "success")
    except Exception as exc:
        flash(str(exc), "danger")
    return redirect(url_for("return_page"))


if __name__ == "__main__":
    # Local run only. Render uses gunicorn from requirements.
    app.run(host="0.0.0.0", port=5000, debug=True)
