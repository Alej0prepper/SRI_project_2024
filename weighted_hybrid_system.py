import math
import pandas as pd
from load import movies
from colaborativo_items import get_movies_by_collaborative
from contenido import Get_movies_by_content
from demografia import Get_movies_by_demography

# Define weights for each recommendation technique
WEIGHTS = {
    'collaborative': 0.5,
    'content': 0.3,
    'demographic': 0.2
}

def weighted_hybrid_recommendations(user_id):
    # Get recommendations from each method
    collaborative_scores = get_movies_by_collaborative(user_id)
    content_scores = Get_movies_by_content(user_id)
    demographic_scores = Get_movies_by_demography(user_id)

    # Initialize a dictionary to store combined scores
    combined_scores = {}

    # Combine scores with weights
    for item in set(collaborative_scores.keys()).union(content_scores.keys(), demographic_scores.keys()):
        collab_score = collaborative_scores.get(item, 0)
        content_score = content_scores.get(item, 0)
        demo_score = demographic_scores.get(item, 0)

        # Calculate the weighted score
        combined_scores[item] = (
            WEIGHTS['collaborative'] * float(collab_score) +
            WEIGHTS['content'] * float(content_score) +
            WEIGHTS['demographic'] * float(demo_score)
        )

    # Sort items by combined score in descending order
    sorted_items = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)

    # Return the top recommendations
    return sorted_items

if __name__ == "__main__":
    user_id = 1

    recommendations = weighted_hybrid_recommendations(user_id)

    valid_recommendations = [(item_id, score) for item_id, score in recommendations if not math.isnan(score)]

    top_recommendations = sorted(valid_recommendations, key=lambda x: x[1], reverse=True)[:10]

    recommendations_df = pd.DataFrame(top_recommendations, columns=['MovieID', 'Score'])

    # Merge with the movies DataFrame to get the titles
    recommendations_with_titles = recommendations_df.merge(movies[['MovieID', 'Title']], on='MovieID', how='left')


    print("Top 10 recommendations (MovieID, Title, Score):")
    for index, row in recommendations_with_titles.iterrows():
        print(f"Movie {row['MovieID']}: ({row['Title']}): {row['Score']:.4f}")
