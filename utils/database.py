import sqlite3
import pandas as pd

DATABASE = "database/movies.db"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():
    return sqlite3.connect(DATABASE)


# ==========================================
# USERS TABLE
# ==========================================

def create_user_table():

    conn = get_connection()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        gmail TEXT UNIQUE,

        favorite_genre TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)

    conn.commit()
    conn.close()


def save_user(gmail):

    conn = sqlite3.connect("users.db")

    conn.execute("""

    CREATE TABLE IF NOT EXISTS app_users(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        gmail TEXT UNIQUE,

        favorite_genre TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )

    """)

    conn.execute(

        "INSERT OR IGNORE INTO app_users(gmail) VALUES(?)",

        (gmail,)

    )

    conn.commit()
    conn.close()

# ==========================================
# WATCH HISTORY
# ==========================================

def create_history_table():

    conn = get_connection()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS watch_history(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        gmail TEXT,

        movie_id INTEGER,

        watched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)

    conn.commit()
    conn.close()


def save_history(gmail, movie_id):

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO watch_history(gmail, movie_id)
        VALUES(?, ?)
        """,
        (gmail, movie_id)
    )

    conn.commit()
    conn.close()


def get_history(gmail, limit=20):

    conn = get_connection()

    query = """
    SELECT clean_movies.*

    FROM watch_history

    JOIN clean_movies

    ON watch_history.movie_id = clean_movies.id

    WHERE gmail = ?

    ORDER BY watched_at DESC

    LIMIT ?
    """

    df = pd.read_sql(
        query,
        conn,
        params=(gmail, limit)
    )

    conn.close()

    return df.to_dict("records")    

# ==========================================
# TRENDING MOVIES
# ==========================================

def get_trending_movies(language, limit=20):

    conn = get_connection()

    if language == "hi":

        query = """
        SELECT *

        FROM clean_movies

        WHERE

        original_language='hi'

        AND vote_count >= 20

        AND vote_average >= 5.8

        AND release_date >= '2015-01-01'

        ORDER BY

        release_date DESC,

        popularity DESC,

        vote_count DESC,

        vote_average DESC

        LIMIT ?
        """

    else:

        query = """
        SELECT *

        FROM clean_movies

        WHERE

        original_language='en'

        AND vote_count >= 400

        AND popularity >= 15

        AND imdb_rating >= 6

        AND vote_average >= 6.5

        AND release_date >= '2015-01-01'

        AND title NOT LIKE '%WWE%'
        AND title NOT LIKE '%RAW%'
        AND title NOT LIKE '%SmackDown%'
        AND title NOT LIKE '%Royal Rumble%'
        AND title NOT LIKE '%Season%'
        AND title NOT LIKE '%Episode%'

        ORDER BY

        release_date DESC,

        popularity DESC,

        vote_count DESC,

        vote_average DESC

        LIMIT ?
        """

    df = pd.read_sql(query, conn, params=(limit,))

    conn.close()

    return df.to_dict("records")

# ==========================================
# GENRE MOVIES
# ==========================================

def get_movies_by_genre(language, genre, limit=30):

    conn = get_connection()

    if language == "hi":

        query = """
        SELECT *

        FROM clean_movies

        WHERE

        original_language='hi'

        AND genres LIKE ?

        AND vote_count >= 20

        AND vote_average >= 5.8

        AND release_date >= '1995-01-01'

        ORDER BY

        release_date DESC,

        popularity DESC,

        vote_count DESC,

        vote_average DESC

        LIMIT ?
        """

        df = pd.read_sql(
            query,
            conn,
            params=(f"%{genre}%", limit)
        )

    else:

        query = """
        SELECT *

        FROM clean_movies

        WHERE

        original_language='en'

        AND genres LIKE ?

        AND vote_count >= 300

        AND popularity >= 10

        AND imdb_rating >= 6

        AND vote_average >= 6.3

        AND release_date >= '2005-01-01'

        AND title NOT LIKE '%WWE%'
        AND title NOT LIKE '%RAW%'
        AND title NOT LIKE '%SmackDown%'
        AND title NOT LIKE '%Royal Rumble%'
        AND title NOT LIKE '%Season%'
        AND title NOT LIKE '%Episode%'
        AND title NOT LIKE '%Part %'

        ORDER BY

        release_date DESC,

        popularity DESC,

        vote_count DESC,

        vote_average DESC

        LIMIT ?
        """

        df = pd.read_sql(
            query,
            conn,
            params=(f"%{genre}%", limit)
        )

    conn.close()

    # =================================
# CREATE TABLES AUTOMATICALLY
# =================================

    create_history_table()
    create_user_table()

    return df.to_dict("records")