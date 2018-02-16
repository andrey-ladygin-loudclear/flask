from flask import render_template
from flask import request

from acme.auth import is_logged_in
from app import app
from models.user import User


@app.route('/user/<int:id>',methods=['GET'])
def user(id):
    user = User.query.filter_by(id=id).first()
    return render_template('users/show.html', user=user)


@app.route('/user/edit/<int:id>',methods=['GET', 'POST'])
@is_logged_in
def edit_user(id):
    user = User.query.filter_by(id=id).first()

    if request.method == 'POST':
        pass # update user

    return render_template('users/edit.html', user=user)