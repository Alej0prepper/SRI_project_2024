#Recomendacion basada en contenido
import pandas as pd 
from load import *
from sklearn.metrics.pairwise import cosine_similarity

# Convertir los géneros en un formato binario para cada película
movies['Genres'] = movies['Genres'].str.split('|').apply(lambda x: ', '.join(x))
movies = movies.explode('Genres')
movies = pd.get_dummies(movies, columns=['Genres'], prefix='', prefix_sep='')

movies = movies.drop_duplicates(subset=['MovieID'])
# Crear la matriz de géneros (MovieID como índice y géneros como columnas)
movie_genres = movies.drop_duplicates(subset=['MovieID']).set_index('MovieID')
movie_genres = movie_genres.drop(columns=['Title'])  # Eliminar la columna 'Title' para evitar el error

# Unir las tablas ratings y movies en función de MovieID
user_movie_ratings = pd.merge(ratings, movies, on='MovieID')

# Eliminar las columnas no necesarias
user_movie_ratings = user_movie_ratings.drop(columns=['Title', 'Timestamp'])

# Crear el perfil de usuario basado en géneros
user_profiles = user_movie_ratings.groupby('UserID').mean().drop(columns=['MovieID', 'Rating'])

def recommend_movies(user_id, user_profiles, movie_genres, ratings, movies, n_recommendations=10):
    # Seleccionar el perfil del usuario
    user_profile = user_profiles.loc[user_id].values.reshape(1, -1)
    
    # Calcular la similitud coseno entre el perfil del usuario y cada película
    cosine_sim = cosine_similarity(user_profile, movie_genres.values)
    
    # Crear un DataFrame de las similitudes
    similarity_df = pd.DataFrame(cosine_sim.T, index=movie_genres.index, columns=['Similarity'])
    
    # Filtrar las películas que el usuario ya ha calificado
    watched_movies = ratings[ratings['UserID'] == user_id]['MovieID']
    similarity_df = similarity_df.drop(index=watched_movies, errors='ignore')
    
    # Obtener las películas más similares (las más recomendadas)
    recommended_movies = similarity_df.sort_values(by='Similarity', ascending=False).head(n_recommendations)
    
    # Unir las recomendaciones con los títulos de las películas y géneros
    recommended_movies = pd.merge(recommended_movies, movies[['MovieID', 'Title']], left_index=True, right_on='MovieID')
    print("herre")
    print(recommended_movies)
    # Identificar los géneros que influyeron en la recomendación
    def get_influential_genres(row):
        influential_genres = movie_genres.loc[row['MovieID']] > 0  # Identificar géneros presentes en la película
        matched_genres = influential_genres[influential_genres].index.tolist()  # Obtener los géneros que coinciden
        return ', '.join(matched_genres)  # Unir los géneros en una cadena
    
    recommended_movies['Reason'] = recommended_movies.apply(get_influential_genres, axis=1)
    
    return recommended_movies[['Title', 'Similarity', 'Reason']]

# Probar el sistema de recomendación para un usuario específico
user_id = 1
recommended_movies = recommend_movies(user_id, user_profiles, movie_genres, ratings, movies)

# Mostrar las recomendaciones con las razones
print(f"Recomendaciones para el usuario {user_id}:")
print(recommended_movies)