import pandas as pd
from load import *  # Importa los DataFrames de ratings, movies, y users
from sklearn.cluster import KMeans

# Paso 1: Aplicar clustering a las películas basado en géneros
def apply_clustering(movies, n_clusters=10):
    # Crear un vector de características simple basado en los géneros
    genres_dummies = movies['Genres'].str.get_dummies(sep='|')
    
    # Aplicar KMeans clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    movies['Cluster'] = kmeans.fit_predict(genres_dummies)
    
    return movies, kmeans

# Paso 2: Identificar el género favorito del usuario basado en sus calificaciones
def get_favorite_genre(user_id, ratings, movies):
    user_ratings = ratings[ratings['UserID'] == user_id]
    merged_data = pd.merge(user_ratings, movies, on='MovieID')
    high_rated = merged_data[merged_data['Rating'] >= 3.0]  # Filtrar las calificaciones altas
    favorite_genre = high_rated['Genres'].str.split('|').explode().mode()[0]  # Encontrar el género más frecuente
    return favorite_genre

# Paso 3: Recomendar películas basadas en el género favorito y el clúster correspondiente
def recommend_by_genre_and_cluster(user_id, ratings, movies, kmeans):
    favorite_genre = get_favorite_genre(user_id, ratings, movies)
    watched_movie_ids = ratings[ratings['UserID'] == user_id]['MovieID']
    
    # Identificar el clúster más relevante para el género favorito
    genres_dummies = movies['Genres'].str.get_dummies(sep='|')
    genre_vector = genres_dummies.loc[movies['Genres'].str.contains(favorite_genre)].mean().values.reshape(1, -1)
    cluster_label = kmeans.predict(genre_vector)[0]
    
    # Filtrar las películas que el usuario no ha visto y que están en el clúster identificado
    cluster_movies = movies[(movies['Cluster'] == cluster_label) & (~movies['MovieID'].isin(watched_movie_ids))]
    genre_recommendations = cluster_movies[cluster_movies['Genres'].str.contains(favorite_genre)]
    
    return genre_recommendations[['Title', 'Genres', 'MovieID']]

# Aplicar el clustering a las películas
movies_clustered, kmeans_model = apply_clustering(movies)

# Probar el sistema de recomendación
user_id = 1
recommended_movies = recommend_by_genre_and_cluster(user_id, ratings, movies_clustered, kmeans_model)

# print(f"Recomendaciones para el usuario {user_id} basadas en el género favorito y clúster correspondiente:")
# print(recommended_movies)

def Get_movies_by_knowledge(user_id):
    return recommend_by_genre_and_cluster(user_id, ratings, movies_clustered, kmeans_model)
