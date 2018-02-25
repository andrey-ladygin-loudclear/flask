from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os.path import abspath, dirname

APP_PATH = dirname(abspath(__file__))

app = Flask(__name__)
app.secret_key = 'OUGAWD8T2yi3e2l39W^&*(D(%'
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)

from routes.dashboard import *
from routes.receipt import *
from routes.user import *
import commands

if __name__ == "__main__":
    app.jinja_env.auto_reload = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True, host='0.0.0.0')
