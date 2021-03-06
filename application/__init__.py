import os
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_heroku import Heroku
from sqlalchemy import create_engine, and_, text
from sqlalchemy.orm import sessionmaker


app = Flask(__name__)
app.config['SECRET_KEY'] = '28f107fb0626ad3488b8f7a4437ab21e0acae7be'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['DEBUG'] = True
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
heroku = Heroku(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


from application import routes, models
