import tkinter as tk
from tkinter import messagebox, ttk

from database import init_db
from login import LoginPage
from books import BookManagementWindow
from students import StudentManagementWindow
from issue_book import IssueBookWindow
from return_book import ReturnBookWindow


def setup_styles(root):
    """Configure simple reusable ttk styles for a cleaner UI."""
    style = ttk.Style(root)
    style.theme_use("clam")

    style.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground="#1f2937")
    style.configure("Card.TFrame", background="#f8fafc")
    style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=8)
    style.configure("Danger.TButton", font=("Segoe UI", 10, "bold"), padding=8)


class LibraryDashboard:
    """Main dashboard shown after successful login."""

    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.root.geometry("500x430")
        self.root.resizable(False, False)
        self.root.configure(bg="#eef2f7")

        self.main_frame = tk.Frame(self.root, padx=20, pady=20, bg="#eef2f7")
        self.main_frame.pack(fill="both", expand=True)

        ttk.Label(self.main_frame, text="Library Management System", style="Title.TLabel").pack(
            pady=(10, 6)
        )
        ttk.Label(
            self.main_frame,
            text="Simple UI for books, students, issue and return",
            font=("Segoe UI", 10),
        ).pack(pady=(0, 15))

        card = ttk.Frame(self.main_frame, style="Card.TFrame", padding=18)
        card.pack(fill="x", padx=12)

        ttk.Button(
            card,
            text="Book Management",
            width=25,
            command=self.open_books,
            style="Primary.TButton",
        ).pack(pady=6)

        ttk.Button(
            card,
            text="Student Management",
            width=25,
            command=self.open_students,
            style="Primary.TButton",
        ).pack(pady=6)

        ttk.Button(
            card,
            text="Issue Book",
            width=25,
            command=self.open_issue_book,
            style="Primary.TButton",
        ).pack(pady=6)

        ttk.Button(
            card,
            text="Return Book",
            width=25,
            command=self.open_return_book,
            style="Primary.TButton",
        ).pack(pady=6)

        ttk.Button(
            card,
            text="Exit",
            width=25,
            command=self.confirm_exit,
            style="Danger.TButton",
        ).pack(pady=10)

    def open_books(self):
        BookManagementWindow(self.root)

    def open_students(self):
        StudentManagementWindow(self.root)

    def open_issue_book(self):
        IssueBookWindow(self.root)

    def open_return_book(self):
        ReturnBookWindow(self.root)

    def confirm_exit(self):
        if messagebox.askyesno("Exit", "Do you want to close the application?"):
            self.root.destroy()


class App:
    """Application startup class handling login then dashboard."""

    def __init__(self, root):
        self.root = root
        init_db()
        self.show_login()

    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear_root()
        LoginPage(self.root, self.show_dashboard)

    def show_dashboard(self):
        self.clear_root()
        LibraryDashboard(self.root)


if __name__ == "__main__":
    root = tk.Tk()
    setup_styles(root)
    App(root)
    root.mainloop()
