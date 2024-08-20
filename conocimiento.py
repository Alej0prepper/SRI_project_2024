#Recomendacion basada en conocimiento
import pandas as pd
from load import *

# Paso 1: Identificar el género favorito del usuario basado en sus calificaciones
def get_favorite_genre(user_id, ratings, movies):
    user_ratings = ratings[ratings['UserID'] == user_id]
    merged_data = pd.merge(user_ratings, movies, on='MovieID')
    high_rated = merged_data[merged_data['Rating'] >= 4.0]  # Filtrar las calificaciones altas
    favorite_genre = high_rated['Genres'].str.split('|').explode().mode()[0]  # Encontrar el género más frecuente
    return favorite_genre

# Paso 2: Recomendar películas basadas en el género favorito
def recommend_by_genre(user_id, ratings, movies):
    favorite_genre = get_favorite_genre(user_id,ratings,movies)
    watched_movie_ids = ratings[ratings['UserID'] == user_id]['MovieID']
    recommendations = movies[~movies['MovieID'].isin(watched_movie_ids)]  # Excluir películas ya vistas
    genre_recommendations = recommendations[recommendations['Genres'].str.contains(favorite_genre)]
    return genre_recommendations[['Title', 'Genres','MovieID']]

# Probar el sistema de recomendación
user_id = 10
# favorite_genre = get_favorite_genre(user_id, ratings, movies)
# recommended_movies = recommend_by_genre(user_id, ratings, movies)

# print(f"Recomendaciones para el usuario {user_id} basadas en el género favorito '{favorite_genre}':")
# print(recommended_movies)

def Get_movies_by_knowledge(user_id):
    return recommend_by_genre(user_id,ratings, movies)