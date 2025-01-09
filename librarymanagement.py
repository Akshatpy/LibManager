from PIL import Image, ImageTk
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import csv
from datetime import datetime, timedelta
BOOKS_FILE = "books.csv"
STUDENTS_FILE = "students.csv"
LOGS_FILE = "logs.csv"
class Book:
    def __init__(self, book_id, title, author, copies):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.copies = int(copies)
    def to_csv(self):
        return [self.book_id, self.title, self.author, self.copies]
class Student:
    def __init__(self, student_id, name, borrowed_books=None):
        self.student_id = student_id
        self.name = name
        self.borrowed_books = borrowed_books or []
    def add_book(self, book_id):
        self.borrowed_books.append(book_id)
    def remove_book(self, book_id):
        self.borrowed_books.remove(book_id)
    def to_csv(self):
        return [self.student_id, self.name, ",".join(self.borrowed_books)]
class Librarian:
    def __init__(self):
        self.books = []
        self.students = []
        self.load_data()
    def load_data(self):
        try:
            with open(BOOKS_FILE, "r") as f:
                reader = csv.reader(f)
                self.books = [Book(*row) for row in reader]
        except FileNotFoundError:
            print("Books.csv is missing!!")
            pass
        try:
            with open(STUDENTS_FILE, "r") as f:
                reader = csv.reader(f)
                self.students = [Student(row[0], row[1], row[2].split(",") if row[2] else []) for row in reader]
        except FileNotFoundError:
            pass
    def save_data(self):
        with open(BOOKS_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(book.to_csv() for book in self.books)
        with open(STUDENTS_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerows(student.to_csv() for student in self.students)
    def check_stock(self):
        return [(book.book_id, book.title, book.author, book.copies) for book in self.books]
    def search_book(self, query):
        return [book for book in self.books if query.lower() in book.title.lower() or query.lower() in book.author.lower()]
    def search_student(self, query):
        return [student for student in self.students if query.lower() in student.name.lower() or query.lower() in student.student_id.lower()]
    def issue_book(self, book_id, student_id):
        book = next((b for b in self.books if b.book_id == book_id), None)
        student = next((s for s in self.students if s.student_id == student_id), None)
        if not book or not student:
            return "Invalid book or student ID"
        if book.copies <= 0:
            return "Book not available"
        if len(student.borrowed_books) >= 5:
            return "Student cannot borrow more books"
        book.copies -= 1
        student.add_book(book_id)
        self.update_logs("Issue", book_id, student_id)
        self.save_data()
        return "Book issued successfully"

    def calculate_penalty(self, return_date, issue_date):
        return_date = datetime.strptime(return_date, "%Y-%m-%d")
        issue_date = datetime.strptime(issue_date, "%Y-%m-%d")
        due_date = issue_date + timedelta(days=14 + self.GRACE_PERIOD)  # Standard 14-day borrow period + grace period
        late_days = max((return_date - due_date).days, 0)
        if late_days > 0:
            late_days -= sum(
                1 for i in range(late_days)
                if (due_date + timedelta(days=i + 1)).weekday() >= 5
            )
        penalty = late_days * self.BASE_PENALTY_RATE
        return min(penalty, self.MAX_PENALTY_CAP)
    def return_book(self, book_id, student_id):
        book = next((b for b in self.books if b.book_id == book_id), None)
        student = next((s for s in self.students if s.student_id == student_id), None)
        if not book or not student:
            return "Invalid book or student ID"
        if book_id not in student.borrowed_books:
            return "Book not borrowed by this student"
        book.copies += 1
        student.remove_book(book_id)
        self.update_logs("Return", book_id, student_id)
        self.save_data()
        return "Book returned successfully"

    def update_logs(self, transaction_type, book_id, student_id):
        with open(LOGS_FILE, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([transaction_type, book_id, student_id, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
class LibraryGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Library Management System")
        self.librarian = Librarian()
        self.create_widgets()
    def create_widgets(self):
        self.root.configure(bg="#f0f8ff")
        label_frame_style = {"bg": "#b0c4de", "fg": "#2f4f4f", "font": ("Arial", 12, "bold")}
        button_style = {"bg": "#4682b4", "fg": "white", "font": ("Arial", 10, "bold")}

        # Style for Entries
        entry_style = {"font": ("Arial", 10), "bg": "#ffffff", "fg": "#000000"}

        # Book Management Frame
        book_frame = tk.LabelFrame(self.root, text="Book Management", **label_frame_style)
        book_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.book_query = tk.Entry(book_frame, width=30, **entry_style)
        self.book_query.grid(row=0, column=0, padx=5, pady=5)

        tk.Button(book_frame, text="Search Books", command=self.search_books, **button_style).grid(row=0, column=1,
                                                                                                   padx=5, pady=5)
        tk.Button(book_frame, text="Check Stock", command=self.check_stock, **button_style).grid(row=0, column=2,
                                                                                                 padx=5, pady=5)

        self.book_list = ttk.Treeview(book_frame, columns=("ID", "Title", "Author", "Copies"), show="headings")
        self.book_list.heading("ID", text="ID")
        self.book_list.heading("Title", text="Title")
        self.book_list.heading("Author", text="Author")
        self.book_list.heading("Copies", text="Copies")
        self.book_list.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

        # Student Management Frame
        student_frame = tk.LabelFrame(self.root, text="Student Management", **label_frame_style)
        student_frame.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.student_query = tk.Entry(student_frame, width=30, **entry_style)
        self.student_query.grid(row=0, column=0, padx=5, pady=5)

        tk.Button(student_frame, text="Search Students", command=self.search_students, **button_style).grid(row=0,
                                                                                                            column=1,
                                                                                                            padx=5,
                                                                                                            pady=5)

        self.student_list = ttk.Treeview(student_frame, columns=("ID", "Name", "Books"), show="headings")
        self.student_list.heading("ID", text="ID")
        self.student_list.heading("Name", text="Name")
        self.student_list.heading("Books", text="Books")
        self.student_list.grid(row=1, column=0, columnspan=2, padx=5, pady=5)

        # Transactions Frame
        transaction_frame = tk.LabelFrame(self.root, text="Transactions", **label_frame_style)
        transaction_frame.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        tk.Label(transaction_frame, text="Book ID", bg="#b0c4de", font=("Arial", 10, "bold")).grid(row=0, column=0,
                                                                                                   padx=5, pady=5)
        self.book_id_entry = tk.Entry(transaction_frame, width=15, **entry_style)
        self.book_id_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(transaction_frame, text="Student ID", bg="#b0c4de", font=("Arial", 10, "bold")).grid(row=1, column=0,
                                                                                                      padx=5, pady=5)
        self.student_id_entry = tk.Entry(transaction_frame, width=15, **entry_style)
        self.student_id_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(transaction_frame, text="Issue Book", command=self.issue_book, **button_style).grid(row=0, column=2,
                                                                                                      padx=5, pady=5)
        tk.Button(transaction_frame, text="Return Book", command=self.return_book, **button_style).grid(row=1, column=2,
                                                                                                        padx=5, pady=5)

        # Add Image on the Right


    # Replace `your_image_path_here.jpg` with the path to your image file.

    def search_books(self):
        query = self.book_query.get()
        results = self.librarian.search_book(query)
        self.book_list.delete(*self.book_list.get_children())
        for book in results:
            self.book_list.insert("", "end", values=(book.book_id, book.title, book.author, book.copies))
    def check_stock(self):
        stock = self.librarian.check_stock()
        self.book_list.delete(*self.book_list.get_children())
        for book_id, title, author, copies in stock:
            self.book_list.insert("", "end", values=(book_id, title, author, copies))
    def search_students(self):
        query = self.student_query.get()
        results = self.librarian.search_student(query)
        self.student_list.delete(*self.student_list.get_children())
        for student in results:
            self.student_list.insert("", "end", values=(student.student_id, student.name, ", ".join(student.borrowed_books)))
    def issue_book(self):
        book_id = self.book_id_entry.get()
        student_id = self.student_id_entry.get()
        message = self.librarian.issue_book(book_id, student_id)
        messagebox.showinfo("Issue Book", message)
    def return_book(self):
        book_id = self.book_id_entry.get()
        student_id = self.student_id_entry.get()
        message = self.librarian.return_book(book_id, student_id)
        messagebox.showinfo("Return Book", message)
if __name__ == "__main__":
    root = tk.Tk()
    app = LibraryGUI(root)
    root.mainloop()
