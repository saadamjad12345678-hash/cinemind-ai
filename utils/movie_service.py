import sqlite3
import pandas as pd
import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")

DATABASE = "database/movies.db"


def get_connection():
    return sqlite3.connect(DATABASE)


# ------------------------
# Search Movie (Database)
# ------------------------

def search_movie(title):

    conn = get_connection()

    query = """
    SELECT *
    FROM clean_movies
    WHERE LOWER(title) LIKE LOWER(?)
    ORDER BY imdb_rating DESC,
             popularity DESC
    LIMIT 1
    """

    movie = pd.read_sql(
        query,
        conn,
        params=(f"%{title}%",)
    )

    conn.close()

    if len(movie) == 0:
        return None

    return movie.iloc[0].to_dict()


# ------------------------
# TMDB Movie Details
# ------------------------

def get_movie_details(movie_id):

    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}"

    response = requests.get(url)

    movie = response.json()

# Convert genre objects to string
    if "genres" in movie:
     movie["genres"] = " • ".join(
        [g["name"] for g in movie["genres"]]
    )

    return movie


# ------------------------
# Trailer
# ------------------------

def get_movie_trailer(movie_id):

    url = f"https://api.themoviedb.org/3/movie/{movie_id}/videos?api_key={API_KEY}"

    response = requests.get(url)

    data = response.json()

    for video in data.get("results", []):

        if video["site"] == "YouTube" and video["type"] == "Trailer":
            return video["key"]

    return None


# ------------------------
# Cast
# ------------------------

def get_movie_cast(movie_id):

    url = f"https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={API_KEY}"

    response = requests.get(url)

    data = response.json()

    return data.get("cast", [])[:6]