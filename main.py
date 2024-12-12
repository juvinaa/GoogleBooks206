import random
from database import fetch_books, store_data_in_db
from calculations import main_calculations
from graphs import main_graphs

# Predefined list of random genres
GENRES = [
    "fiction", "mystery", "fantasy", "romance", 
    "science fiction", "history", "biography", 
    "thriller", "adventure", "horror", "young adult",
    "philosophy", "classics", "humor", "poetry"
]

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
    main_calculations()
    main_graphs()

if __name__ == "__main__":
    main()
