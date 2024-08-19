import pandas as pd
from load import *
# Cargar los datos de usuarios
# users = pd.read_csv('ruta/al/archivo/users.dat', sep='::', names=['UserID', 'Gender', 'Age', 'Occupation', 'Zip-code'], engine='python')

# Cargar los datos de ratings y movies
# ratings = pd.read_csv('ruta/al/archivo/ratings.dat', sep='::', names=['UserID', 'MovieID', 'Rating', 'Timestamp'], engine='python')
# movies = pd.read_csv('ruta/al/archivo/movies.dat', sep='::', names=['MovieID', 'Title', 'Genres'], engine='python')

def recommend_by_demographics(user_id, users, ratings, movies):
    # Obtener información demográfica del usuario
    user_info = users[users['UserID'] == user_id].iloc[0]
    
    # Definir géneros preferidos según la edad
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
    
    # Ajustar géneros según el género del usuario
    if user_info['Gender'] == 'M':
        # Solo añadir géneros si no contradicen los géneros ya establecidos por la edad
        if 'Drama' not in preferred_genres:
            preferred_genres += ['Action', 'Sci-Fi']
    elif user_info['Gender'] == 'F':
        # Solo añadir géneros si no contradicen los géneros ya establecidos por la edad
        if 'Action' not in preferred_genres:
            preferred_genres += ['Romance', 'Comedy']

    # Ajustar géneros según la ocupación del usuario
    if user_info['Occupation'] in [1, 15, 4]:  # académico/educador, científico, estudiante
        preferred_genres += ['Documentary']
    elif user_info['Occupation'] in [2, 20]:  # artista, escritor
        preferred_genres += ['Drama', 'Romance']
    
    # Filtrar películas no vistas y que coincidan con los géneros preferidos
    watched_movie_ids = ratings[ratings['UserID'] == user_id]['MovieID']
    recommendations = movies[~movies['MovieID'].isin(watched_movie_ids)]
    genre_recommendations = recommendations[recommendations['Genres'].str.contains('|'.join(preferred_genres))]
    
    # Devolver las películas recomendadas con sus géneros
    return genre_recommendations[['Title', 'Genres']].drop_duplicates()

# Probar el sistema de recomendación basado en demografía
user_id = 1  # Reemplazar con un ID de usuario válido
recommended_movies = recommend_by_demographics(user_id, users, ratings, movies)

print(f"Recomendaciones para el usuario {user_id} basadas en demografía:")
print(recommended_movies)
