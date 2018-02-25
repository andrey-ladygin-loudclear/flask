import datetime

from os.path import join

from flask import url_for

from app import db, APP_PATH


#https://docs.pylonsproject.org/projects/pyramid_cookbook/en/latest/database/sqlalchemy.html#importing-all-sqlalchemy-models


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    email = db.Column(db.String(255))
    password = db.Column(db.String(100))
    created_at = db.Column(db.Date, default=datetime.datetime.now)
    recipes = db.relationship('Recipe', backref='author', lazy='dynamic')
    profile_images = db.relationship('ProfileImages', lazy='dynamic')

    def get_resource(self, filename = '', static = False, absolute = False):
        if absolute: return join(APP_PATH, 'static', 'resources', 'users', str(self.id), filename)
        if static: return join('static', 'resources', 'users', str(self.id), filename)
        return join('resources', 'users', str(self.id), filename)


class ProfileImages(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    src = db.Column(db.String(100))
    preprocessed_src = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship("User", backref="images")
