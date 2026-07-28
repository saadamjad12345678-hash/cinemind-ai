import sqlite3
import pandas as pd

# ===========================
# CSV File Path
# ===========================

CSV_PATH = r"C:\Users\Shahzad Abid\Downloads\archive\TMDB_all_movies.csv"

# ===========================
# Read CSV
# ===========================

print("Loading dataset...")

df = pd.read_csv(CSV_PATH)

print("Dataset Loaded Successfully!")
print("Total Movies:", len(df))

# ===========================
# Create Database
# ===========================

conn = sqlite3.connect("database/movies.db")

print("Database Connected!")

# ===========================
# Save CSV into SQLite
# ===========================

df.to_sql(
    "movies",
    conn,
    if_exists="replace",
    index=False
)

conn.commit()
conn.close()

print("===================================")
print("Movies Imported Successfully!")
print("Database Saved -> database/movies.db")
print("===================================")