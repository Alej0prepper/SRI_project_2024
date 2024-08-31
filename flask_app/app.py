import math
import os
import sys
from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import time
import random

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from recommendation_system.load import movies
from recommendation_system.weighted_hybrid_system import weighted_hybrid_recommendations

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# File paths for the .dat files
USER_DATA_FILE = 'ml-1m/users.dat'
MOVIE_DATA_FILE = 'ml-1m/movies.dat'
RATING_DATA_FILE = 'ml-1m/ratings.dat'

# Function to read data from a .dat file
def read_data_from_file(file_path, headers):
    data = []
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='latin-1') as file:
            for line in file:
                row = line.strip().split('::')  # Manually split by '::'
                item = dict(zip(headers, row))
                if 'Genres' in item:
                    item['Genres'] = item['Genres'].split('|')  # Split genres into a list
                data.append(item)
    return data

# Function to write data to a .dat file
def write_data_to_file(file_path, headers, data):
    with open(file_path, 'w', encoding='latin-1') as file:
        for item in data:
            if 'Genres' in item:
                item['Genres'] = '|'.join(item['Genres'])  # Join genres back into a string
            line = '::'.join([item[header] for header in headers])
            file.write(line + '\n')


@app.route('/users', methods=['GET', 'POST'])
def handle_users():
    headers = ['UserID', 'Gender', 'Age', 'Occupation', 'Zip-code']
    users = read_data_from_file(USER_DATA_FILE, headers)
    
    if request.method == 'POST':
        data = request.json
        print(data)
        new_user = {
            'UserID': str(len(users) + 1),  # Auto-increment UserID
            'Gender': data['gender'],
            'Age': str(data['age']),
            'Occupation': str(data['occupation']),
            'Zip-code': data['zip_code']
        }
        users.append(new_user)
        write_data_to_file(USER_DATA_FILE, headers, users)
        return jsonify({"message": "User created"}), 201
    
    if request.method == 'GET':
        return jsonify(users), 200
    
@app.route('/ratings/<int:user_id>/<int:movie_id>', methods=['GET'])
def get_rating_for_user_movie(user_id, movie_id):
    headers = ['UserID', 'MovieID', 'Rating', 'Timestamp']
    ratings = read_data_from_file(RATING_DATA_FILE, headers)
    
    # Find the specific rating by user_id and movie_id
    rating = next((r for r in ratings if int(r['UserID']) == user_id and int(r['MovieID']) == movie_id), None)
    
    if rating is None:
        return jsonify({"error": "Rating not found"}), 404
    
    return jsonify({
        'UserID': rating['UserID'],
        'MovieID': rating['MovieID'],
        'Rating': rating['Rating'],
        'Timestamp': rating['Timestamp']
    }), 200

@app.route('/users/<int:user_id>', methods=['GET', 'PUT', 'DELETE'])
def handle_user(user_id):
    headers = ['UserID', 'Gender', 'Age', 'Occupation', 'Zip-code']
    users = read_data_from_file(USER_DATA_FILE, headers)
    user = next((u for u in users if int(u['UserID']) == user_id), None)
    
    if user is None:
        return jsonify({"error": "User not found"}), 404
    
    if request.method == 'GET':
        return jsonify(user), 200
    
    if request.method == 'PUT':
        data = request.json
        user['Gender'] = data.get('gender', user['Gender'])
        user['Age'] = str(data.get('age', user['Age']))
        user['Occupation'] = str(data.get('occupation', user['Occupation']))
        user['Zip-code'] = data.get('zip_code', user['Zip-code'])
        write_data_to_file(USER_DATA_FILE, headers, users)
        return jsonify({"message": "User updated"}), 200
    
    if request.method == 'DELETE':
        users = [u for u in users if int(u['UserID']) != user_id]
        write_data_to_file(USER_DATA_FILE, headers, users)
        return jsonify({"message": "User deleted"}), 200

@app.route('/movies', methods=['GET'])
def get_movies():
    headers = ['MovieID', 'Title', 'Genres']
    movies = read_data_from_file(MOVIE_DATA_FILE, headers)
    return jsonify(movies), 200

@app.route('/ratings', methods=['GET', 'POST'])
def handle_ratings():
    headers = ['UserID', 'MovieID', 'Rating', 'Timestamp']
    ratings = read_data_from_file(RATING_DATA_FILE, headers)
    
    if request.method == 'POST':
        data = request.json

        # Generate a random timestamp within the past 5 years if not provided
        random_timestamp = str(random.randint(int(time.time()) - 5 * 365 * 24 * 60 * 60, int(time.time())))
        
        new_rating = {
            'UserID': str(data['user_id']),
            'MovieID': str(data['movie_id']),
            'Rating': str(data['rating']),
            'Timestamp': str(random_timestamp)
        }
        
        ratings.append(new_rating)
        write_data_to_file(RATING_DATA_FILE, headers, ratings)
        return jsonify({"message": "Rating created", "timestamp": new_rating['Timestamp']}), 201
    
    if request.method == 'GET':
        return jsonify(ratings), 200

@app.route('/ratings/<int:user_id>/<int:movie_id>', methods=['PUT'])
def handle_rating(user_id, movie_id):
    headers = ['UserID', 'MovieID', 'Rating', 'Timestamp']
    ratings = read_data_from_file(RATING_DATA_FILE, headers)
    rating = next((r for r in ratings if int(r['UserID']) == user_id and int(r['MovieID']) == movie_id), None)
    
    if rating is None:
        return jsonify({"error": "Rating not found"}), 404
    
    
    if request.method == 'PUT':
        data = request.json
        rating['Rating'] = str(data.get('rating', rating['Rating']))
        write_data_to_file(RATING_DATA_FILE, headers, ratings)
        return jsonify({"message": "Rating updated"}), 200


@app.route('/recommendations/<int:user_id>', methods=['GET'])
def get_recommendations(user_id):
    recommendations = weighted_hybrid_recommendations(user_id)

    valid_recommendations = [(item_id, score) for item_id, score in recommendations if not math.isnan(score)]
    
    top_recommendations = sorted(valid_recommendations, key=lambda x: x[1], reverse=True)[:10]
    
    recommendations_df = pd.DataFrame(top_recommendations, columns=['MovieID', 'Score'])

    movie_headers = ['MovieID', 'Title', 'Genres']
    movie_data = read_data_from_file(MOVIE_DATA_FILE, movie_headers)
    movies_df = pd.DataFrame(movie_data)

    recommendations_df['MovieID'] = recommendations_df['MovieID'].astype(str)
    
    movies_df['MovieID'] = movies_df['MovieID'].astype(str)
    
    recommendations_with_titles = recommendations_df.merge(movies_df, on='MovieID', how='left')

    return jsonify([{
        'MovieID': row['MovieID'],
        'Title': row['Title'],
        'Score': row['Score']
    } for _, row in recommendations_with_titles.iterrows()])


if __name__ == "__main__":
    app.run(debug=False)
