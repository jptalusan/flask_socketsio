import json
from sockets import socketio, mqtt
from flask_socketio import send, emit

@socketio.on('client_connected')
def handle_client_connect_event(json):
    print('received json: {0}'.format(str(json)))

@socketio.on('alert_button')
def handle_alert_event(json):
    print('py: on alert')
    print('Message from client was {0}'.format(json))
    emit('alert', 'Message from backend')

@socketio.on('message')
def handle_json_button(json):
    print('py: on message')
    emit('my event', json)
    send(json, json=True)
    print('Sending {0} to all clients'.format(json))

@socketio.on('mqtt subscribe')
def handle_mqtt_subscribe(json_str):
    data = json.loads(json_str)
    mqtt.subscribe(data['topic'])

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    print('Message received via mqtt: {0}', format(data))
    socketio.emit('mqtt_message', data=data)
