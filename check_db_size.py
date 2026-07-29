import sqlite3

conn = sqlite3.connect("database/movies.db")
cursor = conn.cursor()

cursor.execute("SELECT COUNT(*) FROM clean_movies")
print("Movies:", cursor.fetchone()[0])

cursor.execute("PRAGMA page_count;")
pages = cursor.fetchone()[0]

cursor.execute("PRAGMA page_size;")
page_size = cursor.fetchone()[0]

print("Pages:", pages)
print("Page Size:", page_size)
print("Database Size:", pages * page_size / 1024 / 1024, "MB")

conn.close()