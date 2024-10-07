import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from recommendation_system.load import *

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
    # Get the cluster for the current user
    user_cluster = user_profiles.loc[user_profiles['UserID'] == user_id, 'Cluster'].values[0]
    # Get all users in the same cluster
    cluster_users = user_profiles[user_profiles['Cluster'] == user_cluster]['UserID']
    # Filter ratings for users in the same cluster
    cluster_ratings = ratings_users[ratings_users['UserID'].isin(cluster_users)]
    
    # Calculate average movie scores within the cluster
    movie_scores = cluster_ratings.groupby('MovieID')['Rating'].mean()
    
    # Get movies the user has already rated
    watched_movies = ratings_users[ratings_users['UserID'] == user_id]['MovieID'].unique()
    # Exclude already watched movies from recommendations
    movie_scores = movie_scores[~movie_scores.index.isin(watched_movies)]
    
    # Sort and prepare the recommendations DataFrame
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
    # Load datasets
    movies = load_movies()
    ratings = load_ratings()
    users = load_users()

    # Process genres
    movies['Genres'] = movies['Genres'].str.split('|')
    movies = movies.explode('Genres')
    movies = pd.get_dummies(movies, columns=['Genres'], prefix='', prefix_sep='')

    movies = movies.drop_duplicates(subset=['MovieID'])

    # Prepare genre and user demographic profiles
    movie_genres = movies.set_index('MovieID').drop(columns=['Title'])
    ratings_users = pd.merge(ratings, users, on='UserID')
    user_profiles = pd.get_dummies(users, columns=['Gender', 'Age', 'Occupation'])

    # Cluster users based on demographic profiles
    n_clusters = 5
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    user_profiles['Cluster'] = kmeans.fit_predict(user_profiles.drop(columns=['UserID', 'Zip-code']))

    # Generate recommendations
    recommendations_df = recommend_movies(user_id, ratings_users, user_profiles, movie_genres, movies)
    recommendations_dict = pd.Series(recommendations_df['Score'].values, index=recommendations_df['MovieID']).to_dict()
    
    return recommendations_dict
