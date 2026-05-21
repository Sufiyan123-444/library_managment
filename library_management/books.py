import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

from database import add_book, get_all_books, delete_book, search_books


class BookManagementWindow(tk.Toplevel):
    """Window for adding, viewing, deleting and searching books."""

    def __init__(self, master):
        super().__init__(master)
        self.title("Book Management")
        self.geometry("820x500")

        ttk.Label(self, text="Book Management", font=("Segoe UI", 14, "bold")).pack(pady=(10, 2))

        form = tk.Frame(self, padx=10, pady=10)
        form.pack(fill="x")

        tk.Label(form, text="Book ID").grid(row=0, column=0, padx=5, pady=5)
        tk.Label(form, text="Title").grid(row=0, column=2, padx=5, pady=5)
        tk.Label(form, text="Author").grid(row=1, column=0, padx=5, pady=5)
        tk.Label(form, text="Quantity").grid(row=1, column=2, padx=5, pady=5)

        self.book_id_entry = tk.Entry(form)
        self.title_entry = tk.Entry(form)
        self.author_entry = tk.Entry(form)
        self.quantity_entry = tk.Entry(form)

        self.book_id_entry.grid(row=0, column=1, padx=5, pady=5)
        self.title_entry.grid(row=0, column=3, padx=5, pady=5)
        self.author_entry.grid(row=1, column=1, padx=5, pady=5)
        self.quantity_entry.grid(row=1, column=3, padx=5, pady=5)

        ttk.Button(form, text="Add Book", command=self.add_book_action).grid(row=2, column=0, pady=8)
        ttk.Button(form, text="Delete Selected", command=self.delete_selected_book).grid(row=2, column=1, pady=8)
        ttk.Button(form, text="Refresh", command=self.load_books).grid(row=2, column=2, pady=8)

        search_frame = tk.Frame(self, padx=10)
        search_frame.pack(fill="x")
        tk.Label(search_frame, text="Search").pack(side="left")
        self.search_entry = ttk.Entry(search_frame)
        self.search_entry.pack(side="left", fill="x", expand=True, padx=8)
        ttk.Button(search_frame, text="Search Book", command=self.search_book_action).pack(side="left")

        columns = ("book_id", "title", "author", "quantity")
        self.tree = ttk.Treeview(self, columns=columns, show="headings")
        self.tree.heading("book_id", text="Book ID")
        self.tree.heading("title", text="Title")
        self.tree.heading("author", text="Author")
        self.tree.heading("quantity", text="Quantity")

        self.tree.column("book_id", width=110)
        self.tree.column("title", width=250)
        self.tree.column("author", width=200)
        self.tree.column("quantity", width=80)

        table_frame = ttk.Frame(self)
        table_frame.pack(fill="both", expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.load_books()

    def clear_entries(self):
        self.book_id_entry.delete(0, tk.END)
        self.title_entry.delete(0, tk.END)
        self.author_entry.delete(0, tk.END)
        self.quantity_entry.delete(0, tk.END)

    def load_books(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in get_all_books():
            self.tree.insert("", tk.END, values=row)

    def add_book_action(self):
        book_id = self.book_id_entry.get().strip()
        title = self.title_entry.get().strip()
        author = self.author_entry.get().strip()
        quantity_text = self.quantity_entry.get().strip()

        if not book_id or not title or not author or not quantity_text:
            messagebox.showerror("Error", "Please fill all fields")
            return

        try:
            quantity = int(quantity_text)
            if quantity < 0:
                messagebox.showerror("Error", "Quantity cannot be negative")
                return
        except ValueError:
            messagebox.showerror("Error", "Quantity must be a number")
            return

        try:
            add_book(book_id, title, author, quantity)
            messagebox.showinfo("Success", "Book added")
            self.clear_entries()
            self.load_books()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Book ID already exists")
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    def delete_selected_book(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Warning", "Select a book first")
            return

        values = self.tree.item(selected[0], "values")
        book_id = values[0]

        deleted = delete_book(book_id)
        if deleted:
            messagebox.showinfo("Success", "Book deleted")
            self.load_books()
        else:
            messagebox.showerror("Error", "Book not found")

    def search_book_action(self):
        keyword = self.search_entry.get().strip()

        for item in self.tree.get_children():
            self.tree.delete(item)

        rows = search_books(keyword) if keyword else get_all_books()
        for row in rows:
            self.tree.insert("", tk.END, values=row)
