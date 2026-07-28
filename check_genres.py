import sqlite3
import pandas as pd

conn = sqlite3.connect("database/movies.db")

df = pd.read_sql("""
SELECT
title,
genres
FROM clean_movies
LIMIT 20
""", conn)

print(df)

conn.close()