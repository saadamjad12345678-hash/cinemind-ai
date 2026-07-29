from flask import Flask, render_template, request
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

from utils.database import (
    save_user,
    save_history,
    get_history,
    get_trending_movies,
    get_movies_by_genre
)

from utils.movie_service import (
    search_movie,
    get_movie_details,
    get_movie_trailer,
    get_movie_cast
    
)

from ml.recommender import recommend


import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)
""")

conn.commit()
conn.close()


app = Flask(__name__)

app.secret_key = "cinemind_ai_secret_key"

@app.route("/", methods=["GET", "POST"])
def home():

    if "user" not in session:
        return redirect(url_for("login"))

    movie = None
    movie_data = None
    recommended_movies = []

    

    history = []

    
    
    trending_hollywood = get_trending_movies("en", 20)
    trending_bollywood = get_trending_movies("hi", 20)

    if request.method == "POST":

        movie = request.form["movie"]

        movie_data = search_movie(movie)

        if movie_data:

            df = recommend(
                movie_data["title"],
                top_n=20
            )

            recommended_movies = df.to_dict("records")

       

    return render_template(
        "index.html",
        user=session["user"],
        movie=movie,
        movie_data=movie_data,
        trending_hollywood=trending_hollywood,
        trending_bollywood=trending_bollywood,
        recommended_movies=recommended_movies,
        history=history
    )

@app.route("/genre", methods=["POST"])
def genre():

    if "user" not in session:
        return redirect(url_for("login"))

    language = request.form["language"]
    genre = request.form["genre"]

    movies = get_movies_by_genre(
        language,
        genre,
        20
    )

    print("Language:", language)
    print("Genre:", genre)

    return render_template(
        "genre.html",
        movies=movies,
        genre=genre,
        language=language,
        user=session["user"]
    )

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        # Check if email already exists
        cursor.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,)
        )

        existing_user = cursor.fetchone()

        if existing_user:
            conn.close()
            return "❌ Email already exists."

        cursor.execute(
            "INSERT INTO users(name, email, password) VALUES(?,?,?)",
            (name, email, password)
        )

        conn.commit()
        conn.close()

        return redirect(url_for("login"))

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, password)
        )

        user = cursor.fetchone()

        conn.close()

        if user:

            session["user"] = user[1]      # name
            session["gmail"] = user[2]     # email

            save_user(user[2])

            return redirect(url_for("home"))

        return "❌ Invalid Email or Password"

    return render_template("login.html")

@app.route("/movie/<int:movie_id>")
def movie_details(movie_id):

    if "user" not in session:
        return redirect(url_for("login"))

    # TMDB se movie details
    movie = get_movie_details(movie_id)

    # Trailer
    trailer = get_movie_trailer(movie_id)

    # Cast
    cast = get_movie_cast(movie_id)

    if not movie or "title" not in movie:
        return "Movie Not Found"

    # -----------------------------
    # Save Watch History
    # -----------------------------
    gmail = session.get("gmail")

    if gmail:
        save_history(gmail, movie_id)

    # -----------------------------
    # AI Recommendations
    # -----------------------------
    recommendations = recommend(
        movie["title"],
        top_n=20
    )

    if recommendations is None:
        recommendations = []

    elif hasattr(recommendations, "to_dict"):
        recommendations = recommendations.to_dict("records")

    return render_template(
        "movie_details.html",
        trailer=trailer,
        cast=cast,
        movie=movie,
        recommendations=recommendations
    )

@app.route("/logout")
def logout():

    session.pop("user", None)

    return redirect(url_for("login"))

 
if __name__ == "__main__":
    app.run(debug=True)

