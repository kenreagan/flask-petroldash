import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY='vhvsdbjbdsfobuoabfubauos;hfuobgweiu'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    UPLOAD_FOLDER = './src/static/images/'
    SQLALCHEMY_DATABASE_URI = 'sqlite:////' + os.path.join(basedir, 'main.sqlite')
    MIGRATE = '.'

class TestingConfig(object):
    TESTING = True
    DEBUG=True
    SQLALCHEMY_DATABASE_URI = 'sqlite:////' + os.path.join(basedir, 'test.sqlite')
