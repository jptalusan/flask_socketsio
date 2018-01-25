import json
from sockets import socketio, mqtt
from flask_socketio import send, emit

datalist = []

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

@socketio.on('mqtt unsubscribe')
def handle_mqtt_unsubscribe(json_str):
    data = json.loads(json_str)
    mqtt.unsubscribe(data['topic'])

@socketio.on('mqtt_query_nodes')
def handle_mqtt_query_nodes(json_str):
    data = json.loads(json_str)
    mqtt.subscribe(data['topic'])
    mqtt.publish('slave/query/flask', 'query')
    global datalist
    datalist = []

@socketio.on('mqtt startMaster')
def handle_mqtt_unsubscribe(json_str):
    data = json.loads(json_str)
    mqtt.publish(data['topic'], data['payload'])

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload=message.payload.decode()
    )
    global datalist
    datalist.append(data['payload'])
    print('Message received via mqtt: {0}', format(data))
    print('current list: {0}', format(datalist))
    print(data['topic']) 
    if 'flask/query' in data['topic']:
        socketio.emit('mqtt_query_response', data=datalist)
    else:
        socketio.emit('mqtt_message', data=data)
