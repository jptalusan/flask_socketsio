from sockets import socketio
from flask_socketio import send, emit

@socketio.on('client_connected')
def handle_client_connect_event(json):
 print('received json: {0}'.format(str(json)))

@socketio.on('alert_button')
def handle_alert_event(json):
 print('Message from client was {0}'.format(json))
 emit('alert', 'Message from backend')

@socketio.on('message')
def handle_json_button(json):
 send(json, json=True)
 print('Sending {0} to all clients'.format(json))
