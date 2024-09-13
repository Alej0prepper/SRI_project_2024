from recommendation_system.load import ratings, movies
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans

class CollaborativeFilteringWithClustering:
    """
    Collaborative filtering with clustering approach for movie recommendations.

    This class uses KMeans clustering to group similar movies based on user ratings,
    calculates cosine similarity within each cluster, and predicts user ratings for
    movies they haven't rated yet. The predicted ratings are used to generate movie
    recommendations.

    Attributes:
    - ratings (DataFrame): The user-movie rating DataFrame with columns ['UserID', 'MovieID', 'Rating'].
    - movies (DataFrame): The movie details DataFrame with columns ['MovieID', 'Title', 'Genres'].
    - n_clusters (int): The number of clusters to use for KMeans. Default is 5.
    - rating_matrix (DataFrame): The user-item rating matrix.
    - kmeans (KMeans): The KMeans clustering model.
    - item_clusters (array): The cluster labels for each movie.
    - rating_matrix_clustered (DataFrame): The rating matrix with an added 'Cluster' column.
    - cluster_similarity (dict): A dictionary mapping cluster numbers to their corresponding
      similarity matrices.
    - predicted_ratings (DataFrame): The DataFrame of predicted ratings for all users and movies.
    """

    def __init__(self, ratings, movies, n_clusters=10):
        """
        Initializes the collaborative filtering model with clustering.

        Param:
        - ratings (DataFrame): The user-movie rating DataFrame.
        - movies (DataFrame): The movie details DataFrame.
        - n_clusters (int): The number of clusters to use for KMeans. Default is 5.
        """
        self.ratings = ratings
        self.movies = movies
        self.n_clusters = n_clusters

        self.rating_matrix = self.ratings.pivot_table(index='UserID', columns='MovieID', values='Rating')

        self.kmeans = KMeans(n_clusters=self.n_clusters, random_state=42)
        self.item_clusters = self.kmeans.fit_predict(self.rating_matrix.T.fillna(0))
        
        self.rating_matrix_clustered = pd.DataFrame(self.rating_matrix.T)
        self.rating_matrix_clustered['Cluster'] = self.item_clusters
        
        self.cluster_similarity = {}
        for cluster in range(self.n_clusters):
            cluster_items = self.rating_matrix_clustered[self.rating_matrix_clustered['Cluster'] == cluster].index
            cluster_ratings = self.rating_matrix[cluster_items].fillna(0)
            if not cluster_ratings.empty:
                item_similarity = cosine_similarity(cluster_ratings.T)
                self.cluster_similarity[cluster] = pd.DataFrame(item_similarity, index=cluster_items, columns=cluster_items)
        
        self.predicted_ratings = self.predict_ratings_with_clustering()

    def predict_ratings_with_clustering(self):
        """
        Predicts ratings for all users and movies using the clustering-based collaborative filtering approach.

        This method calculates predicted ratings by taking into account the similarity of movies within
        the same cluster. It adjusts the ratings based on user-specific average ratings.

        Returns:
        - DataFrame: A DataFrame containing predicted ratings for each user and movie, with NaN values replaced by 0.
        """
        # Initialize the prediction matrix with zeros
        pred = np.zeros(self.rating_matrix.shape)
        
        # Iterate through each cluster and calculate predicted ratings
        for cluster, similarity_matrix in self.cluster_similarity.items():
            cluster_items = similarity_matrix.columns
            
            # Check if there are items in the cluster
            if len(cluster_items) > 0:
                # Compute the mean rating for each user across the movies in the cluster
                user_means = self.rating_matrix[cluster_items].mean(axis=1, skipna=True).values.reshape(-1, 1)
                
                # Demean the ratings (subtract user-specific average ratings)
                ratings_demeaned = self.rating_matrix[cluster_items].sub(user_means, axis=0)
                
                # Calculate the sum of similarities, avoiding division by zero
                similarity_sum = np.abs(similarity_matrix).sum(axis=1)
                similarity_sum[similarity_sum == 0] = 1  # Ensure no division by zero
                
                # Predict the ratings for the movies in the cluster
                pred[:, self.rating_matrix.columns.get_indexer(cluster_items)] = (
                    user_means + (similarity_matrix.dot(ratings_demeaned.fillna(0).T).T / similarity_sum)
                )
        
        # Convert the prediction matrix to a DataFrame
        pred_df = pd.DataFrame(pred, index=self.rating_matrix.index, columns=self.rating_matrix.columns)
        
        # Replace NaN values in the predicted ratings with 0
        pred_df = pred_df.fillna(0)
        
        return pred_df


    def get_recommendations(self, user_id, top_n=200):
        """
        Generates top movie recommendations for a specific user based on predicted ratings.
        Excludes movies the user has already rated.

        Param:
        - user_id (int): The ID of the user to generate recommendations for.
        - top_n (int): The number of top recommendations to return. Default is 200.

        Returns:
        - DataFrame: A DataFrame containing the top-N recommended movies for the user, with columns
        ['MovieID', 'Rating', 'Title', 'Genres'].
        """
        # Get the ratings the user has already provided
        user_rated_movies = self.rating_matrix.loc[user_id].dropna().index

        # Get the predicted ratings for the user
        user_ratings = self.predicted_ratings.loc[user_id]

        # Filter out movies the user has already rated
        user_ratings_filtered = user_ratings.drop(user_rated_movies)
        
        # Sort the filtered ratings and return top-N recommendations
        sorted_ratings = user_ratings_filtered.sort_values(ascending=False).head(top_n)
        recomendaciones_df = pd.DataFrame({'MovieID': sorted_ratings.index, 'Rating': sorted_ratings.values})
        
        # Merge with movie details (title and genres)
        recomendaciones_df = recomendaciones_df.merge(self.movies[['MovieID', 'Title', 'Genres']], on='MovieID', how='left')
        
        return recomendaciones_df


def get_movies_by_collaborative(user_id):
    """
    Retrieves movie recommendations for a user using the collaborative filtering with clustering approach.

    Param:
    - user_id (int): The ID of the user to generate recommendations for.

    Returns:
    - dict: A dictionary where keys are MovieIDs and values are the predicted ratings for the user.
    """
    collaborative_filtering = CollaborativeFilteringWithClustering(ratings, movies)

    recommendations_df = collaborative_filtering.get_recommendations(user_id)

    recommendations_dict = pd.Series(recommendations_df['Rating'].values, index=recommendations_df['MovieID']).to_dict()
    
    return recommendations_dict
