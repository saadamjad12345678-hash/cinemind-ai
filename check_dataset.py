import sqlite3
import pandas as pd

conn = sqlite3.connect("database/movies.db")

movies = [
    "Golmaal",
    "Dhamaal",
    "Hera Pheri",
    "Welcome",
    "Bhool Bhulaiyaa",
    "Munna Bhai"
]

for movie in movies:

    df = pd.read_sql(
        """
        SELECT title, genres, release_date
        FROM clean_movies
        WHERE LOWER(title) LIKE LOWER(?)
        """,
        conn,
        params=(f"%{movie}%",)
    )

    print("\n====================")
    print(movie)
    print(df)

conn.close()