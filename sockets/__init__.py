#import eventlet
import json

from flask import Flask
from flask_socketio import SocketIO
from flask_mqtt import Mqtt
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from importlib import import_module
import logging

#eventlet.monkey_patch()

app = Flask(__name__, static_url_path='/static')
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)
socketio = SocketIO(app, async_mode="threading")
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

mqtt = Mqtt(app)
Camera = import_module('sockets.camera_pi').Camera

from sockets import views, websockets, models
