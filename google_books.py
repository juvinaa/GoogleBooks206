import random
import requests
import sqlite3
import matplotlib.pyplot as plt

# Set your API key here
API_KEY = 'AIzaSyDp75ZQEtUDinfAW--tDW_pUBt4f6dyxas'
DATABASE_NAME = 'book_database.db'

# Predefined list of random genres
GENRES = [
    "fiction", "mystery", "fantasy", "romance", 
    "science fiction", "history", "biography", 
    "thriller", "adventure", "horror", "young adult",
    "philosophy", "classics", "humor", "poetry"
]

# Function to fetch data from Google Books API
def fetch_books(query, max_results=25, start_index=0):
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults={max_results}&startIndex={start_index}&key={API_KEY}"
    response = requests.get(url)
    return response.json()

# Function to store data in SQLite database
def store_data_in_db(data):
    conn = sqlite3.connect(DATABASE_NAME)  # Use DATABASE_NAME here
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
        book_unique_id = item['id']  # Using book_unique_id instead of book_id
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

# Function to calculate average ratings
def calculate_average_ratings():
    conn = sqlite3.connect(DATABASE_NAME)  # Use DATABASE_NAME here
    cursor = conn.cursor()

    cursor.execute('''
        SELECT AVG(average_rating) FROM books WHERE average_rating IS NOT NULL;
    ''')
    
    average_rating = cursor.fetchone()[0]
    print(f'Average Rating of Books: {average_rating}')

    conn.close()

# Function to visualize data
def visualize_data():
    conn = sqlite3.connect(DATABASE_NAME)  # Use DATABASE_NAME here
    cursor = conn.cursor()

    cursor.execute('SELECT title, average_rating FROM books WHERE average_rating IS NOT NULL;')
    results = cursor.fetchall()

    titles = [result[0] for result in results]
    ratings = [result[1] for result in results]

    plt.barh(titles, ratings)
    plt.xlabel('Average Rating')
    plt.title('Average Ratings of Books')
    plt.show()

# Function to calculate average ratings by genre
def average_rating_by_genre():
    conn = sqlite3.connect(DATABASE_NAME)  # Use DATABASE_NAME here
    cursor = conn.cursor()

    cursor.execute('''
        SELECT categories.name, AVG(books.average_rating) 
        FROM categories
        JOIN book_categories ON categories.id = book_categories.category_id
        JOIN books ON books.book_unique_id = book_categories.book_unique_id
        WHERE books.average_rating IS NOT NULL
        GROUP BY categories.name;
    ''')

    results = cursor.fetchall()

    genres = [result[0] for result in results]
    avg_ratings = [result[1] for result in results]

    # Visualize average rating by genre
    plt.barh(genres, avg_ratings)
    plt.xlabel('Average Rating')
    plt.title('Average Rating by Genre')
    plt.show()

    conn.close()

# Main function to run the project
def main():
    query = random.choice(GENRES)  # Select a random genre
    print(f"Fetching books for genre: {query}")
    
    total_books_stored = 0
    start_index = 0

    # Only fetch 25 books
    data = fetch_books(query, max_results=25, start_index=start_index)
    if 'items' in data:
        store_data_in_db(data)
        total_books_stored += len(data['items'])

    print(f"Total books stored: {total_books_stored}")
    calculate_average_ratings()
    visualize_data()

    # New calculations
    average_rating_by_genre()  # Show average rating by genre

if __name__ == "__main__":
    main()
