import pandas as pd
import sqlite3

print("Loading CSV...")

df = pd.read_csv("clean_movies_fixed.csv")

print("Original:", len(df))

# Remove duplicate movies
df = df.drop_duplicates(subset="id")

# Remove unnecessary columns
remove_columns = [
    "homepage",
    "tagline",
    "status",
    "spoken_languages",
    "production_companies",
    "production_countries"
]

for col in remove_columns:
    if col in df.columns:
        df.drop(columns=col, inplace=True)

# Fill missing values
df.fillna("", inplace=True)

print("Saving optimized database...")

conn = sqlite3.connect("database/movies.db")

df.to_sql(
    "clean_movies",
    conn,
    if_exists="replace",
    index=False
)

conn.close()

print("Done!")
print("Movies:", len(df))