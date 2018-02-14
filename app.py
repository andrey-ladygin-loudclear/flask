from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = 'OUGAWD8T2yi3e2l39W^&*(D(%'
app.config.from_pyfile('config.cfg')
db = SQLAlchemy(app)

from routes.dashboard import *
from routes.receipt import *
from routes.user import *
import commands

if __name__ == "__main__":
    app.run(debug=True)
