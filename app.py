import logging
from tempfile import mkdtemp
import eventlet
from flask_socketio import SocketIO
from acme.Networks.FaceNet.face_net import FaceNet

try:
    eventlet.monkey_patch()
except Exception as e:
    print(str(e))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os.path import abspath, dirname, join, isfile

APP_PATH = dirname(abspath(__file__))
APP_STATIC = join(APP_PATH, 'static')
APP_URL = '/'

app = Flask(__name__)
app.secret_key = 'OW^U8(DT2yi3e(GAWD2l39&*%'
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)
logging.getLogger().setLevel(logging.INFO)


app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_FILE_DIR"] = mkdtemp()

#mgr = socketio.KombuManager('redis://172.96.50.3', write_only=True)
#sio = socketio.Server(client_manager=mgr)
socketio_app = SocketIO(app, message_queue='redis://172.96.50.3')

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

    #default run application
    #app.run(debug=True, host='127.0.0.1')

    #run application with flask_socketio
    socketio_app.run(app, host='0.0.0.0', port=8000)#0.0.0.0 for docker binding

    # wrap Flask application with socketio's middleware
    #app = socketio.Middleware(sio, app)

    # deploy as an eventlet WSGI server
    #eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
