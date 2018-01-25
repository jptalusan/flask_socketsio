import eventlet
import json

from flask import Flask
from flask_socketio import SocketIO
from flask_mqtt import Mqtt

eventlet.monkey_patch()

app = Flask(__name__)
socketio = SocketIO(app)
app.config['MQTT_BROKER_URL'] = '163.221.68.234'
app.config['MQTT_BROKER_PORT'] = 1883

mqtt = Mqtt(app)

from sockets import views, websockets
