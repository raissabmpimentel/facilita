import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    DEBUG = True
    SECRET_KEY = '28f107fb0626ad3488b8f7a4437ab21e0acae7be'
    SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
