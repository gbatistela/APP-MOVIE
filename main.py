import pandas as pd
import numpy as np
from typing import Union
from fastapi import FastAPI
from sklearn.metrics.pairwise import cosine_similarity

app = FastAPI() 

df_movies= pd.read_csv("df_movies.csv",low_memory=False)

@app.get("/Proyecto Veronica van Vugt")
def read_root():
    return {"Hello": "World"}



@app.get("/Cantidad de filmaciones mes")
def cantidad_filmaciones_mes(mes:str):
    # Diccionario de meses en español
    meses = {
        1: 'Enero',
        2: 'Febrero',
        3: 'Marzo',
        4: 'Abril',
        5: 'Mayo',
        6: 'Junio',
        7: 'Julio',
        8: 'Agosto',
        9: 'Septiembre',
        10: 'Octubre',
        11: 'Noviembre',
        12: 'Diciembre'
    }    

    df_movies['release_date'] = pd.to_datetime(df_movies['release_date'], errors='coerce')

    # Extraer el mes numérico
    df_movies['mes_num'] = df_movies['release_date'].dt.month

    # Convertir el mes numérico a nombre de mes
    df_movies['mes'] = df_movies['mes_num'].map(meses)

    meses = df_movies[df_movies['mes'] == mes].shape[0]

    return f"{meses} cantidad de películas fueron estrenadas en el mes de {mes}"


@app.get("/Cantidad de filmaciones dias")
def cantidad_filmaciones_dia( Dia :str):

    # Crear una columna adicional con el nombre del día de la semana en inglés
    df_movies['day_of_week_en'] = df_movies['release_date'].dt.strftime('%A').str.lower()
 
    dias = {
        'monday': 'lunes',
        'tuesday': 'martes',
        'wednesday': 'miercoles',
        'thursday': 'jueves',
        'friday': 'viernes',
        'saturday': 'sabado',
        'sunday': 'domingo'
    }

    # Traducir los días de la semana al español usando el diccionario
    df_movies['day_of_week_es'] = df_movies['day_of_week_en'].map(dias)

    # Filtrar las películas que coinciden con el día consultado
    count = df_movies[df_movies['day_of_week_es'] == Dia].shape[0]

    return f"{count} cantidad de películas fueron estrenadas en los días {Dia}"

@app.get("/score_titulo")
def score_titulo( titulo:str ):

    # Buscar la película por el título
    pelicula = df_movies[df_movies['title'].str.lower() == titulo.lower()]

    # Extraer el título, el año y el score
    titulo = pelicula['title'].values[0]
    anio = pelicula['release_year'].values[0]
    score = pelicula['vote_average'].values[0]

    return f"La película {titulo} fue estrenada en el año {anio} con un score/popularidad de {score}"

@app.get("/votos_titulo")
def votos_titulo( titulo:str ):

    # Buscar la película por el título
    pelicula = df_movies[df_movies['title'].str.lower() == titulo.lower()]

    # Contar la cantidad de votos
    votos = pelicula["vote_count"].values[0]
    if votos >= 2000:

        # Extraer el título, el año y el score
        titulo= pelicula['title'].values[0]
        cantidad_votos = pelicula["vote_count"].values[0]
        promedio_votos = pelicula['vote_average'].values[0]
        año = pelicula["release_year"].values[0]

        return f"La película {titulo} fue estrenada en el año {año}. La misma cuenta con un total de {cantidad_votos} valoraciones, con un promedio de {promedio_votos}"
    
    else:
        return f"La película {titulo} no cumple con las condiciones de superar los 2000 votos"


@app.get("/get_actor")
def get_actor(nombre_actor):
    # Filtrar el DataFrame para obtener solo las filas donde el actor está en el cast
    df_actor = df_movies[df_movies['actor'] == nombre_actor]
    
    # Contar el número de películas en las que ha participado
    cantidad_peliculas = df_actor.shape[0]
    
    # Filtrar para obtener solo las películas con retorno de inversión válido
    df_actor = df_actor[
        (df_actor['retorno_de_inversion'] != np.inf) &  # Excluir infinito
        (df_actor['retorno_de_inversion'] != -np.inf) &  # Excluir -infinito
        (df_actor['retorno_de_inversion'].notna()) &  # Excluir NaN
        (df_actor['retorno_de_inversion'] >= 0)  # Asegurarse de que el valor sea positivo
    ]
    
    # Calcular el promedio de retorno de inversión
    promedio_retorno = df_actor['retorno_de_inversion'].mean() if cantidad_peliculas > 0 else 0
    retorno_inversion =df_actor["retorno_de_inversion"].sum() 

    
    return f"El actor {nombre_actor} participado de {cantidad_peliculas} de filmaciones, el mismo ha obtenido un retorno de {retorno_inversion} un promedio de {promedio_retorno:.2f} filmación"



@app.get("/get_director")
def get_director(nombre_director):
    
    # Filtrar el dataframe por el nombre del director
    df_director= pd.DataFrame(df_movies[["director","retorno_de_inversion","release_year","title","revenue","budget"]])

    director_df = df_movies[df_movies['director'] == nombre_director]
    
    # Filtrar para obtener solo las películas con retorno de inversión válido
    director_df = director_df[
        (director_df['retorno_de_inversion'] != np.inf) &  # Excluir infinito
        (director_df['retorno_de_inversion'] != -np.inf) &  # Excluir -infinito
        (director_df['retorno_de_inversion'].notna()) &  # Excluir NaN
        (director_df['retorno_de_inversion'] >= 0)  # Asegurarse de que el valor sea positivo
    ]

    # Calcular el retorno total (éxito)
    retorno_total = director_df['retorno_de_inversion'].sum()
    
    # Crear una lista de diccionarios con la información de cada película
    peliculas_info = []
    for _, row in director_df.iterrows():
        peliculas_info.append({
            'titulo': row['title'],
            'fecha_lanzamiento': row['release_year'],
            'retorno_individual': row['retorno_de_inversion'],
            'costo': row['budget'],
            'ganancia': row['revenue']
        })
    
    return {
        'nombre_director': nombre_director,
        'retorno_total': retorno_total,
        'peliculas': peliculas_info
    }


@app.get("/Recomendacion_juego")
def Recomendacion_juego(pelicula:str):
    

        # Filtrar por películas lanzadas desde 2017
        df_movies_filtered = df_movies[df_movies['release_year'] >= 2017]

        # Crear una matriz de usuario-item
        user_item_matrix = pd.pivot_table(df_movies_filtered, values='vote_average', index='movie_id', columns='title', fill_value=0)

        # Calcular la similitud de coseno entre peliculas
        peliculas_similares = cosine_similarity(user_item_matrix.T)

        # Encontrar el índice del juego en la matriz
        peliculas_index = user_item_matrix.columns.get_loc(pelicula)
        

        # Calcular la similitud de coseno entre el juego deseado y otros juegos
        peliculas_similares = peliculas_similares[peliculas_index] 

        # Crear un DataFrame con juegos similares y sus similitudes
        similar_peliculas = pd.DataFrame({
            'Peliculas': user_item_matrix.columns,
            'Similarity' : peliculas_similares
        })

        # Ordenar los juegos por similitud en orden descendente
        top_5_recomendadas = similar_peliculas.sort_values(by='Similarity', ascending=False).head(5)

        return top_5_recomendadas