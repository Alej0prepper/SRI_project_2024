import pandas as pd
import os 
# Cargar los datos
print(os.getcwd())
path = os.getcwd()
ratings = pd.read_csv(path + '/ml-1m/ratings.dat', sep='::', names=['UserID', 'MovieID', 'Rating', 'Timestamp'], engine='python',encoding='ISO-8859-1')
users = pd.read_csv(path + '/ml-1m/users.dat', sep='::', names=['UserID', 'Gender', 'Age', 'Occupation', 'Zip-code'], engine='python',encoding='ISO-8859-1')
movies = pd.read_csv(path + '/ml-1m/movies.dat', sep='::', names=['MovieID', 'Title', 'Genres'], engine='python', encoding='ISO-8859-1')

# Mostrar una parte de los datos para verificar
# print(ratings.head())
# print(users.head())
# print(movies.head())
