import pandas as pd
from load import movies
from collections import Counter
from contenido import Get_movies_by_content
from conocimiento import Get_movies_by_knowledge
from demografia import Get_movies_by_demography
from colaborativo_items import Get_movies_by_colaborative

def obtener_recomendaciones_unificadas_por_movieid(*dataframes_de_recomendaciones):
    # Extraer la columna 'MovieID' de cada DataFrame y combinar todas en una lista
    todas_las_peliculas = []
    for df in dataframes_de_recomendaciones:
        todas_las_peliculas.extend(df['MovieID'].tolist())

    # Contar cuántas veces aparece cada 'MovieID'
    conteo_peliculas = Counter(todas_las_peliculas)

    # Ordenar las películas por la cantidad de apariciones (de más a menos)
    peliculas_ordenadas = sorted(conteo_peliculas.items(), key=lambda x: x[1], reverse=True)

    # Convertir el conteo en un DataFrame para poder hacer el merge
    recomendaciones_finales_df = pd.DataFrame(peliculas_ordenadas, columns=['MovieID', 'Count'])

    return recomendaciones_finales_df

user_id = 1
crop = 10

# Obtener recomendaciones de diferentes métodos
recomendaciones_colaborativo_items = Get_movies_by_colaborative(user_id).head(crop)
recomendaciones_contenido = Get_movies_by_content(user_id).head(crop)
recomendaciones_conocimiento = Get_movies_by_knowledge(user_id).head(crop)
recomendaciones_demografia = Get_movies_by_demography(user_id).head(crop)

print(recomendaciones_colaborativo_items)
print(recomendaciones_conocimiento)
print(recomendaciones_contenido)
print(recomendaciones_demografia)
# Obtener la recomendación unificada
recomendaciones_finales_df = obtener_recomendaciones_unificadas_por_movieid(
    recomendaciones_colaborativo_items,
    recomendaciones_contenido,
    recomendaciones_conocimiento,
    recomendaciones_demografia
)

# Hacer un merge de las recomendaciones con la tabla de películas para obtener título y trama
recomendaciones_completas = pd.merge(recomendaciones_finales_df, movies, on='MovieID', how='left')

# Mostrar las recomendaciones con título, trama y cantidad de apariciones
print(recomendaciones_completas[['MovieID', 'Title', 'Count']])
