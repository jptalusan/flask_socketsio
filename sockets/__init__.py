import eventlet
import json
import os

from flask import Flask
from flask_socketio import SocketIO
from flask_mqtt import Mqtt
#from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

eventlet.monkey_patch()
db = SQLAlchemy()
mqtt = Mqtt()
socketio = SocketIO()
migrate = Migrate()
def create_app(config_name):
    app = Flask(__name__, static_url_path='/static')
    socketio.init_app(app)

    cfg = os.path.join(os.getcwd(), 'config', config_name + '.py')
    app.config.from_pyfile(cfg)
    db.init_app(app)
    migrate.init_app(app, db)

    mqtt.init_app(app)
    from sockets.views import route_blueprint
    app.register_blueprint(route_blueprint)

    #from sockets import views, websockets, models
    return app
