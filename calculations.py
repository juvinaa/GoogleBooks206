import csv
import sqlite3
from database import get_data_from_db

# Function to calculate average ratings
def calculate_average_ratings():
    query = '''
        SELECT AVG(average_rating) FROM books WHERE average_rating IS NOT NULL;
    '''
    average_rating = get_data_from_db(query)[0][0]
    return average_rating

# Function to calculate average ratings by genre
def average_rating_by_genre():
    query = '''
        SELECT categories.name, AVG(books.average_rating) 
        FROM categories
        JOIN book_categories ON categories.id = book_categories.category_id
        JOIN books ON books.book_unique_id = book_categories.book_unique_id
        WHERE books.average_rating IS NOT NULL
        GROUP BY categories.name;
    '''
    results = get_data_from_db(query)
    genres = [result[0] for result in results]
    avg_ratings = [result[1] for result in results]
    return genres, avg_ratings

# Function to write calculations to a CSV file
def write_to_csv(genres, avg_ratings, average_rating):
    with open('book_calculations.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Average Rating of All Books", average_rating])
        writer.writerow(["Genre", "Average Rating"])
        for genre, avg_rating in zip(genres, avg_ratings):
            writer.writerow([genre, avg_rating])

# Main function for calculations
def main_calculations():
    average_rating = calculate_average_ratings()
    genres, avg_ratings = average_rating_by_genre()
    write_to_csv(genres, avg_ratings, average_rating)

if __name__ == "__main__":
    main_calculations()
