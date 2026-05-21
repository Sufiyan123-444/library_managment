import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

from database import add_student, get_all_students, delete_student


class StudentManagementWindow(tk.Toplevel):
    """Window for adding, viewing and deleting students."""

    def __init__(self, master):
        super().__init__(master)
        self.title("Student Management")
        self.geometry("780x470")

        ttk.Label(self, text="Student Management", font=("Segoe UI", 14, "bold")).pack(pady=(10, 2))

        form = tk.Frame(self, padx=10, pady=10)
        form.pack(fill="x")

        tk.Label(form, text="Student ID").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(form, text="Name").grid(row=0, column=2, padx=5, pady=5)
        tk.Label(form, text="Department").grid(row=1, column=0, padx=5, pady=5)

        self.student_id_entry = tk.Entry(form)
        self.name_entry = tk.Entry(form)
        self.department_entry = tk.Entry(form)

        self.student_id_entry.grid(row=0, column=1, padx=5, pady=5)
        self.name_entry.grid(row=0, column=3, padx=5, pady=5)
        self.department_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(form, text="Add Student", command=self.add_student_action).grid(row=2, column=0, pady=8)
        ttk.Button(form, text="Delete Selected", command=self.delete_selected_student).grid(row=2, column=1, pady=8)
        ttk.Button(form, text="Refresh", command=self.load_students).grid(row=2, column=2, pady=8)

        columns = ("student_id", "name", "department")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("student_id", text="Student ID")
        self.tree.heading("name", text="Name")
        self.tree.heading("department", text="Department")

        self.tree.column("student_id", width=130)
        self.tree.column("name", width=260)
        self.tree.column("department", width=220)

        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.load_students()

    def clear_entries(self):
        self.student_id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.department_entry.delete(0, tk.END)

    def load_students(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in get_all_students():
            self.tree.insert("", tk.END, values=row)

    def add_student_action(self):
        student_id = self.student_id_entry.get().strip()
        name = self.name_entry.get().strip()
        department = self.department_entry.get().strip()

        if not student_id or not name or not department:
            messagebox.showerror("Error", "Please fill all fields")
            return

        try:
            add_student(student_id, name, department)
            messagebox.showinfo("Success", "Student added")
            self.clear_entries()
            self.load_students()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Student ID already exists")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def delete_selected_student(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a student first")
            return

        values = self.tree.item(selected[0], "values")
        student_id = values[0]

        deleted = delete_student(student_id)
        if deleted:
            messagebox.showinfo("Success", "Student deleted")
            self.load_students()
        else:
            messagebox.showerror("Error", "Student not found")
