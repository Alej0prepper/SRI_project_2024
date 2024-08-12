# Filtrado colaborativo basado en items
from load import *
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# Crear la matriz de calificaciones (usuarios x películas)
rating_matrix = ratings.pivot_table(index='UserID', columns='MovieID', values='Rating').fillna(0)

# Mostrar la matriz de calificaciones
print(rating_matrix.head())
# Calcular la similitud entre ítems (películas)
item_similarity = cosine_similarity(rating_matrix.T)

# Convertir la matriz de similitud en un DataFrame para facilitar su uso
item_similarity_df = pd.DataFrame(item_similarity, index=rating_matrix.columns, columns=rating_matrix.columns)

# Mostrar la matriz de similitud
print(item_similarity_df.head())


def predict_ratings(ratings, similarity, dynamic_weight=True):
    # # Inicializar una matriz para las predicciones
    # pred = np.zeros(ratings.shape)
    # # Para cada usuario, predecir la calificación para cada película
    # for i in range(ratings.shape[0]):
    #     print(ratings.shape[0])
    #     # Promedio ponderado por similitud
    #     pred[i, :] = similarity.dot(ratings.iloc[i, :]) / np.abs(similarity).sum(axis=1)

     # Calcular la media de las calificaciones por usuario
     # Calcular la media de las calificaciones por usuario
    user_mean = ratings.mean(axis=1)
    
    # Restar la media de cada usuario para centrar las calificaciones
    ratings_demeaned = ratings.sub(user_mean, axis=0)
    
    pred = user_mean[:, np.newaxis] + (similarity.dot(ratings_demeaned.T).T / np.abs(similarity).sum(axis=1))
    
    return pred

# Calcular las calificaciones predichas
predicted_ratings = predict_ratings(rating_matrix, item_similarity_df)

# Convertir la matriz predicha en un DataFrame para facilitar su uso
predicted_ratings_df = pd.DataFrame(predicted_ratings, index=rating_matrix.index, columns=rating_matrix.columns)

# Mostrar las primeras filas de las calificaciones predichas
print(predicted_ratings_df.head())

# Definir un ID de usuario para hacer recomendaciones
user_id = 1

# Obtener las calificaciones predichas para este usuario
user_ratings = predicted_ratings_df.loc[user_id]

# Ordenar las películas según la calificación predicha
sorted_ratings = user_ratings.sort_values(ascending=False)

# Mostrar las principales recomendaciones
print(f"Recomendaciones para el usuario {user_id}:")
print(sorted_ratings.head(10))  # Las 10 mejores recomendaciones