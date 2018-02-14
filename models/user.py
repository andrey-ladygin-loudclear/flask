import datetime

from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(255))
    password = db.Column(db.String(100))
    created_at = db.Column(db.Date, default=datetime.datetime.now)
    recipes = db.relationship('Recipe', backref='author', lazy='dynamic') #TODO: optimize relation query