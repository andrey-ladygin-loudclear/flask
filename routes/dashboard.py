import base64
import tempfile

import os
import uuid

import cv2
import numpy as np
from PIL import Image
from flask import flash, json, url_for
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from io import BytesIO, StringIO

from os.path import join

from acme.utils import get_tmp_image_from_base64, save_image_from_base64
from app import app, db, APP_STATIC, face_net_instance
from acme.auth import Auth, is_logged_in
from acme.url import URL, resource, static
from models.recipe import Recipe
from models.user import ProfileImages, User


@app.route('/')
@app.route('/<int:page>',methods=['GET'])
def dashboard(page=1):
    print(APP_STATIC)
    p = join(APP_STATIC, 'users/resources/1', 'images')
    print(url_for('static', filename=p))

    per_page = 10
    recipes = Recipe.query.order_by(Recipe.id.desc()).paginate(page, per_page, error_out=False)
    return render_template('dashboard.html', recipes=recipes)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if Auth.check():
        return redirect('/')

    if request.method == 'POST':

        email = request.form['email']

        if request.form['face_photo']:
            jpg = get_tmp_image_from_base64(request.form['face_photo'])
            preprocessed_image = face_net_instance.process_image(jpg.name, 180)
            if preprocessed_image is not None:
                Auth.verify_by_image(email, preprocessed_image)
            else:
                flash('Please, put your face straight at the webcam!', 'danger')
        else:
            password = request.form['password']
            user = Auth.verify(email, password)

            if user:
                Auth.save(user)
                flash('Hi {} {}'.format(user.first_name, user.last_name), 'success')
                return redirect(URL.back())

            flash('Wrong email or password', 'danger')

    return render_template('auth/login.html')


@app.route('/registration', methods=['GET', 'POST'])
def registration():
    user_form = {}

    if request.method == 'POST':
        valid = True
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        user_form = request.form

        if password != request.form['confirm_password']:
            valid = False
            flash('Please confirm your password', 'danger')

        if valid:
            user = User(first_name=first_name, last_name=last_name, email=email, password=Auth.crypt_password(password))
            db.session.add(user)
            db.session.commit()
            Auth.save(user)
            return redirect('/')


    return render_template('auth/registration.html', user_form=user_form)

@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logget out', 'success')
    return redirect('/')

@app.route('/profile', methods=['GET', 'POST'])
@is_logged_in
def profile():
    if request.method == 'POST':
        pass
    print('AUTH USER', Auth.user())
    return render_template('auth/profile.html', user=Auth.user())

@app.route('/upload_profile_image', methods=['POST'])
@is_logged_in
def upload_profile_image():
    if request.method == 'POST':
        user = Auth.user()
        image = save_image_from_base64(request.form['fileToUpload'], user.get_profile_images_dir())

        preprocessed_image = face_net_instance.process_image(image.filename, 180)

        if preprocessed_image is not None:
            profile_images = ProfileImages(src=filename, user_id=Auth.user().id)
            db.session.add(profile_images)
            db.session.commit()
            try:
                user_wights = np.load(user.get_profile_images_weights() + '.npy')
                np.append(user_wights, {profile_images.id: preprocessed_image})
            except FileNotFoundError:
                user_wights = {profile_images.id: preprocessed_image}
            np.save(user.get_profile_images_weights(), user_wights)

            return json.dumps({
                'success': True,
                'path': static(path)
            })
    return json.dumps({
        'success': False
    })