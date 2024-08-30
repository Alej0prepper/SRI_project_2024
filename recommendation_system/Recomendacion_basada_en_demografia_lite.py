import pandas as pd
from recommendation_system.load import *

def recommend_by_demographics(user_id, users, ratings, movies):
    """
    Recommends movies to a user based on demographic information, including age, gender, and occupation.

    Param:
    - user_id (int): The ID of the user to recommend movies to.
    - users (DataFrame): DataFrame containing user demographic data.
    - ratings (DataFrame): DataFrame containing user ratings for movies.
    - movies (DataFrame): DataFrame containing movie details, including titles and genres.

    Returns:
    - DataFrame: A DataFrame containing recommended movies with columns for Title and Genres.
    """
    user_info = users[users['UserID'] == user_id].iloc[0]
    
    if user_info['Age'] == 1:  # Under 18
        preferred_genres = ['Animation', 'Adventure', 'Family']
    elif user_info['Age'] == 18:  # 18-24
        preferred_genres = ['Action', 'Comedy', 'Sci-Fi']
    elif user_info['Age'] == 25:  # 25-34
        preferred_genres = ['Drama', 'Comedy', 'Action']
    elif user_info['Age'] == 35:  # 35-44
        preferred_genres = ['Drama', 'Romance', 'Thriller']
    elif user_info['Age'] in [45, 50, 56]:  # 45-49, 50-55, 56+
        preferred_genres = ['Drama', 'Documentary', 'Mystery']
    
    if user_info['Gender'] == 'M':
        if 'Drama' not in preferred_genres:
            preferred_genres += ['Action', 'Sci-Fi']
    elif user_info['Gender'] == 'F':
        if 'Action' not in preferred_genres:
            preferred_genres += ['Romance', 'Comedy']

    if user_info['Occupation'] in [1, 15, 4]:  # academic/educator, scientist, student
        preferred_genres += ['Documentary']
    elif user_info['Occupation'] in [2, 20]:  # artist, writer
        preferred_genres += ['Drama', 'Romance']
    
    watched_movie_ids = ratings[ratings['UserID'] == user_id]['MovieID']
    recommendations = movies[~movies['MovieID'].isin(watched_movie_ids)]
    genre_recommendations = recommendations[recommendations['Genres'].str.contains('|'.join(preferred_genres))]
    
    return genre_recommendations[['Title', 'Genres']].drop_duplicates()

# user_id = 1
# recommended_movies = recommend_by_demographics(user_id, users, ratings, movies)
