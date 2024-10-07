import pandas as pd 
from recommendation_system.load import *
from sklearn.metrics.pairwise import cosine_similarity

# Ensure genres are processed correctly
movies['Genres'] = movies['Genres'].str.split('|').apply(lambda x: ', '.join(x))
movies = movies.explode('Genres')
movies = pd.get_dummies(movies, columns=['Genres'], prefix='', prefix_sep='')

movies = movies.drop_duplicates(subset=['MovieID'])
movie_genres = movies.drop_duplicates(subset=['MovieID']).set_index('MovieID')
movie_genres = movie_genres.drop(columns=['Title'])

# Merge user ratings with movie genres and compute user profiles
user_movie_ratings = pd.merge(ratings, movies, on='MovieID')
user_movie_ratings = user_movie_ratings.drop(columns=['Title', 'Timestamp'])

# Create user profiles, filling missing values with 0
user_profiles = user_movie_ratings.groupby('UserID').mean().drop(columns=['MovieID', 'Rating']).fillna(0)
def recommend_movies(user_id, user_profiles, movie_genres, ratings, movies, n_recommendations=200):
    """
    Recommends movies to a user based on the similarity between their profile and the genres of movies.

    Param:
    - user_id (int): The ID of the user to recommend movies to.
    - user_profiles (DataFrame): The profile of each user, representing their average rating across genres.
    - movie_genres (DataFrame): A DataFrame with movies and their one-hot encoded genres.
    - ratings (DataFrame): A DataFrame containing user ratings for movies.
    - movies (DataFrame): A DataFrame containing movie details, including titles and genres.
    - n_recommendations (int): The number of movie recommendations to return. Default is 200.

    Returns:
    - recommended_movies (DataFrame): A DataFrame containing recommended movies with columns for 
      title, similarity score, reason (influential genres), and movie ID.
    """
    # Get the user profile
    user_profile = user_profiles.loc[user_id].values.reshape(1, -1)
    
    # Calculate the cosine similarity between the user profile and the movie genres
    cosine_sim = cosine_similarity(user_profile, movie_genres.values)
    
    # Create a DataFrame of similarity scores
    similarity_df = pd.DataFrame(cosine_sim.T, index=movie_genres.index, columns=['Similarity'])
    
    # Remove movies the user has already rated
    watched_movies = ratings[ratings['UserID'] == user_id]['MovieID'].unique()
    similarity_df = similarity_df.drop(index=watched_movies, errors='ignore')
    
    # Sort movies by similarity
    recommended_movies = similarity_df.sort_values(by='Similarity', ascending=False).head(n_recommendations)
    
    # Merge with movie details
    recommended_movies = pd.merge(recommended_movies, movies[['MovieID', 'Title']], left_index=True, right_on='MovieID')

    # Find the most influential genres for each movie
    def get_influential_genres(row):
        influential_genres = movie_genres.loc[row['MovieID']] > 0
        matched_genres = influential_genres[influential_genres].index.tolist()
        return ', '.join(matched_genres)
    
    # Apply function to find the reason (influential genres)
    recommended_movies['Reason'] = recommended_movies.apply(get_influential_genres, axis=1)
    
    # Split the 'Reason' (which contains genres) and explode into multiple rows, one per genre
    recommended_movies_exploded = recommended_movies.copy()
    recommended_movies_exploded['Reason'] = recommended_movies_exploded['Reason'].str.split(', ')
    recommended_movies_exploded = recommended_movies_exploded.explode('Reason')

    # Sort the exploded DataFrame by similarity
    recommended_movies_exploded = recommended_movies_exploded.sort_values(by='Similarity', ascending=False)

    # Count the number of movies per genre
    genre_counts = recommended_movies_exploded['Reason'].value_counts()

    # Normalize the similarity scores based on the frequency of movies in each genre
    def normalize_similarity(row):
        genre_count = genre_counts[row['Reason']]
        normalized_score = row['Similarity'] / genre_count  # Reduce score by genre frequency
        return normalized_score

    recommended_movies_exploded['NormalizedSimilarity'] = recommended_movies_exploded.apply(normalize_similarity, axis=1)
    
    # Keep only the first occurrence of each movie (highest similarity) while ensuring unique movies
    filtered_recommended_movies = recommended_movies_exploded.loc[
        recommended_movies_exploded.groupby('Reason')['NormalizedSimilarity'].idxmax()
    ]
    
    # Return the normalized similarity score and other details
    return filtered_recommended_movies[['Title', 'NormalizedSimilarity', 'Reason', 'MovieID']].rename(columns={'NormalizedSimilarity': 'Similarity'})

def Get_movies_by_content(user_id):
    """
    Gets movie recommendations for a user based on content-based filtering.

    Param:
    - user_id (int): The ID of the user to recommend movies to.

    Returns:
    - recommendations_dict (dict): A dictionary where the keys are movie IDs and the values are the similarity scores.
    """
    recommendations_df = recommend_movies(user_id, user_profiles, movie_genres, ratings, movies)
    
    recommendations_df = recommendations_df.sort_values(by='Similarity', ascending=False)
    
    recommendations_dict = pd.Series(recommendations_df['Similarity'].values, index=recommendations_df['MovieID']).to_dict()
    
    return recommendations_dict