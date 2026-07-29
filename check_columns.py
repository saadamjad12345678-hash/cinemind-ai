import sqlite3
import pandas as pd

conn = sqlite3.connect("database/movies.db")

df = pd.read_sql("SELECT * FROM clean_movies LIMIT 5", conn)

print(df.columns.tolist())

conn.close()