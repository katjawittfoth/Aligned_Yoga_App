import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.urandom(24)
    Q = 'sqlite:///' + os.path.join(basedir, 'aligned.db')
    SQLALCHEMY_DATABASE_URI = Q
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    UPLOAD_FOLDER = './uploads'
