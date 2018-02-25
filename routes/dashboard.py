import base64
import tempfile

import os
import uuid

import cv2
#from PIL import Image
import numpy as np
from PIL import Image
from flask import flash, json
from flask import redirect
from flask import render_template
from flask import request
from flask import session
from io import BytesIO, StringIO

from acme.Networks.FaceNet.preprocess import _process_image
from app import app, db
from acme.auth import Auth, is_logged_in
from acme.url import URL
from models.recipe import Recipe
from models.user import ProfileImages


@app.route('/')
@app.route('/<int:page>',methods=['GET'])
def dashboard(page=1):
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
        os.makedirs(user.get_resource(absolute=True), exist_ok=True)
        path = user.get_resource(filename=filename, absolute=True)
        img_data = img_data.replace('data:image/jpeg;base64', '')
        image_bytes = BytesIO(base64.b64decode(img_data))
        image = Image.open(image_bytes)
        image.save(path)

        preprocessed_image = _process_image(path, 180)

        if preprocessed_image is not None:
            data_filename = str(uuid.uuid4())
            data_path = user.get_resource(filename=data_filename, absolute=True)
            np.save(data_path, preprocessed_image)
            profile_images = ProfileImages(src=filename, preprocessed_src=data_filename, user_id=Auth.user().id)
            db.session.add(profile_images)
            db.session.commit()

            return json.dumps({
                'success': True,
                'path': user.get_resource(filename=filename, static=True)
            })
    return json.dumps({
        'success': False
    })