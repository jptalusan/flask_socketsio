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
import os

from threading import Thread
from queue import Queue

global_bench_camera_control = 0
number_of_nodes = 4

node_frames = [[1, 26], [2, 8], [3, 5], [4, 2], [5, 1]]

class FileVideoStream:
    def __init__(self, path, queueSize=128):
        # initialize the file video stream along with the boolean
        # used to indicate if the thread should be stopped or not
        self.stream = cv2.VideoCapture(path)
        self.stopped = False

        # initialize the queue used to store frames read from
        # the video file
        self.Q = Queue(maxsize=queueSize)

    def start(self):
        # start a thread to read frames from the file video stream
        t = Thread(target=self.update, args=())
        t.daemon = True
        t.start()
        return self

    def update(self):
        # keep looping infinitely
        while True:
            # if the thread indicator variable is set, stop the
            # thread
            if self.stopped:
                return

            # otherwise, ensure the queue has room in it
            if not self.Q.full():
                # read the next frame from the file
                (grabbed, frame) = self.stream.read()

                # if the `grabbed` boolean is `False`, then we have
                # reached the end of the video file
                if not grabbed:
                    self.stop()
                    return

                # add the frame to the queue
                self.Q.put(frame)

    def read(self):
        # return next frame in the queue
        return self.Q.get()

    def more(self):
        # return True if there are still frames in the queue
        return self.Q.qsize() > 0

    def stop(self):
        # indicate that the thread should be stopped
        self.stopped = True


@socketio.on('bench_switch')
def bench_switch(flag):
    global global_bench_camera_control
    global_bench_camera_control = flag

def vid_to_frames(video):
    vidcap = cv2.VideoCapture(video)
    count = 0
    while vidcap.isOpened():
        success, frame = vidcap.read()
        if success:
            frame = imutils.resize(frame, width=450)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = np.dstack([frame, frame, frame])
            cv2.putText(frame, "Slow Method", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)  
            yield (frame)
            # print('success')
        else:
            print('unsuccess')
            break
    vidcap.release()

def vid_to_frames_faster(video):
    fvs = FileVideoStream(video).start()
    time.sleep(1.0)
    while fvs.more():
        # grab the frame from the threaded video file stream, resize
        # it, and convert it to grayscale (while still retaining 3
        # channels)
        frame = fvs.read()
        frame = imutils.resize(frame, width=450)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = np.dstack([frame, frame, frame])
     
        # display the size of the queue on the frame
        cv2.putText(frame, "Queue Size: {}".format(fvs.Q.qsize()),
            (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)    
        
        yield (frame)
        # show the frame and update the FPS counter
        # cv2.imshow("Frame", frame)
        # cv2.waitKey(1)
        # fps.update()

def playback_from_file():
    count = 0
    #Two methods (seems same to me)
    # frame = vid_to_frames('/home/pi/git/flask_socketsio/sockets/BigBuckBunny.mp4')
    frame = vid_to_frames_faster('/home/pi/git/flask_socketsio/sockets/BigBuckBunny.mp4')
    while True:
        curr_frame = next(frame)
        img_str = cv2.imencode(".jpg", curr_frame)
        # cv2.imwrite(os.path.join('/home/pi/git/flask_socketsio/test', '%d.png') % count, curr_frame)
        count += 1
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img_str[1].tostring() + b'\r\n')

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

        img_str = cv2.imencode(".jpg", frame)

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
