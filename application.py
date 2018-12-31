import os

from flask import Flask, session, render_template, jsonify, request, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import text
from sqlalchemy import or_
from models import *
import requests
import json


app = Flask(__name__)


# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/registration", methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        session['name'] = request.form.get("name")
        session['password'] = request.form.get("password")
        session['email'] = request.form.get("email")

    return render_template("registration.html")



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form['name'] in session['name'] and request.form['password'] in session['password']:
            name = session['name']
            return render_template("login.html", name=name)
        return "You are not logged in <br><a href ='/login'></b>" + "Please log in</b></a>"
    return render_template("login_form.html")


@app.route("/logout")
def logout():
    session.clear()
    return render_template("logout.html")



@app.route("/search", methods=["GET", "POST"])
def search():
    if 'name' in session:
        if request.method == "POST":
            try:
                book_search = request.form.get("search")
                if not book_search:
                    return "please type a book name!"

                books = db.execute("SELECT * FROM books WHERE title LIKE :book_search OR isbn LIKE :book_search OR author LIKE :book_search", {"book_search": '%'+book_search+'%'}).fetchall()

                return render_template("search_result.html", books=books)

            except ValueError:
                return render_template("error.html", message="Please type a valid entry")

        return render_template("search.html")
    return render_template("not_logged_in.html")


@app.route("/book/<int:id>", methods=["GET", "POST"])
def book(id):

    # Get a single book details
    book = db.execute("SELECT * FROM books WHERE id = :id", {"id": id}).fetchone()

    # User ratings and review
    session['rating'] = request.form.get("rating")
    session['review'] = request.form.get("review")

    # User ratings and review save in variables
    rating = session['rating']
    review = session['review']

    return render_template("result_detail.html", book=book, rating=rating, review=review)


@app.route("/goodreads/<isbn>")
def goodreads(isbn):

    # data extracts from goodreads API
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "xewTe1pz8hTMGFYsRSJkA", "isbns": isbn})
    data = res.json()
    return render_template("api_data.html", data=data)



@app.route("/api/<isbn>")
def api(isbn):

    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    if book is None:
        return jsonify({"Error": "Invalid book isbn"}), 404

    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "Cdjuz7jTYIwy5Jj9GhY9sw", "isbns": isbn})

    average_rating=res.json()['books'][0]['average_rating']
    work_ratings_count=res.json()['books'][0]['work_ratings_count']

    return jsonify({
            "title": book.title,
            "isbn": book.isbn,
            "publication year": book.year,
            "author": book.author,
            "review_count": work_ratings_count,
            "average_score": average_rating
            })
