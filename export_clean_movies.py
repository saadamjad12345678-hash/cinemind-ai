import sqlite3
import pandas as pd

conn = sqlite3.connect("database/movies.db")

df = pd.read_sql("SELECT * FROM clean_movies", conn)

df.to_csv("clean_movies.csv", index=False)

conn.close()

print("Done!")
print("Rows:", len(df))