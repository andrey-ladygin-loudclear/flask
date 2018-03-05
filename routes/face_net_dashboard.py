import tarfile
import urllib.request
import os
from time import sleep

import eventlet
from flask import render_template
from flask_socketio import emit

from acme.Networks.FaceNet.download_and_extract_model import download_and_extract_model
from acme.Networks.FaceNet.preprocess import preprocess
from app import app, socketio, sio, mgr
from acme.auth import Auth, is_logged_in
from acme.url import URL, absolute

@app.route('/face_net_dashboard', methods=['GET', 'POST'])
@is_logged_in
def face_net_dashboard():
    return render_template('admin/face_net_dashboard.html', user=Auth.user(), net=get_face_net_info())


def get_face_net_info():
    net = {}
    net['landmarks_path'] = absolute(app.config['FACE_NET_LANDMARKS'])
    net['landmarks'] = False
    net['lfw_path'] = absolute(app.config['FACE_NET_DATA'])
    net['lfw'] = False
    net['output_path'] = absolute(app.config['FACE_NET_OUTPUT'])
    net['output'] = False

    if os.path.isdir(net['landmarks_path']): net['landmarks'] = sizeof_fmt(get_size(net['landmarks_path']))
    if os.path.isdir(net['lfw_path']): net['lfw'] = sizeof_fmt(get_size(net['lfw_path']))
    if os.path.isdir(net['output_path']): net['output'] = sizeof_fmt(get_size(net['output_path']))

    return net



@sio.on('update')
def update_request(sid, message):
    print(sid, message)
    name = message['name']

    if name == 'landmarks': update_landmark()
    if name == 'lfw': update_lfw()
    if name == 'output': update_callout()
    if name == 'prediction': make_tests()


def update_landmark():
    mgr.emit('log-landmark', {'message': 'Start updating...'})
    download_and_extract_model('20170511-185253', absolute(app.config['FACE_NET_LANDMARKS']))
    mgr.emit('log-landmark', {'message': 'Done'})
    size = sizeof_fmt(get_size(absolute(app.config['FACE_NET_LANDMARKS'])))
    mgr.emit('finish-landmark', size)

def update_lfw():
    mgr.emit('log-lfw', {'message': 'Start downloading...'})
    archive = absolute(app.config['FACE_NET_DATA']) + '.tar.gz'
    data = absolute(app.config['FACE_NET_DATA'])
    urllib.request.urlretrieve(app.config['FACE_NET_LWF_URL'], archive)
    mgr.emit('log-lfw', {'message': 'Extracting...'})
    os.makedirs(data, exist_ok=True)
    tar = tarfile.open(archive, "r:gz")
    tar.extractall(data)
    tar.close()
    os.remove(archive)
    mgr.emit('log-lfw', {'message': 'Done'})
    size = sizeof_fmt(get_size(data))
    mgr.emit('finish-lfw', size)

def update_callout():
    mgr.emit('log-callout', {'message': 'Start updating...'})
    output_dir = absolute(app.config['FACE_NET_OUTPUT'])
    preprocess(absolute(app.config['FACE_NET_DATA']), output_dir, 180)
    mgr.emit('log-callout', {'message': 'Done'})
    size = sizeof_fmt(get_size(output_dir))
    mgr.emit('finish-lfw', size)

def make_tests():
    pass

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