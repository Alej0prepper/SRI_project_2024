import pandas as pd
from load import movies
from collections import Counter
from contenido import Get_movies_by_content
from conocimiento import Get_movies_by_knowledge
from demografia import Get_movies_by_demography
from colaborativo_items import Get_movies_by_colaborative

def obtener_recomendaciones_con_origen(user_id, crop=200):
    # Obtener recomendaciones de diferentes métodos y añadir una columna con el origen
    recomendaciones_colaborativo_items = Get_movies_by_colaborative(user_id).head(crop)
    recomendaciones_colaborativo_items['Recomendado_Por'] = 'Colaborativo'

    recomendaciones_contenido = Get_movies_by_content(user_id).head(crop)
    recomendaciones_contenido['Recomendado_Por'] = 'Contenido'

    # recomendaciones_conocimiento = Get_movies_by_knowledge(user_id).head(crop)
    # recomendaciones_conocimiento['Recomendado_Por'] = 'Conocimiento'

    recomendaciones_demografia = Get_movies_by_demography(user_id)
    recomendaciones_demografia['Recomendado_Por'] = 'Demografía'

    # Unir todas las recomendaciones en un solo DataFrame
    todas_las_recomendaciones = pd.concat([
        recomendaciones_colaborativo_items,
        recomendaciones_contenido,
        # recomendaciones_conocimiento,
        recomendaciones_demografia
    ])

    # Eliminar duplicados y mantener todas las fuentes de recomendación en caso de que una película sea recomendada por múltiples métodos
    todas_las_recomendaciones = todas_las_recomendaciones.drop_duplicates(subset=['MovieID', 'Recomendado_Por'])

    return todas_las_recomendaciones

def obtener_recomendaciones_unificadas_por_movieid(*dataframes_de_recomendaciones):
    todas_las_peliculas = []
    for df in dataframes_de_recomendaciones:
        todas_las_peliculas.extend(df['MovieID'].tolist())

    conteo_peliculas = Counter(todas_las_peliculas)
    peliculas_ordenadas = sorted(conteo_peliculas.items(), key=lambda x: x[1], reverse=True)
    recomendaciones_finales_df = pd.DataFrame(peliculas_ordenadas, columns=['MovieID', 'Count'])

    return recomendaciones_finales_df

# Ejemplo de uso
user_id = 1
crop = 100

# Obtener recomendaciones con el origen
recomendaciones_con_origen = obtener_recomendaciones_con_origen(user_id, crop)

# Unificar las recomendaciones por MovieID
recomendaciones_finales_df = obtener_recomendaciones_unificadas_por_movieid(
    recomendaciones_con_origen
)

# Hacer un merge de las recomendaciones con la tabla de películas para obtener título, género y cantidad de apariciones
recomendaciones_completas = pd.merge(recomendaciones_finales_df, movies, on='MovieID', how='left')

# Unir la información de origen a las recomendaciones finales
recomendaciones_completas = pd.merge(recomendaciones_completas, recomendaciones_con_origen[['MovieID', 'Recomendado_Por']], on='MovieID', how='left')

# Guardar como archivo Excel
recomendaciones_completas.to_excel("recomendaciones_completas_con_origen.xlsx", index=False)

# Mostrar las recomendaciones con título, género, cantidad de apariciones y origen de la recomendación
print(recomendaciones_completas[['MovieID', 'Title', 'Genres', 'Count', 'Recomendado_Por']])
