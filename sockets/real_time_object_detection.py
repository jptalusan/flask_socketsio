# import the necessary packages
from imutils.video import FPS
import numpy as np
import imutils
import time
import cv2
from sockets import socketio, mqtt
import base64
import json
import datetime
from sockets.websockets import datalist

global_bench_camera_control = 0
number_of_nodes = 1

node_frames = [[1, 26], [2, 8], [3, 5], [4, 2]]

# CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
#     "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
#     "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
#     "sofa", "train", "tvmonitor"]
# # COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
# COLORS = [[ 44.18937886, 246.96730454,  73.04242211],
#        [250.12082477,  64.86789038, 127.30777312],
#        [ 42.24136576,  58.37372156, 164.26309563],
#        [223.06331711, 109.74376324, 155.80390287],
#        [185.08709893, 226.65109253, 207.6055207 ],
#        [236.07673731, 185.30827578, 202.81771854],
#        [144.55106179, 144.33676777,  13.94532094],
#        [187.12402101,  17.84717238, 169.79134966],
#        [108.56370186,  11.93672853, 101.48437193],
#        [242.67313174, 199.58060928, 105.16230962],
#        [ 55.8721673 , 152.57844089,  10.81330649],
#        [ 61.49715633, 202.01490572, 215.6031341 ],
#        [ 46.84328774,  97.63950579,  45.02124015],
#        [155.97362898, 170.12816067,  22.99799861],
#        [ 84.17340808, 195.2619167 ,  15.89690156],
#        [ 82.28596664, 101.00173901, 133.31767819],
#        [157.12551971, 136.96627224, 219.19731213],
#        [168.25525718,  46.68111693,  89.16807578],
#        [ 41.48822204,  29.68208425, 244.29332197],
#        [197.541347  , 106.32026389, 183.67652336],
#        [203.44645816, 117.39418267, 127.80463932]]

@socketio.on('bench_switch')
def bench_switch(flag):
    global global_bench_camera_control
    global_bench_camera_control = flag

def bench(camera):     
    print("[INFO] loading model...")

    time.sleep(2.0)
    fps = FPS().start()

    frame_cnt = 0
    curr_node = 0
    # since 18 frames a second, and detection is ~1 fps. only send every 18 frames
    while True:
        test = camera.get_frame()

        frame = cv2.imdecode(np.fromstring(test, dtype=np.uint8), 1)
        frame = imutils.resize(frame, width=400)

        #before detect
        # img_str = cv2.imencode(".jpg", frame)
        frame_cnt = frame_cnt + 1
        if (frame_cnt % (node_frames[number_of_nodes - 1][0] * node_frames[number_of_nodes - 1][1]) == 0):
            print('Time before first send: {}'.format(datetime.datetime.now()))
            send_data = base64.b64encode(test)
            # send_to_node = 'hello/world0'
            send_to_node = 'hello/world' + str(curr_node)
            mqtt.publish(send_to_node, send_data)
            frame_cnt = 1
            curr_node = curr_node + 1
            if curr_node == number_of_nodes:
                curr_node = 0

        # (fH, fW) = frame.shape[:2]

        # Change code to just send detections over mqtt
        # https://stackoverflow.com/questions/24423162/how-to-send-an-array-over-a-socket-in-python
        # if datalist:
        #     print('Popping datalist...')
        #     detections = datalist.pop(0)
        #     # draw the detections on the frame)
        #     if detections is not None:
        #         print('Detecting...')
        #         for i in np.arange(0, detections.shape[2]):
        #             confidence = detections[0, 0, i, 2]
        #             if confidence < 0.2:
        #                 continue
        #             idx = int(detections[0, 0, i, 1])
        #             dims = np.array([fW, fH, fW, fH])
        #             box = detections[0, 0, i, 3:7] * dims
        #             (startX, startY, endX, endY) = box.astype("int")
         
        #             # draw the prediction on the frame
        #             label = "{}: {:.2f}%".format(CLASSES[idx],
        #                 confidence * 100)
        #             cv2.rectangle(frame, (startX, startY), (endX, endY),
        #                 COLORS[idx], 2)
        #             y = startY - 15 if startY - 15 > 15 else startY + 15
        #             cv2.putText(frame, label, (startX, y),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)
        #     else:
        #         print('Detection is null...')
        # else:
        #     print('Datalist is empty...')

        img_str = cv2.imencode(".jpg", frame)

        #or after detect
        # send_data = base64.b64encode(img_str[1].tostring())
        # mqtt.publish('hello/world', send_data)

        fps.update()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img_str[1].tostring() + b'\r\n')
     
        if global_bench_camera_control == 1:
            break
     
    # stop the timer and display FPS information
    fps.stop()
    print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
    data = {"elapsed": fps.elapsed(), "fps": fps.fps()}
    socketio.emit('fps_data', json.dumps(data))
