import matplotlib.pyplot as plt

# Function to visualize data
def visualize_data():
    import database
    query = '''
        SELECT title, average_rating FROM books WHERE average_rating IS NOT NULL;
    '''
    results = database.get_data_from_db(query)
    titles = [result[0] for result in results]
    ratings = [result[1] for result in results]

    plt.barh(titles, ratings)
    plt.xlabel('Average Rating')
    plt.title('Average Ratings of Books')
    plt.show()

# Function to visualize average rating by genre
def average_rating_by_genre_graph():
    import database
    query = '''
        SELECT categories.name, AVG(books.average_rating) 
        FROM categories
        JOIN book_categories ON categories.id = book_categories.category_id
        JOIN books ON books.book_unique_id = book_categories.book_unique_id
        WHERE books.average_rating IS NOT NULL
        GROUP BY categories.name;
    '''
    results = database.get_data_from_db(query)
    genres = [result[0] for result in results]
    avg_ratings = [result[1] for result in results]

    plt.barh(genres, avg_ratings)
    plt.xlabel('Average Rating')
    plt.title('Average Rating by Genre')
    plt.show()

# Main function for graphs
def main_graphs():
    visualize_data()
    average_rating_by_genre_graph()

if __name__ == "__main__":
    main_graphs()
