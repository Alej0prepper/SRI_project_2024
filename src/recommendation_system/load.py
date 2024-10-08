import pandas as pd
import os 
# Load info from csvs
path = os.getcwd()
def load_ratings():
    return pd.read_csv(path + '/ml-1m/ratings.dat', sep='::', names=['UserID', 'MovieID', 'Rating', 'Timestamp'], engine='python',encoding='ISO-8859-1')
def load_users():
    return pd.read_csv(path + '/ml-1m/users.dat', sep='::', names=['UserID', 'Gender', 'Age', 'Occupation', 'Zip-code'], engine='python',encoding='ISO-8859-1')
def load_movies():
    return pd.read_csv(path + '/ml-1m/movies.dat', sep='::', names=['MovieID', 'Title', 'Genres'], engine='python', encoding='ISO-8859-1')

ratings = pd.read_csv(path + '/ml-1m/ratings.dat', sep='::', names=['UserID', 'MovieID', 'Rating', 'Timestamp'], engine='python',encoding='ISO-8859-1')
users = pd.read_csv(path + '/ml-1m/users.dat', sep='::', names=['UserID', 'Gender', 'Age', 'Occupation', 'Zip-code'], engine='python',encoding='ISO-8859-1')
movies = pd.read_csv(path + '/ml-1m/movies.dat', sep='::', names=['MovieID', 'Title', 'Genres'], engine='python', encoding='ISO-8859-1')


