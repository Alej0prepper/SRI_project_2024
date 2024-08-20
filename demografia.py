#Recomendacion basada en demografia 2

import pandas as pd
from load import *

#

# Unir las tablas ratings y users
ratings_users = pd.merge(ratings, users, on='UserID')

# Unir con la tabla de movies para tener los géneros
ratings_users_movies = pd.merge(ratings_users, movies, on='MovieID')

# Mostrar las primeras filas para verificar
print(ratings_users_movies.head())

# Explode los géneros para que cada género tenga su propia fila
ratings_users_movies['Genres'] = ratings_users_movies['Genres'].str.split('|')
ratings_users_movies = ratings_users_movies.explode('Genres')

# Calcular la media de las calificaciones para cada género dentro de cada grupo de edad
genre_preference_by_age = ratings_users_movies.groupby(['Age', 'Genres'])['Rating'].mean().reset_index()

# Ordenar por grupo de edad y calificación promedio para encontrar los géneros más preferidos
genre_preference_by_age = genre_preference_by_age.sort_values(['Age', 'Rating'], ascending=[True, False])

# Calcular la media de las calificaciones para cada género dentro de cada grupo de ocupación
genre_preference_by_occupation = ratings_users_movies.groupby(['Occupation', 'Genres'])['Rating'].mean().reset_index()

# Ordenar por grupo de ocupación y calificación promedio para encontrar los géneros más preferidos
genre_preference_by_occupation = genre_preference_by_occupation.sort_values(['Occupation', 'Rating'], ascending=[True, False])

# Mostrar el resultado
print(genre_preference_by_occupation)


# Mostrar el resultado
print(genre_preference_by_age)

def recommend_by_age_and_occupation(user_id, users=users, ratings_users=ratings_users, genre_preference_by_age=genre_preference_by_age, genre_preference_by_occupation=genre_preference_by_occupation):
    # Obtener la información del usuario
    user_info = users[users['UserID'] == user_id].iloc[0]
    user_age = user_info['Age']
    user_occupation = user_info['Occupation']
    
    # Obtener los géneros más preferidos para el grupo de edad del usuario
    top_genres_age = genre_preference_by_age[genre_preference_by_age['Age'] == user_age]['Genres'].head(3).tolist()
    
    # Obtener los géneros más preferidos para el grupo de ocupación del usuario
    top_genres_occupation = genre_preference_by_occupation[genre_preference_by_occupation['Occupation'] == user_occupation]['Genres'].head(3).tolist()
    
    # Combinar los géneros preferidos de ambos grupos (edad y ocupación)
    combined_genres = list(set(top_genres_age + top_genres_occupation))
    
    # Filtrar películas no vistas y que coincidan con los géneros preferidos
    watched_movie_ids = ratings_users_movies[ratings_users_movies['UserID'] == user_id]['MovieID']
    recommendations = movies[~movies['MovieID'].isin(watched_movie_ids)]
    genre_recommendations = recommendations[recommendations['Genres'].str.contains('|'.join(combined_genres))]
    
    # Devolver las películas recomendadas con sus géneros
    return genre_recommendations[['Title', 'Genres','MovieID']].drop_duplicates(), combined_genres

# Probar el sistema de recomendación basado en edad y ocupación
# user_id = 1  # Reemplazar con un ID de usuario válido
# recommended_movies, combined_genres = recommend_by_age_and_occupation(user_id, users, ratings_users_movies, genre_preference_by_age, genre_preference_by_occupation)

# # Imprimir las recomendaciones personalizadas
# print(f"Recomendaciones para el usuario {user_id} basadas en su grupo de edad y ocupación:")
# print(recommended_movies)

# Imprimir los géneros combinados que fueron utilizados para la recomendación
# print(f"\nGéneros considerados en la recomendación: {', '.join(combined_genres)}")

def Get_movies_by_demography(user_id):
    recommended_movies, combined_genres = recommend_by_age_and_occupation(user_id, users, ratings_users_movies, genre_preference_by_age, genre_preference_by_occupation)
    return recommended_movies

print(Get_movies_by_demography(1))