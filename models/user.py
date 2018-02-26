import datetime

from os.path import join

from flask import url_for

from app import db, APP_PATH, APP_STATIC


#https://docs.pylonsproject.org/projects/pyramid_cookbook/en/latest/database/sqlalchemy.html#importing-all-sqlalchemy-models


class User(db.Model):
    profile_images_dir = join(APP_STATIC, 'users', str(id), 'images')
    profile_images_weights = join(APP_STATIC, 'users', str(id))

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(255))
    password = db.Column(db.String(100))
    created_at = db.Column(db.Date, default=datetime.datetime.now)
    recipes = db.relationship('Recipe', backref='author', lazy='dynamic')
    profile_images = db.relationship('ProfileImages', lazy='dynamic')


class ProfileImages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    src = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", backref="images")
