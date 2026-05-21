import os
import sqlite3


# Keep DB location configurable for Render disk mounts.
def get_db_path():
    default_path = os.path.join(os.path.dirname(__file__), "library.db")
    return os.getenv("DB_PATH", default_path)


def get_connection():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS books (
            book_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            quantity INTEGER NOT NULL CHECK (quantity >= 0)
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS issued_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            book_id TEXT NOT NULL,
            issue_date TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(student_id) ON DELETE RESTRICT,
            FOREIGN KEY(book_id) REFERENCES books(book_id) ON DELETE RESTRICT
        )
        """
    )

    conn.commit()
    conn.close()


# ------------------------ Book queries ------------------------
def add_book(book_id, title, author, quantity):
    conn = get_connection()
    conn.execute(
        "INSERT INTO books (book_id, title, author, quantity) VALUES (?, ?, ?, ?)",
        (book_id, title, author, quantity),
    )
    conn.commit()
    conn.close()


def get_books(search_text=""):
    conn = get_connection()
    if search_text:
        like = f"%{search_text}%"
        rows = conn.execute(
            """
            SELECT book_id, title, author, quantity
            FROM books
            WHERE book_id LIKE ? OR title LIKE ? OR author LIKE ?
            ORDER BY title
            """,
            (like, like, like),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT book_id, title, author, quantity FROM books ORDER BY title"
        ).fetchall()
    conn.close()
    return rows


def get_available_books():
    conn = get_connection()
    rows = conn.execute(
        "SELECT book_id, title, author, quantity FROM books WHERE quantity > 0 ORDER BY title"
    ).fetchall()
    conn.close()
    return rows


def delete_book(book_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    return deleted


# ------------------------ Student queries ------------------------
def add_student(student_id, name, department):
    conn = get_connection()
    conn.execute(
        "INSERT INTO students (student_id, name, department) VALUES (?, ?, ?)",
        (student_id, name, department),
    )
    conn.commit()
    conn.close()


def get_students():
    conn = get_connection()
    rows = conn.execute(
        "SELECT student_id, name, department FROM students ORDER BY name"
    ).fetchall()
    conn.close()
    return rows


def delete_student(student_id):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
    conn.commit()
    deleted = cur.rowcount
    conn.close()
    return deleted


# ------------------------ Issue / Return queries ------------------------
def issue_book(student_id, book_id, issue_date):
    conn = get_connection()
    cur = conn.cursor()

    row = cur.execute("SELECT quantity FROM books WHERE book_id = ?", (book_id,)).fetchone()
    if row is None:
        conn.close()
        raise ValueError("Book not found")

    if row["quantity"] <= 0:
        conn.close()
        raise ValueError("Book is out of stock")

    cur.execute(
        "INSERT INTO issued_books (student_id, book_id, issue_date) VALUES (?, ?, ?)",
        (student_id, book_id, issue_date),
    )
    cur.execute("UPDATE books SET quantity = quantity - 1 WHERE book_id = ?", (book_id,))
    conn.commit()
    conn.close()


def get_issued_books():
    conn = get_connection()
    rows = conn.execute(
        """
        SELECT i.id, i.issue_date, i.student_id, s.name AS student_name,
               i.book_id, b.title AS book_title
        FROM issued_books i
        JOIN students s ON s.student_id = i.student_id
        JOIN books b ON b.book_id = i.book_id
        ORDER BY i.id DESC
        """
    ).fetchall()
    conn.close()
    return rows


def return_book(issue_id):
    conn = get_connection()
    cur = conn.cursor()

    row = cur.execute("SELECT book_id FROM issued_books WHERE id = ?", (issue_id,)).fetchone()
    if row is None:
        conn.close()
        raise ValueError("Issued record not found")

    book_id = row["book_id"]
    cur.execute("UPDATE books SET quantity = quantity + 1 WHERE book_id = ?", (book_id,))
    cur.execute("DELETE FROM issued_books WHERE id = ?", (issue_id,))

    conn.commit()
    conn.close()
