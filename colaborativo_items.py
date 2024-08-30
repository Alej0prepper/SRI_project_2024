from load import ratings, movies, users  # Importa los DataFrames de ratings, movies y users
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans

class CollaborativeFilteringWithClustering:
    def __init__(self, ratings, movies, n_clusters=5):
        # Guardar los DataFrames y el número de clústeres
        self.ratings = ratings
        self.movies = movies
        self.n_clusters = n_clusters

        # Crear la matriz de calificaciones (usuarios x películas)
        self.rating_matrix = self.ratings.pivot_table(index='UserID', columns='MovieID', values='Rating')

        # Aplicar clustering a los ítems (películas)
        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42)
        self.item_clusters = self.kmeans.fit_predict(self.rating_matrix.T.fillna(0))  # Usamos 0 solo para clustering, no en el análisis
        
        # Añadir la información de clúster a la matriz de calificaciones
        self.rating_matrix_clustered = pd.DataFrame(self.rating_matrix.T)
        self.rating_matrix_clustered['Cluster'] = self.item_clusters
        
        # Crear una matriz de similitud por cada clúster
        self.cluster_similarity = {}
        for cluster in range(self.n_clusters):
            cluster_items = self.rating_matrix_clustered[self.rating_matrix_clustered['Cluster'] == cluster].index
            cluster_ratings = self.rating_matrix[cluster_items].fillna(0)  # Temporalmente reemplazamos NaN para calcular la similitud
            if not cluster_ratings.empty:
                item_similarity = cosine_similarity(cluster_ratings.T)
                self.cluster_similarity[cluster] = pd.DataFrame(item_similarity, index=cluster_items, columns=cluster_items)
        
        # Calcular las calificaciones predichas
        self.predicted_ratings = self.predict_ratings_with_clustering()

    def predict_ratings_with_clustering(self):
        pred = np.zeros(self.rating_matrix.shape)
        
        for cluster, similarity_matrix in self.cluster_similarity.items():
            cluster_items = similarity_matrix.columns
            if len(cluster_items) > 0:
                user_means = self.rating_matrix[cluster_items].mean(axis=1, skipna=True).values.reshape(-1, 1)
                ratings_demeaned = self.rating_matrix[cluster_items].sub(user_means, axis=0)
                
                # Manejo de NaN: aseguramos que no contribuyan al cálculo
                similarity_sum = np.abs(similarity_matrix).sum(axis=1)
                similarity_sum[similarity_sum == 0] = 1  # Evitar división por 0
                pred[:, self.rating_matrix.columns.get_indexer(cluster_items)] = user_means + (similarity_matrix.dot(ratings_demeaned.fillna(0).T).T / similarity_sum)
    
        # Manejo de NaN en las predicciones: Si un valor sigue siendo NaN, mantenemos NaN o lo manejamos según sea necesario
        pred_df = pd.DataFrame(pred, index=self.rating_matrix.index, columns=self.rating_matrix.columns)
        pred_df = pred_df.where(~self.rating_matrix.isna(), self.rating_matrix)  # Si el valor original era NaN, mantenlo como NaN
        
        return pred_df

    def get_recommendations(self, user_id, top_n=200):
        user_ratings = self.predicted_ratings.loc[user_id]
        sorted_ratings = user_ratings.sort_values(ascending=False).head(top_n)
        recomendaciones_df = pd.DataFrame({'MovieID': sorted_ratings.index, 'Rating': sorted_ratings.values})
        recomendaciones_df = recomendaciones_df.merge(self.movies[['MovieID', 'Title', 'Genres']], on='MovieID', how='left')
        return recomendaciones_df

# Ejemplo de uso en el mismo archivo
if __name__ == "__main__":
    collaborative_filtering = CollaborativeFilteringWithClustering(ratings, movies)
    user_id = 1
    print(f"Recomendaciones para el usuario {user_id}:")
    print(collaborative_filtering.get_recommendations(user_id))

def get_movies_by_collaborative(user_id):
    collaborative_filtering = CollaborativeFilteringWithClustering(ratings, movies)
    recommendations_df = collaborative_filtering.get_recommendations(user_id)

    # Convert the DataFrame to a dictionary {MovieID: Similarity}
    recommendations_dict = pd.Series(recommendations_df['Rating'].values, index=recommendations_df['MovieID']).to_dict()
    
    return recommendations_dict