import pandas as pd
from recommendation_system.load import *
from sklearn.cluster import KMeans

def apply_clustering(movies, n_clusters=10):
    """
    Applies KMeans clustering to movies based on their genres.

    Param:
    - movies (DataFrame): DataFrame containing movie information, including genres.
    - n_clusters (int): The number of clusters to form. Default is 10.
    
    Returns:
    - movies (DataFrame): The updated DataFrame with cluster labels assigned to each movie.
    - kmeans (KMeans): The trained KMeans model.
    """
    genres_dummies = movies['Genres'].str.get_dummies(sep='|')
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    movies['Cluster'] = kmeans.fit_predict(genres_dummies)
    
    return movies, kmeans

def get_favorite_genre(user_id, ratings, movies):
    """
    Determines the favorite genre of a user based on their highly-rated movies.

    Param:
    - user_id (int): The ID of the user.
    - ratings (DataFrame): DataFrame containing user ratings for movies.
    - movies (DataFrame): DataFrame containing movie information, including genres.
    
    Returns:
    - favorite_genre (str): The genre that the user rates the highest on average.
    """
    user_ratings = ratings[ratings['UserID'] == user_id]
    merged_data = pd.merge(user_ratings, movies, on='MovieID')
    high_rated = merged_data[merged_data['Rating'] >= 3.0]  
    favorite_genre = high_rated['Genres'].str.split('|').explode().mode()[0] 
    return favorite_genre

def recommend_by_genre_and_cluster(user_id, ratings, movies, kmeans):
    """
    Recommends movies to a user based on their favorite genre and movie cluster.

    Param:
    - user_id (int): The ID of the user.
    - ratings (DataFrame): DataFrame containing user ratings for movies.
    - movies (DataFrame): DataFrame containing movie information, including genres.
    - kmeans (KMeans): The KMeans model used for clustering the movies.
    
    Returns:
    - genre_recommendations (DataFrame): DataFrame containing recommended movies with columns
      ['Title', 'Genres', 'MovieID'] that match the user's favorite genre and are in the same cluster.
    """
    favorite_genre = get_favorite_genre(user_id, ratings, movies)
    watched_movie_ids = ratings[ratings['UserID'] == user_id]['MovieID']
    
    genres_dummies = movies['Genres'].str.get_dummies(sep='|')
    genre_vector = genres_dummies.loc[movies['Genres'].str.contains(favorite_genre)].mean().values.reshape(1, -1)
    cluster_label = kmeans.predict(genre_vector)[0]
    
    cluster_movies = movies[(movies['Cluster'] == cluster_label) & (~movies['MovieID'].isin(watched_movie_ids))]
    genre_recommendations = cluster_movies[cluster_movies['Genres'].str.contains(favorite_genre)]
    
    return genre_recommendations[['Title', 'Genres', 'MovieID']]

movies_clustered, kmeans_model = apply_clustering(movies)

def Get_movies_by_knowledge(user_id):
    """
    Gets movie recommendations for a user based on their favorite genre and the genre's cluster.

    Param:
    - user_id (int): The ID of the user.
    
    Returns:
    - recommendations (DataFrame): DataFrame containing recommended movies for the user.
    """
    return recommend_by_genre_and_cluster(user_id, ratings, movies_clustered, kmeans_model)
