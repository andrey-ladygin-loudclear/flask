import bz2
import os
import tarfile
import urllib.request

import numpy as np
from flask import render_template

from acme.Networks.FaceNet.download_and_extract_model import download_and_extract_model
from acme.Networks.FaceNet.test_classifier import get_emmbedings
from acme.auth import Auth, is_logged_in
from acme.url import absolute
from app import app, face_net_instance, socketio_app


@app.route('/face_net_dashboard', methods=['GET', 'POST'])
@is_logged_in
def face_net_dashboard():
    return render_template('admin/face_net_dashboard.html', user=Auth.user(), net=get_face_net_info())


def get_face_net_info():
    net = {}
    net['landmarks_path'] = absolute(app.config['FACE_NET_LANDMARKS_FILE'])
    net['model_path'] = absolute(app.config['FACE_NET_WEIGHTS_DIR'])
    net['lfw_path'] = absolute(app.config['FACE_NET_DATA_DIR'])
    net['output_path'] = absolute(app.config['FACE_NET_OUTPUT_DIR'])
    net['landmarks'] = False
    net['model'] = False
    net['lfw'] = False
    net['output'] = False

    if os.path.isfile(net['landmarks_path']): net['landmarks'] = sizeof_fmt(os.path.getsize(net['landmarks_path']))
    if os.path.isdir(net['lfw_path']): net['lfw'] = sizeof_fmt(get_size(net['lfw_path']))
    if os.path.isdir(net['output_path']): net['output'] = sizeof_fmt(get_size(net['output_path']))
    if os.path.isdir(net['model_path']): net['model'] = sizeof_fmt(get_size(net['model_path']))

    return net


@socketio_app.on('update')
def update_request(message):
    print('Receive', message)
    name = message['name']

    try:
        if name == 'landmarks': update_landmark()
        if name == 'model': update_model()
        if name == 'lfw': update_lfw()
        if name == 'output': update_callout()
        if name == 'prediction': make_tests()
    except Exception as e:
        socketio_app.emit('finish-' + str(name), {'error': "{}: {}".format(type(e).__name__, str(e))})
        raise e


def update_model():
    socketio_app.emit('log-model', {'message': 'Start updating...'})
    download_and_extract_model('20170511-185253', absolute(app.config['FACE_NET_WEIGHTS_DIR']))
    socketio_app.emit('log-model', {'message': 'Done'})
    size = sizeof_fmt(get_size(absolute(app.config['FACE_NET_WEIGHTS_DIR'])))
    socketio_app.emit('finish-model', {'size': size})


def update_landmark():
    socketio_app.emit('log-landmark', {'message': 'Start downloading...'})
    file = absolute(app.config['FACE_NET_LANDMARKS_FILE'])
    archive = file + '.bz2'
    urllib.request.urlretrieve(app.config['FACE_NET_LANDMARKS_URL'], archive)
    socketio_app.emit('log-landmark', {'message': 'Extracting...'})

    with open(file, 'wb') as new_file, bz2.BZ2File(archive, 'rb') as bz2_file:
        for bytes in iter(lambda : bz2_file.read(100 * 1024), b''):
        #for bytes in file.read():
            new_file.write(bytes)

    os.remove(archive)
    socketio_app.emit('log-landmark', {'message': 'Done'})
    size = sizeof_fmt(os.path.getsize(file))
    socketio_app.emit('finish-landmark', {'size': size})


def update_lfw():
    socketio_app.emit('log-lfw', {'message': 'Start downloading...'})
    archive = absolute(app.config['FACE_NET_DATA_DIR']) + '.tar.gz'
    data = absolute(app.config['FACE_NET_DATA_DIR'])
    urllib.request.urlretrieve(app.config['FACE_NET_LWF_URL'], archive)
    socketio_app.emit('log-lfw', {'message': 'Extracting...'})
    os.makedirs(data, exist_ok=True)
    tar = tarfile.open(archive, "r:gz")
    tar.extractall(data)
    tar.close()
    os.remove(archive)
    socketio_app.emit('log-lfw', {'message': 'Done'})
    size = sizeof_fmt(get_size(data))
    socketio_app.emit('finish-lfw', {'size': size})


def update_callout():
    socketio_app.emit('log-callout', {'message': 'Start updating...'})
    output_dir = absolute(app.config['FACE_NET_OUTPUT'])
    preprocess(absolute(app.config['FACE_NET_DATA']), output_dir, 180)
    socketio_app.emit('log-callout', {'message': 'Done'})
    size = sizeof_fmt(get_size(output_dir))
    socketio_app.emit('finish-lfw', {'size': size})


def make_tests():
    print('make_tests')
    crop_dim = 180
    im1 = '/home/srivoknovski/Python/flask/acme/Networks/FaceNet/data/lfw/Aaron_Peirsol/Aaron_Peirsol_0002.jpg'
    im2 = '/home/srivoknovski/Python/flask/acme/Networks/FaceNet/data/lfw/Aaron_Peirsol/Aaron_Peirsol_0004.jpg'
    im3 = '/home/srivoknovski/Python/flask/acme/Networks/FaceNet/data/lfw/Aaron_Tippin/Aaron_Tippin_0001.jpg'

    images = []
    images.append(face_net_instance.process_image(im1, crop_dim))
    images.append(face_net_instance.process_image(im2, crop_dim))
    images.append(face_net_instance.process_image(im3, crop_dim))

    model_path = absolute(app.config['FACE_NET_WEIGHTS_FILE'])
    embs = get_emmbedings(images=images, model_path=model_path)

    diff1 = np.linalg.norm(embs[0] - embs[1])
    diff2 = np.linalg.norm(embs[0] - embs[2])

    print(im1, im2, np.linalg.norm(embs[0] - embs[1]))
    print(im1, im3, np.linalg.norm(embs[0] - embs[2]))
    message = 'The same persons: {}, The different persons: {}'.format(diff1, diff2)
    socketio_app.emit('finish-lfw', {'message': message})


def get_size(start_path = '.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)