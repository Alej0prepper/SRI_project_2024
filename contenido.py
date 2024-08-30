import pandas as pd 
from load import *
from sklearn.metrics.pairwise import cosine_similarity

movies['Genres'] = movies['Genres'].str.split('|').apply(lambda x: ', '.join(x))
movies = movies.explode('Genres')
movies = pd.get_dummies(movies, columns=['Genres'], prefix='', prefix_sep='')

movies = movies.drop_duplicates(subset=['MovieID'])
movie_genres = movies.drop_duplicates(subset=['MovieID']).set_index('MovieID')
movie_genres = movie_genres.drop(columns=['Title'])

user_movie_ratings = pd.merge(ratings, movies, on='MovieID')
user_movie_ratings = user_movie_ratings.drop(columns=['Title', 'Timestamp'])

user_profiles = user_movie_ratings.groupby('UserID').mean().drop(columns=['MovieID', 'Rating'])

def recommend_movies(user_id, user_profiles, movie_genres, ratings, movies, n_recommendations=10):
    """
    Recommends movies to a user based on the similarity between their profile and the genres of movies.

    Param:
    - user_id (int): The ID of the user to recommend movies to.
    - user_profiles (DataFrame): The profile of each user, representing their average rating across genres.
    - movie_genres (DataFrame): A DataFrame with movies and their one-hot encoded genres.
    - ratings (DataFrame): A DataFrame containing user ratings for movies.
    - movies (DataFrame): A DataFrame containing movie details, including titles and genres.
    - n_recommendations (int): The number of movie recommendations to return. Default is 10.

    Returns:
    - recommended_movies (DataFrame): A DataFrame containing recommended movies with columns for 
      title, similarity score, reason (influential genres), and movie ID.
    """
    user_profile = user_profiles.loc[user_id].values.reshape(1, -1)
    cosine_sim = cosine_similarity(user_profile, movie_genres.values)
    
    similarity_df = pd.DataFrame(cosine_sim.T, index=movie_genres.index, columns=['Similarity'])
    
    watched_movies = ratings[ratings['UserID'] == user_id]['MovieID']
    similarity_df = similarity_df.drop(index=watched_movies, errors='ignore')
    
    recommended_movies = similarity_df.sort_values(by='Similarity', ascending=False)
    recommended_movies = pd.merge(recommended_movies, movies[['MovieID', 'Title']], left_index=True, right_on='MovieID')

    def get_influential_genres(row):
        influential_genres = movie_genres.loc[row['MovieID']] > 0  
        matched_genres = influential_genres[influential_genres].index.tolist() 
        return ', '.join(matched_genres)
    
    recommended_movies['Reason'] = recommended_movies.apply(get_influential_genres, axis=1)
    
    return recommended_movies[['Title', 'Similarity', 'Reason', 'MovieID']]

def Get_movies_by_content(user_id):
    """
    Gets movie recommendations for a user based on content-based filtering.

    Param:
    - user_id (int): The ID of the user to recommend movies to.

    Returns:
    - recommendations_dict (dict): A dictionary where the keys are movie IDs and the values are the similarity scores.
    """
    recommendations_df = recommend_movies(user_id, user_profiles, movie_genres, ratings, movies)
    recommendations_dict = pd.Series(recommendations_df['Similarity'].values, index=recommendations_df['MovieID']).to_dict()
    
    return recommendations_dict
