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

#from acme.Networks.FaceNet.preprocess import _process_image
from app import app, db, APP_STATIC
from acme.auth import Auth, is_logged_in
from acme.url import URL
from models.recipe import Recipe
from models.user import ProfileImages


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

@app.route('/profile', methods=['GET', 'POST'])
@is_logged_in
def profile():
    if request.method == 'POST':
        pass
    return render_template('auth/profile.html', user=Auth.user())

@app.route('/upload_profile_image', methods=['POST'])
@is_logged_in
def upload_profile_image():
    if request.method == 'POST':
        user = Auth.user()
        img_data = request.form['fileToUpload']
        filename = str(uuid.uuid4()) + '.jpeg'
        os.makedirs(user.profile_images_dir)
        path = join(user.profile_images_dir, filename)
        img_data = img_data.replace('data:image/jpeg;base64', '')
        image_bytes = BytesIO(base64.b64decode(img_data))
        image = Image.open(image_bytes)
        image.save(path)

        preprocessed_image = _process_image(path, 180)

        if preprocessed_image is not None:
            profile_images = ProfileImages(src=filename, user_id=Auth.user().id)
            db.session.add(profile_images)
            db.session.commit()
            user_wights = np.load(user.profile_images_weights + '.npy')
            user_wights[profile_images.id] = preprocessed_image
            np.save(user.profile_images_weights, user_wights)

            return json.dumps({
                'success': True,
                'path': user.get_resource(filename=filename, static=True)
            })
    return json.dumps({
        'success': False
    })