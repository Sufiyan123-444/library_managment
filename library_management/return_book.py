import tkinter as tk
from tkinter import ttk, messagebox

from database import get_issued_books, return_issued_book


class ReturnBookWindow(tk.Toplevel):
    """Window to return issued books."""

    def __init__(self, master):
        super().__init__(master)
        self.title("Return Book")
        self.geometry("920x520")

        ttk.Label(self, text="Return Book", font=("Segoe UI", 14, "bold")).pack(pady=(10, 2))

        top = tk.Frame(self, padx=10, pady=10)
        top.pack(fill="x")

        ttk.Button(top, text="Return Selected", command=self.return_selected).pack(side="left")
        ttk.Button(top, text="Refresh", command=self.load_issued_books).pack(side="left", padx=8)

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

        self.load_issued_books()

    def load_issued_books(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in get_issued_books():
            self.tree.insert("", tk.END, values=row)

    def return_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select an issued record first")
            return

        values = self.tree.item(selected[0], "values")
        issue_id = values[0]

        try:
            return_issued_book(issue_id)
            messagebox.showinfo("Success", "Book returned successfully")
            self.load_issued_books()
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
