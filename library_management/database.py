import sqlite3

DB_NAME = "library.db"


def get_connection():
    """Create and return a database connection."""
    return sqlite3.connect(DB_NAME)


def init_db():
    """Create required tables if they do not exist."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS books (
            book_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            quantity INTEGER NOT NULL CHECK(quantity >= 0)
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS students (
            student_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS issued_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            book_id TEXT NOT NULL,
            issue_date TEXT NOT NULL,
            FOREIGN KEY(student_id) REFERENCES students(student_id),
            FOREIGN KEY(book_id) REFERENCES books(book_id)
        )
        """
    )

    conn.commit()
    conn.close()


# ------------------------- Book functions -------------------------
def add_book(book_id, title, author, quantity):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO books (book_id, title, author, quantity) VALUES (?, ?, ?, ?)",
        (book_id, title, author, quantity),
    )
    conn.commit()
    conn.close()


def get_all_books():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT book_id, title, author, quantity FROM books ORDER BY title")
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_available_books():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT book_id, title, author, quantity FROM books WHERE quantity > 0 ORDER BY title"
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_book(book_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM books WHERE book_id = ?", (book_id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    return deleted


def search_books(keyword):
    conn = get_connection()
    cursor = conn.cursor()
    like_text = f"%{keyword}%"
    cursor.execute(
        """
        SELECT book_id, title, author, quantity
        FROM books
        WHERE book_id LIKE ? OR title LIKE ? OR author LIKE ?
        ORDER BY title
        """,
        (like_text, like_text, like_text),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


# ------------------------- Student functions -------------------------
def add_student(student_id, name, department):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO students (student_id, name, department) VALUES (?, ?, ?)",
        (student_id, name, department),
    )
    conn.commit()
    conn.close()


def get_all_students():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT student_id, name, department FROM students ORDER BY name")
    rows = cursor.fetchall()
    conn.close()
    return rows


def delete_student(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM students WHERE student_id = ?", (student_id,))
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    return deleted


# ------------------------- Issue / Return functions -------------------------
def issue_book(student_id, book_id, issue_date):
    """Issue a book and reduce quantity by 1."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT quantity FROM books WHERE book_id = ?", (book_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise ValueError("Book not found.")

    quantity = row[0]
    if quantity <= 0:
        conn.close()
        raise ValueError("Book is out of stock.")

    cursor.execute(
        "INSERT INTO issued_books (student_id, book_id, issue_date) VALUES (?, ?, ?)",
        (student_id, book_id, issue_date),
    )
    cursor.execute(
        "UPDATE books SET quantity = quantity - 1 WHERE book_id = ?",
        (book_id,),
    )

    conn.commit()
    conn.close()


def get_issued_books():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT i.id, i.student_id, s.name, i.book_id, b.title, i.issue_date
        FROM issued_books i
        JOIN students s ON i.student_id = s.student_id
        JOIN books b ON i.book_id = b.book_id
        ORDER BY i.id DESC
        """
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def return_issued_book(issue_id):
    """Return a book: increase quantity and remove issue record."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT book_id FROM issued_books WHERE id = ?", (issue_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        raise ValueError("Issued record not found.")

    book_id = row[0]

    cursor.execute("UPDATE books SET quantity = quantity + 1 WHERE book_id = ?", (book_id,))
    cursor.execute("DELETE FROM issued_books WHERE id = ?", (issue_id,))

    conn.commit()
    conn.close()
