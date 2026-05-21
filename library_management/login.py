import tkinter as tk
from tkinter import messagebox, ttk


class LoginPage:
    """Simple login page for admin."""

    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success

        self.root.title("Library Management - Login")
        self.root.geometry("420x290")
        self.root.resizable(False, False)
        self.root.configure(bg="#eef2f7")

        outer = tk.Frame(self.root, bg="#eef2f7", padx=16, pady=18)
        outer.pack(fill="both", expand=True)

        self.container = ttk.Frame(outer, padding=18)
        self.container.pack(fill="both", expand=True)

        ttk.Label(self.container, text="Admin Login", font=("Segoe UI", 14, "bold")).pack(
            pady=(0, 12)
        )
        ttk.Label(self.container, text="Username").pack(anchor="w")
        self.username_entry = ttk.Entry(self.container)
        self.username_entry.pack(fill="x", pady=6)

        ttk.Label(self.container, text="Password").pack(anchor="w")
        self.password_entry = ttk.Entry(self.container, show="*")
        self.password_entry.pack(fill="x", pady=6)

        ttk.Button(self.container, text="Login", command=self.check_login).pack(pady=14)

        self.username_entry.focus_set()

    def check_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if username == "admin" and password == "admin123":
            messagebox.showinfo("Success", "Login successful")
            self.on_success()
        else:
            messagebox.showerror("Error", "Invalid username or password")
