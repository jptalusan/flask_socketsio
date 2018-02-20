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
import os
import time

from threading import Thread
from queue import Queue
import matplotlib.pyplot as plt
import numpy as np

global_bench_camera_control = 0
number_of_nodes = 5
first_run = True
# node_frames = [[1, 20], [2, 12], [3, 6], [4, 3], [5, 2]]
node_frames = [[1, 20], [2, 7], [3, 4], [4, 2], [5, 1.2]]

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
    print('switch pressed in realtime.py')
    global global_bench_camera_control
    global_bench_camera_control = flag
    curr_node = 0

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

def generate_plot():
    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    # ax1.set_yticks(np.arange(min(duration), max(duration) + 5, 5))
    print(duration)
    # if len(duration) == 1:
    ax1.set_ylim([duration[0] - duration[0]/2, duration[0] + duration[0]/2])
    # ax1.plot(iterations, duration, linestyle=':', marker='x', color='b')
    ax1.bar(iterations, duration, align='center', alpha=0.5)# linestyle=':', marker='x', color='b')
    ax1.set_ylabel('Duration(s)', fontsize=14)

    ax2 = ax1.twinx()
    # ax2.set_yticks(np.arange(0.2, 1.2, 0.1))
    ax2.plot(iterations, accuracy, linestyle='--', marker='o', color='r')
    ax2.set_ylim([0.5, 1.0])
    ax2.set_ylabel('Duration(s)', fontsize=14)
    for tl in ax2.get_yticklabels():
        tl.set_color('r')

    plt.setp(ax2.get_yticklabels(), visible=True)
    ax1.set_xlabel('iterations', fontsize=14)
    ax1.set_xticks(np.arange(min(iterations), max(iterations) + 1, 1))
    plt.savefig(img)

def bench(camera):
    socketio.emit('number_of_nodes', number_of_nodes)
    # print("[INFO] loading model...")

    # time.sleep(2.0)
    fps = FPS().start()
    
    frames_for_fps = 0
    time_for_fps = time.time()
    first_run = True
    frame_cnt = 0
    curr_node = 0
    # since 18 frames a second, and detection is ~1 fps. only send every 18 frames
    while True:
        test = camera.get_frame()
        # print('number of nodes: {}'.format(number_of_nodes))
        frame = cv2.imdecode(np.fromstring(test, dtype=np.uint8), 1)
        frame = imutils.resize(frame, width=400)
        node_cnt = number_of_nodes

        if first_run and node_cnt == 0:
            frames_for_fps = 0
            time_for_fps = time.time()
            CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
                "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
                "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
                "sofa", "train", "tvmonitor"]
            COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
             
            # load our serialized model from disk
            print("[INFO] loading model...")
            net = cv2.dnn.readNetFromCaffe('/home/pi/git/flask_socketsio/sockets/MobileNetSSD_deploy.prototxt', '/home/pi/git/flask_socketsio/sockets/MobileNetSSD_deploy.caffemodel')
            first_run = False

        if node_cnt is 0:
            frame_cnt = frame_cnt + 1

            if frame_cnt % 10 == 0:
                (h, w) = frame.shape[:2]
                blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
                    0.007843, (300, 300), 127.5)
             
                net.setInput(blob)
                detections = net.forward()

                # data = pickle.dumps(detections)

                for i in np.arange(0, detections.shape[2]):
                    confidence = detections[0, 0, i, 2]
                    if confidence > 0.2:
                        idx = int(detections[0, 0, i, 1])
                        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                        (startX, startY, endX, endY) = box.astype("int")

                        label = "{}: {:.2f}%".format(CLASSES[idx],
                            confidence * 100)
                        cv2.rectangle(frame, (startX, startY), (endX, endY),
                            COLORS[idx], 2)
                        y = startY - 15 if startY - 15 > 15 else startY + 15
                        cv2.putText(frame, label, (startX, y),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

                img_str = cv2.imencode(".jpg", frame)

                # time_sent = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                # fh = open("0 nodes.txt","a")
                # fh.write(time_sent)
                # fh.write('\r\n')
                # fh.close()

                fps.update()
                frames_for_fps += 1
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + img_str[1].tostring() + b'\r\n')
             
            curr_time = time.time()
            difference = int(curr_time - time_for_fps)
            if difference != 0:
                curr_fps = (frames_for_fps * 1.0) / difference
                # print('FPS:{}'.format(str(curr_fps)))
                curr_fps_str = '{0:.2f}'.format(curr_fps)
                data = {"elapsed": difference, "fps": curr_fps_str}
                socketio.emit('fps_data', json.dumps(data))
        else:
            #before detect
            # img_str = cv2.imencode(".jpg", frame)
            frame_cnt = frame_cnt + 1
            if (frame_cnt % (node_frames[node_cnt - 1][0] * node_frames[node_cnt - 1][1]) == 0):
                # print('Time before first send: {}'.format(datetime.datetime.now()))
                time_sent = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
                send_data = base64.b64encode(test)

                base64_string = send_data.decode('utf-8')
                data = {"image": base64_string, "time_sent": time_sent}

                # send_to_node = 'hello/world0'
                send_to_node = 'hello/world' + str(curr_node)
                mqtt.publish(send_to_node, json.dumps(data))
                frame_cnt = 1
                curr_node = curr_node + 1
                if curr_node % node_cnt == 0:
                    curr_node = 0

            img_str = cv2.imencode(".jpg", frame)

            fps.update()
            frames_for_fps += 1
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + img_str[1].tostring() + b'\r\n')
         
            curr_time = time.time()
            difference = int(curr_time - time_for_fps)
            if difference != 0:
                curr_fps = (frames_for_fps * 1.0) / difference
                # print('FPS:{}'.format(str(curr_fps)))
                curr_fps_str = '{0:.2f}'.format(curr_fps)
                data = {"elapsed": difference, "fps": curr_fps_str}
                socketio.emit('fps_data', json.dumps(data))

        if global_bench_camera_control == 1:
            print('should stop here...')
            break

    # stop the timer and display FPS information
    fps.stop()
    print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
    data = {"elapsed": fps.elapsed(), "fps": fps.fps()}
    socketio.emit('fps_data', json.dumps(data))
