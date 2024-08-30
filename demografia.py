import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from load import *

movies['Genres'] = movies['Genres'].str.split('|')
movies = movies.explode('Genres')
movies = pd.get_dummies(movies, columns=['Genres'], prefix='', prefix_sep='')

movies = movies.drop_duplicates(subset=['MovieID'])

movie_genres = movies.set_index('MovieID').drop(columns=['Title'])

ratings_users = pd.merge(ratings, users, on='UserID')

user_profiles = pd.get_dummies(users, columns=['Gender', 'Age', 'Occupation'])

n_clusters = 5
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
user_profiles['Cluster'] = kmeans.fit_predict(user_profiles.drop(columns=['UserID', 'Zip-code']))

def recommend_movies(user_id, ratings_users, user_profiles, movie_genres, movies):
    """
    Recommends movies to a user based on demographic clustering.

    Param:
    - user_id (int): The ID of the user to recommend movies to.
    - ratings_users (DataFrame): DataFrame containing merged user ratings and user demographic data.
    - user_profiles (DataFrame): DataFrame containing user demographic profiles with clustering information.
    - movie_genres (DataFrame): DataFrame with movies and their one-hot encoded genres.
    - movies (DataFrame): DataFrame containing movie details, including titles and genres.

    Returns:
    - DataFrame: A DataFrame containing recommended movies with columns for MovieID, Title, and Score.
    """
    user_cluster = user_profiles.loc[user_profiles['UserID'] == user_id, 'Cluster'].values[0]
    cluster_users = user_profiles[user_profiles['Cluster'] == user_cluster]['UserID']
    cluster_ratings = ratings_users[ratings_users['UserID'].isin(cluster_users)]
    
    movie_scores = cluster_ratings.groupby('MovieID')['Rating'].mean()
    watched_movies = ratings_users[ratings_users['UserID'] == user_id]['MovieID']
    movie_scores = movie_scores[~movie_scores.index.isin(watched_movies)]
    
    recommended_movies = movie_scores.sort_values(ascending=False)
    recommended_movies_df = movies[movies['MovieID'].isin(recommended_movies.index)]
    
    recommended_movies_df = recommended_movies_df.set_index('MovieID')
    recommended_movies_df['Score'] = recommended_movies
    
    return recommended_movies_df[['Title', 'Score']].reset_index()

def Get_movies_by_demography(user_id):
    """
    Retrieves movie recommendations for a user based on their demographic profile.

    Param:
    - user_id (int): The ID of the user to recommend movies to.

    Returns:
    - dict: A dictionary where the keys are MovieIDs and the values are the recommendation scores.
    """
    recommendations_df = recommend_movies(user_id, ratings_users, user_profiles, movie_genres, movies)
    recommendations_dict = pd.Series(recommendations_df['Score'].values, index=recommendations_df['MovieID']).to_dict()
    
    return recommendations_dict
