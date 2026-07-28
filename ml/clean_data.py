import sqlite3
import pandas as pd

print("Loading database...")

conn = sqlite3.connect("database/movies.db")

df = pd.read_sql("SELECT * FROM movies", conn)

print("Original Movies :", len(df))

# -----------------------------
# Remove Duplicate Movies
# -----------------------------

df.drop_duplicates(subset=["title"], inplace=True)

# -----------------------------
# Remove Missing Values
# -----------------------------

important_columns = [
    "title",
    "overview",
    "genres",
    "cast",
    "director",
    "keywords",
    "poster_path"
]

df.dropna(subset=important_columns, inplace=True)

# -----------------------------
# Remove Empty Strings
# -----------------------------

for col in important_columns:
    df = df[df[col].astype(str).str.strip() != ""]

# -----------------------------
# Keep Good Movies Only
# -----------------------------

df = df[df["imdb_rating"] >= 4.5]

df = df[df["vote_count"] >= 20]

# -----------------------------
# Remove Adult Movies
# -----------------------------

adult_keywords = [
    "porn",
    "sex",
    "adult",
    "erotic",
    "xxx"
]

pattern = "|".join(adult_keywords)

df = df[
    ~df["genres"].str.lower().str.contains(pattern, na=False)
]

# -----------------------------
# Remove Unnecessary Columns
# -----------------------------

keep_columns = [
    "id",
    "title",
    "overview",
    "genres",
    "cast",
    "director",
    "keywords",
    "poster_path",
    "release_date",
    "vote_average",
    "vote_count",
    "imdb_rating",
    "popularity",
    "original_language"
]

df = df[keep_columns]

print("Movies After Cleaning :", len(df))

# -----------------------------
# Save Clean Dataset
# -----------------------------

df.to_sql(
    "clean_movies",
    conn,
    if_exists="replace",
    index=False
)

conn.commit()

conn.close()

print("===================================")
print("Cleaning Completed Successfully!")
print("Table Name : clean_movies")
print("===================================")