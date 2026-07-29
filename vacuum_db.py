import sqlite3

conn = sqlite3.connect("database/movies.db")

print("Running VACUUM...")

conn.execute("VACUUM")

conn.close()

print("Done!")