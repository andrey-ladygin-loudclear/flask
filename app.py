import eventlet
from flask_socketio import SocketIO
from gevent import monkey

from acme.Networks.FaceNet.face_net import FaceNet

monkey.patch_all()
eventlet.monkey_patch()

from flask import Flask
import socketio
from flask_sqlalchemy import SQLAlchemy
from os.path import abspath, dirname, join, isfile
import engineio.async_gevent

APP_PATH = dirname(abspath(__file__))
APP_STATIC = join(APP_PATH, 'static')
APP_URL = '/'

app = Flask(__name__)
app.secret_key = 'OUGAWD8T2yi3e2l39W^&*(D(%'
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)

mgr = socketio.KombuManager('redis://', write_only=True)
sio = socketio.Server(client_manager=mgr)

face_net_instance = FaceNet()
if isfile(join(APP_PATH, app.config['FACE_NET_LANDMARKS_FILE'])):
    face_net_instance.set_align_dlib_path(join(APP_PATH, app.config['FACE_NET_LANDMARKS_FILE']))


from routes.dashboard import *
from routes.receipt import *
from routes.user import *
from routes.face_net_dashboard import *
import commands

if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    #app.run(debug=True, host='127.0.0.1')
    #socketio_app = SocketIO(app)
    #socketio_app.run(app)

    # wrap Flask application with socketio's middleware
    app = socketio.Middleware(sio, app)

    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
