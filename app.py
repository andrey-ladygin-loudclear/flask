import eventlet
from gevent import monkey
monkey.patch_all()

from flask import Flask
#from flask_socketio import SocketIO
import socketio
from flask_sqlalchemy import SQLAlchemy
from os.path import abspath, dirname, join

APP_PATH = dirname(abspath(__file__))
APP_STATIC = join(APP_PATH, 'static')
APP_URL = '/'

app = Flask(__name__)
app.secret_key = 'OUGAWD8T2yi3e2l39W^&*(D(%'
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)
sio = socketio.Server()
#sio = socketio.AsyncServer(async_mode='sanic')
#sio.attach(app)
#socketio = SocketIO(app, message_queue='redis://127.0.0.1')

#sio = socketio.Server(async_mode='threading')
#app.wsgi_app = socketio.Middleware(sio, app.wsgi_app)

from routes.dashboard import *
from routes.receipt import *
from routes.user import *
from routes.face_net_dashboard import *
import commands

if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    #socketio.run(app)
    #app.run(debug=True, host='127.0.0.1', threaded=True)
    # wrap Flask application with socketio's middleware
    app = socketio.Middleware(sio, app)

    # deploy as an eventlet WSGI server
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
