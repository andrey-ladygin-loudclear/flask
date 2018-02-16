from flask import flash
from flask import redirect
from flask import render_template
from flask import request
from flask import session

from app import app
from acme.auth import Auth
from acme.url import URL
from models.recipe import Recipe


@app.route('/')
@app.route('/<int:page>',methods=['GET'])
def dashboard(page=1):
    per_page = 10
    recipes = Recipe.query.order_by(Recipe.id.desc()).paginate(page,per_page, error_out=False)
    return render_template('dashboard.html', recipes=recipes)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if Auth.check():
        return redirect('/')

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Auth.verify(email, password)

        if user:
            Auth.save(user)
            return redirect(URL.back())

        flash('Wrong email or password', 'danger')

    return render_template('auth/login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logget out', 'success')
    return redirect('/')