import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "user"
    name = db.Column(db.String, nullable=False, primary_key=True)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False)

    def add_review(self, comment):
        c = Reviews(comment=comment, name=self.name)
        db.session.add(c)
        db.session.commit()


class Books(db.Model):
    __tablename__="books"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    isbn = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    year = db.Column(db.CHAR(4), nullable=False)


class Reviews(db.Model):
    __tablename__="reviews"
    reviewer = db.Column(db.String, primary_key=True, nullable=False)
    review = db.Column(db.String)
    rating = db.Column(db.Integer, nullable=False)

