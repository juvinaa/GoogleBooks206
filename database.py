import sqlite3
import json
import requests

# Set your API key here
API_KEY = 'AIzaSyDp75ZQEtUDinfAW--tDW_pUBt4f6dyxas'
DATABASE_NAME = 'book_database.db'

# Function to fetch data from Google Books API
def fetch_books(query, max_results=25, start_index=0):
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults={max_results}&startIndex={start_index}&key={API_KEY}"
    response = requests.get(url)
    return response.json()

# Function to store data in SQLite database
def store_data_in_db(data):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Create books, authors, categories, and junction tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS books (
            book_unique_id TEXT PRIMARY KEY,
            title TEXT,
            published_date TEXT,
            average_rating REAL
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS authors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS book_authors (
            book_unique_id TEXT,
            author_id INTEGER,
            FOREIGN KEY (book_unique_id) REFERENCES books(book_unique_id),
            FOREIGN KEY (author_id) REFERENCES authors(id),
            PRIMARY KEY (book_unique_id, author_id)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS book_categories (
            book_unique_id TEXT,
            category_id INTEGER,
            FOREIGN KEY (book_unique_id) REFERENCES books(book_unique_id),
            FOREIGN KEY (category_id) REFERENCES categories(id),
            PRIMARY KEY (book_unique_id, category_id)
        )
    ''')

    # Loop through the fetched books and insert data into the database
    for item in data.get('items', []):
        volume_info = item['volumeInfo']
        book_unique_id = item['id']
        title = volume_info.get('title', '')
        published_date = volume_info.get('publishedDate', '')
        average_rating = volume_info.get('averageRating', None)

        # Insert data into the books table
        cursor.execute('''
            INSERT OR IGNORE INTO books (book_unique_id, title, published_date, average_rating)
            VALUES (?, ?, ?, ?)
        ''', (book_unique_id, title, published_date, average_rating))

        # Insert authors into the authors table and create relationships in book_authors table
        authors = volume_info.get('authors', [])
        for author in authors:
            cursor.execute('''
                INSERT OR IGNORE INTO authors (name) VALUES (?)
            ''', (author,))
            cursor.execute('''
                INSERT OR IGNORE INTO book_authors (book_unique_id, author_id)
                SELECT ?, id FROM authors WHERE name = ?
            ''', (book_unique_id, author))

        # Insert categories into the categories table and create relationships in book_categories table
        categories = volume_info.get('categories', [])
        for category in categories:
            cursor.execute('''
                INSERT OR IGNORE INTO categories (name) VALUES (?)
            ''', (category,))
            cursor.execute('''
                INSERT OR IGNORE INTO book_categories (book_unique_id, category_id)
                SELECT ?, id FROM categories WHERE name = ?
            ''', (book_unique_id, category))

    conn.commit()
    conn.close()

# Function to retrieve data from the database
def get_data_from_db(query):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()
    return results
