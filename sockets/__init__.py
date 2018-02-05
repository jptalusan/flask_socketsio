import eventlet
import json

from flask import Flask
from flask_socketio import SocketIO
from flask_mqtt import Mqtt
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

eventlet.monkey_patch()

app = Flask(__name__, static_url_path='/static')
socketio = SocketIO(app)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

mqtt = Mqtt(app)

from sockets import views, websockets, models
