import os
from time import sleep

import eventlet
from flask import render_template
from flask_socketio import emit

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
    net['lfw_path'] = app.config['FACE_NET_DATA']
    net['lfw'] = False
    net['output_path'] = app.config['FACE_NET_OUTPUT']
    net['output'] = False

    if os.path.isfile(net['landmarks_path']): net['landmarks'] = os.stat(net['landmarks_path'])
    if os.path.isdir(net['lfw_path']): net['lfw'] = os.stat(net['lfw_path'])
    if os.path.isdir(net['output_path']): net['output'] = os.stat(net['output_path'])

    return net



@sio.on('update')
#def handle_my_custom_event(json):
def handle_my_custom_event(sid, message):
    print(sid, message)
    #mgr.emit('my event', data={'foo': 'bar'})
    for i in range(5):
        mgr.emit('log', {'log':i, 'message': message['name'] + ': ' + str(i)})
        eventlet.sleep(1)