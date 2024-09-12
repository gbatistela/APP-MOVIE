import pandas as pd
from typing import Union
from fastapi import FastAPI

app = FastAPI()

df_movies= pd.read_csv("df_movies.csv")

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}

@app.get("/Cantida de filmaciones")
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


def score_titulo( titulo:str ):

    # Buscar la película por el título
    pelicula = df_movies[df_movies['title'].str.lower() == titulo.lower()]

    # Extraer el título, el año y el score
    titulo = pelicula['title'].values[0]
    anio = pelicula['release_year'].values[0]
    score = pelicula['vote_average'].values[0]

    return f"La película {titulo} fue estrenada en el año {anio} con un score/popularidad de {score}"


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