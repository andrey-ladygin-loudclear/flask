from functools import wraps

from app import app
from flask import Response
from flask import flash
from flask import redirect
from flask import session
from flask import url_for, g
from passlib.handlers.sha2_crypt import sha256_crypt

from models.user import User


class Auth:
    current_user = None

    @staticmethod
    def check():
        return 'user_id' in session

    @staticmethod
    def verify(email, password):
        user = User.query.filter_by(email=email).first()

        if user and sha256_crypt.verify(password, user.password):
            return user

        return False

    @staticmethod
    def save(user):
        session['logged_in'] = True
        session['user_id'] = user.id

    @staticmethod
    def crypt_password(password):
        return sha256_crypt.encrypt(password)

    @staticmethod
    def user():
        if 'user_id' in session:
            if Auth.current_user:
                return Auth.current_user

            Auth.current_user = User.query.filter_by(id=session['user_id']).first()
            return Auth.current_user

        return False

app.add_template_global(Auth, name='Auth')

def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwards):
        if Auth.check():
            return f(*args, **kwards)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap