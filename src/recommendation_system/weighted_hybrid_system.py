import pandas as pd
from recommendation_system.collaborative_by_items import get_movies_by_collaborative
from recommendation_system.content import Get_movies_by_content
from recommendation_system.demography import Get_movies_by_demography
from recommendation_system.load import *

def weighted_hybrid_recommendations(user_id, weights):
    """
    Generates movie recommendations for a user by combining collaborative, content-based, 
    and demographic recommendation scores using a weighted hybrid approach.

    Param:
    - user_id (int): The ID of the user to generate recommendations for.
    - weights (dict): A dictionary with weights for 'collaborative', 'content', and 'demographic'.

    Returns:
    - list: A sorted list of tuples, where each tuple contains a MovieID and its combined score, 
      sorted by score in descending order.
    """
    try:
        collaborative_scores = get_movies_by_collaborative(user_id)
    except:
        print("Can't get collaborative recommendations for user")
        collaborative_scores = dict()
    
    try:
        content_scores = Get_movies_by_content(user_id)
    except:
        print("Can't get content recommendations for user")
        content_scores = dict()
        
    try:
        demographic_scores = Get_movies_by_demography(user_id)
    except:
        print("Can't get demography recommendations for user")
        demographic_scores = dict()

    # Get the movies already rated by the user to exclude them from recommendations
    ratings = load_ratings()
    rated_movies = set(ratings[ratings['UserID'] == user_id]['MovieID'])

    combined_scores = {}
    for item in set(collaborative_scores.keys()).union(content_scores.keys(), demographic_scores.keys()):
        if item in rated_movies:
            continue  # Skip movies the user has already rated

        collab_score = collaborative_scores.get(item, 0)
        content_score = content_scores.get(item, 0)
        demo_score = demographic_scores.get(item, 0)

        combined_scores[item] = (
            weights.get('collaborative', 0) * float(collab_score) +
            weights.get('content', 0) * float(content_score) +
            weights.get('demographic', 0) * float(demo_score)
        )

    sorted_items = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
    return sorted_items

# if __name__ == "__main__":
#     # Load data
#     movies = load_movies()
    
#     # Define user and weights for recommendation sources
#     user_id = 1
#     weights = {
#         'collaborative': 0.5,
#         'content': 0.3,
#         'demographic': 0.2
#     }

#     # Get weighted hybrid recommendations
#     recommendations = weighted_hybrid_recommendations(user_id, weights)

#     # Get the top 10 recommendations
#     top_recommendations = recommendations[:10]

#     # Convert to DataFrame for easier merging and displaying
#     recommendations_df = pd.DataFrame(top_recommendations, columns=['MovieID', 'Score'])

#     # Merge with movie titles
#     recommendations_with_titles = recommendations_df.merge(movies[['MovieID', 'Title']], on='MovieID', how='left')
