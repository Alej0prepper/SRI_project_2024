import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from load import *

# Convertir los géneros en un formato binario para cada película
movies['Genres'] = movies['Genres'].str.split('|')
movies = movies.explode('Genres')
movies = pd.get_dummies(movies, columns=['Genres'], prefix='', prefix_sep='')

movies = movies.drop_duplicates(subset=['MovieID'])

# Crear la matriz de géneros (MovieID como índice y géneros como columnas)
movie_genres = movies.set_index('MovieID').drop(columns=['Title'])

# Unir las tablas ratings y users
ratings_users = pd.merge(ratings, users, on='UserID')

# Crear el perfil de usuario basado en demografía
user_profiles = pd.get_dummies(users, columns=['Gender', 'Age', 'Occupation'])

# Aplicar clustering a los usuarios basados en sus características demográficas
n_clusters = 5  # Puedes ajustar el número de clústeres según sea necesario
kmeans = KMeans(n_clusters=n_clusters, random_state=42)
user_profiles['Cluster'] = kmeans.fit_predict(user_profiles.drop(columns=['UserID', 'Zip-code']))

def recommend_movies(user_id, ratings_users, user_profiles, movie_genres, movies):
    # Identificar el clúster del usuario
    user_cluster = user_profiles.loc[user_profiles['UserID'] == user_id, 'Cluster'].values[0]
    
    # Filtrar las películas calificadas por usuarios en el mismo clúster
    cluster_users = user_profiles[user_profiles['Cluster'] == user_cluster]['UserID']
    cluster_ratings = ratings_users[ratings_users['UserID'].isin(cluster_users)]
    
    # Calcular el promedio de calificaciones por película dentro del clúster
    movie_scores = cluster_ratings.groupby('MovieID')['Rating'].mean()
    
    # Filtrar películas que el usuario ya ha visto
    watched_movies = ratings_users[ratings_users['UserID'] == user_id]['MovieID']
    movie_scores = movie_scores[~movie_scores.index.isin(watched_movies)]
    
    # Ordenar todas las películas por el promedio de calificaciones
    recommended_movies = movie_scores.sort_values(ascending=False)
    recommended_movies_df = movies[movies['MovieID'].isin(recommended_movies.index)]
    
    # Añadir la columna de puntuación
    recommended_movies_df = recommended_movies_df.set_index('MovieID')
    recommended_movies_df['Score'] = recommended_movies
    
    return recommended_movies_df[['Title', 'Score']].reset_index()

# Probar el sistema de recomendación para un usuario específico
user_id = 1
recommended_movies = recommend_movies(user_id, ratings_users, user_profiles, movie_genres, movies)

# Mostrar las recomendaciones
# print(f"Recomendaciones para el usuario {user_id}:")
# print(recommended_movies)

def Get_movies_by_demography(user_id):
    # Call the demographic-based recommendation function
    recommendations_df = recommend_movies(user_id, ratings_users, user_profiles, movie_genres, movies)
    
    # Convert to dictionary {MovieID: Score}
    recommendations_dict = pd.Series(recommendations_df['Score'].values, index=recommendations_df['MovieID']).to_dict()
    
    return recommendations_dict
