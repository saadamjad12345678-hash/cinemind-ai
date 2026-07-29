import sqlite3
import pandas as pd
from datetime import datetime

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATABASE = "database/movies.db"

# ===============================
# LOAD DATABASE
# ===============================

conn = sqlite3.connect(DATABASE)

movies = pd.read_sql(
    "SELECT * FROM clean_movies",
    conn
)

conn.close()

print("Movies Loaded :", len(movies))


# ===============================
# NORMALIZE FUNCTION
# ===============================

def normalize(series):

    minimum = series.min()
    maximum = series.max()

    if maximum == minimum:
        return series * 0

    return (series - minimum) / (maximum - minimum)


# ===============================
# RECENCY SCORE
# ===============================

def calculate_recency_score(release_date):

    try:
        year = int(str(release_date)[:4])
    except:
        return 0

    current_year = datetime.now().year

    age = current_year - year

    score = max(0, 1 - (age / 20))

    return score


# ===============================
# CREATE AI FEATURES
# ===============================

movies["combined_features"] = (
    movies["genres"].fillna("").astype(str) + " " +
    movies["keywords"].fillna("").astype(str) + " " +
    movies["cast"].fillna("").astype(str) + " " +
    movies["director"].fillna("").astype(str) + " " +
    movies["overview"].fillna("").astype(str)
)

# ===============================
# TF-IDF
# ===============================

vectorizer = TfidfVectorizer(

    stop_words="english",

    max_features=15000,

    ngram_range=(1,2),

    min_df=2
)

feature_matrix = vectorizer.fit_transform(

    movies["combined_features"]
)

print("TF-IDF Ready")

# ==========================================
# AI RECOMMENDATION FUNCTION
# ==========================================

def recommend(movie_title, top_n=20):

    movie = movies[
        movies["title"].str.lower() == movie_title.lower()
    ]

    if movie.empty:
        return []

    selected = movie.iloc[0]

    language = selected["original_language"]

    selected_genres = [
        g.strip().lower()
        for g in str(selected["genres"]).split(",")
        if g.strip()
    ]

    filtered = movies[
        movies["original_language"] == language
    ].copy()


    # --------------------------
    # Genre Matching
    # --------------------------

    def genre_match(genres):

        movie_genres = [
            g.strip().lower()
            for g in str(genres).split(",")
            if g.strip()
        ]

        common = len(
            set(selected_genres) &
            set(movie_genres)
        )

        return common

    filtered["genre_match"] = filtered["genres"].apply(
        genre_match
    )

    filtered = filtered[
        filtered["genre_match"] >= 1
    ].copy()


    # --------------------------
    # Bollywood / Hollywood Filters
    # --------------------------

    if language == "hi":

        filtered = filtered[
            (filtered["vote_average"] >= 5.8) &
            (filtered["vote_count"] >= 15)
        ].copy()

    else:

        filtered = filtered[
            (filtered["vote_average"] >= 6.5) &
            (filtered["vote_count"] >= 150) &
            (filtered["imdb_rating"] >= 6.0)
        ].copy()

    # --------------------------
    # Release Year
    # --------------------------

    filtered["release_year"] = (
        filtered["release_date"]
        .fillna("1900")
        .str[:4]
        .astype(int)
    )

    if language == "hi":

        filtered = filtered[
            filtered["release_year"] >= 2000
        ].copy()

    else:

        filtered = filtered[
            filtered["release_year"] >= 2005
        ].copy()

    filtered.reset_index(drop=True, inplace=True)

    # Make sure selected movie exists
    if selected["id"] not in filtered["id"].values:

        filtered = pd.concat(
            [filtered, pd.DataFrame([selected])],
            ignore_index=True
        )

    # --------------------------
    # Create Features
    # --------------------------

    filtered["combined"] = (

    filtered["genres"].fillna("") + " " +

    filtered["keywords"].fillna("") + " " +

    filtered["cast"].fillna("") + " " +

    filtered["director"].fillna("") + " " +

    filtered["overview"].fillna("")
)

    local_vectorizer = TfidfVectorizer(

        stop_words="english",

        max_features=15000,

        ngram_range=(1,2),

        min_df=2
    )

    matrix = local_vectorizer.fit_transform(
        filtered["combined"]
    )

    movie_index = filtered[
        filtered["id"] == selected["id"]
    ]

    if movie_index.empty:
        return []

    idx = movie_index.index[0]

    similarity = cosine_similarity(
        matrix[idx],
        matrix
    ).flatten()

    filtered["similarity"] = similarity

    # --------------------------
    # AI SCORE
    # --------------------------

    filtered["rating_score"] = normalize(
        filtered["imdb_rating"].fillna(0)
    )

    filtered["popularity_score"] = normalize(
        filtered["popularity"].fillna(0)
    )

    filtered["vote_score"] = normalize(
        filtered["vote_count"].fillna(0)
    )

    filtered["recency_score"] = filtered[
        "release_date"
    ].apply(calculate_recency_score)

    filtered["genre_score"] = normalize(
        filtered["genre_match"]
    )

    # --------------------------
    # FINAL AI SCORE
    # --------------------------

    filtered["ai_score"] = (

        filtered["similarity"] * 0.45 +

        filtered["genre_score"] * 0.25 +

        filtered["rating_score"] * 0.10 +

        filtered["popularity_score"] * 0.10 +

        filtered["vote_score"] * 0.05 +

        filtered["recency_score"] * 0.05

    ) * 100

    # --------------------------
    # SORT
    # --------------------------

    filtered = filtered.sort_values(

        by=[
            "ai_score",
            "vote_count",
            "popularity",
            "imdb_rating"
        ],

        ascending=False

    )

    # Remove selected movie
    filtered = filtered[
        filtered["id"] != selected["id"]
    ]

    # Remove duplicate titles
    filtered = filtered.drop_duplicates(
        subset="title"
    )

    return filtered.head(top_n)[

        [
            "id",
            "title",
            "poster_path",
            "genres",
            "release_date",
            "vote_average",
            "imdb_rating",
            "ai_score"
        ]

    ].to_dict("records")


# ==========================
# TEST
# ==========================

if __name__ == "__main__":

    result = recommend("Interstellar")

    print(pd.DataFrame(result).head(20))           