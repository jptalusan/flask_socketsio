import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    MQTT_BROKER_URL = os.environ.get('MQTT_BROKER_URL') or '163.221.68.224'
    MQTT_BROKER_PORT = os.environ.get('MQTT_BROKER_PORT') or 1883
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = 'sockets/uploads'