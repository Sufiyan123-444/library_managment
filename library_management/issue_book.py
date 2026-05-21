import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from database import get_all_students, get_available_books, issue_book, get_issued_books


class IssueBookWindow(tk.Toplevel):
    """Window to issue a book to a student."""

    def __init__(self, master):
        super().__init__(master)
        self.title("Issue Book")
        self.geometry("920x560")

        ttk.Label(self, text="Issue Book", font=("Segoe UI", 14, "bold")).pack(pady=(10, 2))

        top = tk.Frame(self, padx=10, pady=10)
        top.pack(fill="x")

        tk.Label(top, text="Student").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        tk.Label(top, text="Book").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        tk.Label(top, text="Issue Date (YYYY-MM-DD)").grid(row=2, column=0, padx=5, pady=5, sticky="w")

        self.student_combobox = ttk.Combobox(top, state="readonly", width=45)
        self.book_combobox = ttk.Combobox(top, state="readonly", width=45)
        self.issue_date_entry = ttk.Entry(top, width=20)

        self.student_combobox.grid(row=0, column=1, padx=5, pady=5)
        self.book_combobox.grid(row=1, column=1, padx=5, pady=5)
        self.issue_date_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        # Fill today's date by default for convenience.
        self.issue_date_entry.insert(0, str(date.today()))

        ttk.Button(top, text="Issue Book", command=self.issue_book_action).grid(row=3, column=0, pady=10)
        ttk.Button(top, text="Refresh Lists", command=self.load_combobox_data).grid(row=3, column=1, pady=10, sticky="w")

        columns = ("id", "student_id", "student_name", "book_id", "book_title", "issue_date")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("id", text="Issue ID")
        self.tree.heading("student_id", text="Student ID")
        self.tree.heading("student_name", text="Student Name")
        self.tree.heading("book_id", text="Book ID")
        self.tree.heading("book_title", text="Book Title")
        self.tree.heading("issue_date", text="Issue Date")

        self.tree.column("id", width=70)
        self.tree.column("student_id", width=110)
        self.tree.column("student_name", width=160)
        self.tree.column("book_id", width=90)
        self.tree.column("book_title", width=220)
        self.tree.column("issue_date", width=120)

        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.student_map = {}
        self.book_map = {}

        self.load_combobox_data()
        self.load_issued_books()

    def load_combobox_data(self):
        self.student_map.clear()
        self.book_map.clear()

        student_labels = []
        for sid, name, _dept in get_all_students():
            label = f"{sid} - {name}"
            student_labels.append(label)
            self.student_map[label] = sid

        book_labels = []
        for bid, title, _author, qty in get_available_books():
            label = f"{bid} - {title} (Qty: {qty})"
            book_labels.append(label)
            self.book_map[label] = bid

        self.student_combobox["values"] = student_labels
        self.book_combobox["values"] = book_labels

        if student_labels:
            self.student_combobox.current(0)
        else:
            self.student_combobox.set("")

        if book_labels:
            self.book_combobox.current(0)
        else:
            self.book_combobox.set("")

    def load_issued_books(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in get_issued_books():
            self.tree.insert("", tk.END, values=row)

    def issue_book_action(self):
        student_label = self.student_combobox.get().strip()
        book_label = self.book_combobox.get().strip()
        issue_date = self.issue_date_entry.get().strip()

        if not student_label or not book_label or not issue_date:
            messagebox.showerror("Error", "Please fill/select all fields")
            return

        student_id = self.student_map.get(student_label)
        book_id = self.book_map.get(book_label)

        if not student_id or not book_id:
            messagebox.showerror("Error", "Invalid student or book selection")
            return

        try:
            issue_book(student_id, book_id, issue_date)
            messagebox.showinfo("Success", "Book issued successfully")
            self.load_combobox_data()
            self.load_issued_books()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
