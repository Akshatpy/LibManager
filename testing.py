import csv
import random
import requests
BOOKS_API_URL = "http://openlibrary.org/search.json?limit=10&q="
def fetch_books(query="fiction"):
    response = requests.get(BOOKS_API_URL + query)
    if response.status_code == 200:
        data = response.json()
        books = []
        for i, book in enumerate(data.get("docs", []), start=1):
            book_id = f"B{i:03}"
            title = book.get("title", "Unknown Title")
            author = ", ".join(book.get("author_name", ["Unknown Author"]))
            copies = random.randint(1, 10)
            books.append([book_id, title, author, copies])
        return books
    else:
        print(f"Error fetching books: {response.status_code}")
        return []
books = fetch_books("fiction")
with open("books.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(books)
student_names = [
    "Mayank Agarwal", "Lakshay Jain", "Kanishka Sharma", "Akshat Sharma",
    "Akshay Kumar", "Varun Danda", "Akshit Singhal", "Amogh Patil",
    "Priya Deshpande", "Virat Kohli", "Anushka Singh"
]
students = []
for i in range(1, 11):
    student_id = f"S{i:03}"
    name = random.choice(student_names)
    borrowed_books = random.sample([book[0] for book in books], random.randint(0, 3))
    students.append([student_id, name, ",".join(borrowed_books)])
with open("students.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerows(students)