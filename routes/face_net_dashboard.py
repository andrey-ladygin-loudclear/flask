import os
from time import sleep

from flask import render_template
from flask_socketio import emit

from app import app, socketio, sio
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
async def my_custom_event(arg1, arg2):
    print('arg1', arg1)
    print('arg2', arg2)
    sio.emit('logggged', {'name':123123123})
    # sio.emit('log', {'name':123123123})
    return "OK", 123

@sio.on('update old')
def handle_my_custom_event(arg1, arg2):
    print(arg1, arg2)
    emit('logggged', 'tetetetete')
    return
    print(json['name'])
    for i in range(10):
        #send(json['name'] + ', ' + str(i))
        emit('log', {'log':i, 'name':json['name']})
        #emit('log', {'log':i, 'name':json['name']})
        sleep(1)