import json
from sockets import socketio, mqtt
from flask_socketio import send, emit
import datetime
import time
import pickle
import sockets.real_time_object_detection
from flask import make_response
from base64 import b64encode
import collections

#from sockets import parser 
from sockets.parser import Parser
datalist = []
images_deque = collections.deque()

@socketio.on('client_connected')
def handle_client_connect_event(json):
    mqtt.subscribe('master/lastWill/#')
    print('received json: {0}'.format(str(json)))

@socketio.on('number_of_nodes2')
def number_of_nodes2(data):
    images_deque.clear()
    datalist.clear()
    resp = make_response()
    resp.set_cookie("number_of_nodes2", data['data'])
    print('No. of nodes: ' + str(data['data']))
    sockets.real_time_object_detection.number_of_nodes = int(data['data'])
    sockets.real_time_object_detection.first_run = True
    sockets.real_time_object_detection.time_for_fps = time.time()

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

@socketio.on('detected_image')
def handle_mqtt_unsubscribe(b64):
    print(b64)

@socketio.on('deleteDB')
def handle_delete_DB(json_str):
    p = Parser()
    p.deleteDB()
    print('Deleted all entries in DB')

@socketio.on('mqtt_query_nodes')
def handle_mqtt_query_nodes(json_str):
    data = json.loads(json_str)
    mqtt.subscribe(data['topic'])
    mqtt.publish('slave/query/flask', 'query')
    mqtt.publish('master/query/flask', 'query')

@socketio.on('mqtt startMaster')
def handle_mqtt_unsubscribe(json_str):
    data = json.loads(json_str)
    p = Parser()
    
    mqtt.publish(data['topic'], data['payload'])

class images(object):
    def __init__(self, image_string, time_sent):
        self.image_string = image_string
        self.time_sent = time_sent

    def print_image(self):
        print(self.time_sent)

    def __eq__(self, other):
        return self.time_sent == other.time_sent

    def __lt__(self, other):
        return self.time_sent < other.time_sent

@mqtt.on_message()
def handle_mqtt_message(client, userdata, message):
    data = dict(
        topic=message.topic,
        payload = message.payload.decode()
    )
    if 'flask/query' in data['topic']:
        p = Parser()
        # print(data['payload'])
        p.insert_or_update(data['payload'])
        p.test()

        json_str = p.generateJSON()
        # get all data from DB and send as list? to emit
        socketio.emit('mqtt_query_response', data = json_str)
    elif 'master/lastWill' in data['topic']:
        p = Parser()
        p.deleteDB()
        print('Deleted all entries in DB')
        mqtt.publish('slave/query/flask', 'query')
        mqtt.publish('master/query/flask', 'query')
    elif 'hello/server' in data['topic']:
        # print(data['topic'])
        # print('Time before send to JS: {}'.format(datetime.datetime.now()))
        json_payload = data['payload']
        json_str = json.loads(json_payload)

        # last resort: just finish in a loop before moving on and appending
        #option 2 : slow but not failing easily? or not failing intensely
        datalist.append(images(json_str['image'], json_str['time_sent']))
        datalist.sort(reverse=True)
        earliest_in_queue = datalist.pop()
        socketio.emit('processed_image_by_slave', data=earliest_in_queue.image_string)

        #option 1: fails after some time
        # if images_deque:
        #     latest_timestamp = images_deque[0]['time_sent']
        #     if json_str['time_sent'] > latest_timestamp:
        #         images_deque.appendleft(json_str)
        #     else:
        #         print('discarded received image')
        # else:
        #     images_deque.appendleft(json_str)

        # if images_deque:
        #     earliest_in_queue = images_deque.pop()

        # socketio.emit('processed_image_by_slave', data=earliest_in_queue['image'])
    else:
        socketio.emit('mqtt_message', data=data)
