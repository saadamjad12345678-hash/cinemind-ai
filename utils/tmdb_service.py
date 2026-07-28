import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TMDB_API_KEY")


def search_movie(movie):

    url = f"https://api.themoviedb.org/3/search/movie?query={movie}&api_key={API_KEY}"

    response = requests.get(url)

    data = response.json()

    if data["results"]:
        return data["results"][0]

    return None


def get_trending_hollywood():

    url = (
        f"https://api.themoviedb.org/3/trending/movie/week"
        f"?api_key={API_KEY}"
    )

    response = requests.get(url)

    data = response.json()

    return data["results"][:10]


def get_trending_bollywood():

    url = (
        f"https://api.themoviedb.org/3/discover/movie"
        f"?api_key={API_KEY}"
        f"&with_original_language=hi"
        f"&sort_by=popularity.desc"
        f"&vote_count.gte=500"
        f"&primary_release_date.gte=2022-01-01"
    )

    response = requests.get(url)

    data = response.json()

    return data["results"][:10]


def get_recommended_movies(genre_ids, language, movie_id, pages=3):

    if not genre_ids:
        return []

    genre = ",".join(str(g) for g in genre_ids[:2])

    movies = []

    for page in range(1, pages + 1):

        url = (
            f"https://api.themoviedb.org/3/discover/movie"
            f"?api_key={API_KEY}"
            f"&with_genres={genre}"
            f"&with_original_language={language}"
            f"&sort_by=popularity.desc"
            f"&vote_average.gte=6"
            f"&vote_count.gte=100"
            f"&page={page}"
        )

        response = requests.get(url)

        data = response.json()

        for movie in data.get("results", []):

            if movie["id"] == movie_id:
                continue

            if movie.get("poster_path") is None:
                continue

            score = 0

            # Rating (0–50)
            score += movie["vote_average"] * 5

            # Popularity (0–30)
            score += min(movie["popularity"] / 10, 30)

            # Vote Count (0–20)
            score += min(movie["vote_count"] / 100, 20)

            movie["ai_score"] = round(score)

            movies.append(movie)

    # Remove duplicates
    unique_movies = []

    seen = set()

    for movie in movies:

        if movie["id"] not in seen:

            seen.add(movie["id"])

            unique_movies.append(movie)

    unique_movies = sorted(
        unique_movies,
        key=lambda x: x["ai_score"],
        reverse=True
    )

    return unique_movies[:20]

def get_movies_by_genre(genre_id, language):

    movies = []

    for page in range(1,4):

        url = (
            f"https://api.themoviedb.org/3/discover/movie"
            f"?api_key={API_KEY}"
            f"&with_genres={genre_id}"
            f"&with_original_language={language}"
            f"&sort_by=popularity.desc"
            f"&vote_average.gte=6"
            f"&vote_count.gte=200"
            f"&page={page}"
        )

        response = requests.get(url)

        data = response.json()

        movies.extend(data.get("results", []))

    unique = []

    ids = set()

    for movie in movies:

        if movie["id"] not in ids:

            ids.add(movie["id"])

            unique.append(movie)

    return unique[:30]