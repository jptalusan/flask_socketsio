# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
from multiprocessing import Process
from multiprocessing import Queue
import numpy as np
import argparse
import imutils
import time
import cv2
from sockets import socketio, mqtt
import base64
import json

#camera is faster when using the VideoStream, faster by almost three times.
#however processing is still the same anyway
global_bench_camera_control = 0

@socketio.on('bench_switch')
def bench_switch(flag):
    print('switch pressed: {}'.format(flag))
    global global_bench_camera_control
    global_bench_camera_control = flag

def classify_frame(net, inputQueue, outputQueue):
    # keep looping
    while True:
        # check to see if there is a frame in our input queue
        if not inputQueue.empty():
            # grab the frame from the input queue, resize it, and
            # construct a blob from it
            frame = inputQueue.get()
            frame = cv2.resize(frame, (300, 300))
            blob = cv2.dnn.blobFromImage(frame, 0.007843,
                (300, 300), 127.5)
 
            # set the blob as input to our deep learning object
            # detector and obtain the detections
            net.setInput(blob)
            detections = net.forward()
 
            # write the detections to the output queue
            outputQueue.put(detections)

            if global_bench_camera_control == 1:
                break
# def bench_rt():
def bench_rt(camera):
    global global_bench_camera_control
    global_bench_camera_control = 0
    # initialize the list of class labels MobileNet SSD was trained to
    # detect, then generate a set of bounding box colors for each class
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
        "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
        "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
        "sofa", "train", "tvmonitor"]
    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
     
    # load our serialized model from disk
    print("[INFO] loading model...")
    net = cv2.dnn.readNetFromCaffe('/home/pi/git/flask_socketsio/sockets/MobileNetSSD_deploy.prototxt', '/home/pi/git/flask_socketsio/sockets/MobileNetSSD_deploy.caffemodel')

    # initialize the input queue (frames), output queue (detections),
    # and the list of actual detections returned by the child process
    inputQueue = Queue(maxsize=1)
    outputQueue = Queue(maxsize=1)
    detections = None

    # construct a child process *indepedent* from our main process of
    # execution
    print("[INFO] starting process...")
    p = Process(target=classify_frame, args=(net, inputQueue,
        outputQueue,))
    p.daemon = True
    p.start()

    # initialize the video stream, allow the cammera sensor to warmup,
    # and initialize the FPS counter
    print("[INFO] starting video stream...")
    # vs = VideoStream(usePiCamera=True).start()
    time.sleep(2.0)
    fps = FPS().start()

    # loop over the frames from the video stream
    while True:
        # grab the frame from the threaded video stream, resize it, and
        # grab its dimensions
        # frame = vs.read()

        test = camera.get_frame()
        #probably because o this extra step
        frame = cv2.imdecode(np.fromstring(test, dtype=np.uint8), 1)

        frame = imutils.resize(frame, width=400)
        (fH, fW) = frame.shape[:2]

        # if the input queue *is* empty, give the current frame to
        # classify
        if inputQueue.empty():
            inputQueue.put(frame)
     
        # if the output queue *is not* empty, grab the detections
        if not outputQueue.empty():
            detections = outputQueue.get()

        # draw the detections on the frame)
        if detections is not None:
            # loop over the detections
            for i in np.arange(0, detections.shape[2]):
                # extract the confidence (i.e., probability) associated
                # with the prediction
                confidence = detections[0, 0, i, 2]
     
                # filter out weak detections by ensuring the `confidence`
                # is greater than the minimum confidence
                if confidence < 0.2:
                    continue
     
                # otherwise, extract the index of the class label from
                # the `detections`, then compute the (x, y)-coordinates
                # of the bounding box for the object
                idx = int(detections[0, 0, i, 1])
                dims = np.array([fW, fH, fW, fH])
                box = detections[0, 0, i, 3:7] * dims
                (startX, startY, endX, endY) = box.astype("int")
     
                # draw the prediction on the frame
                label = "{}: {:.2f}%".format(CLASSES[idx],
                    confidence * 100)
                cv2.rectangle(frame, (startX, startY), (endX, endY),
                    COLORS[idx], 2)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                cv2.putText(frame, label, (startX, y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

        # show the output frame
        #and this one
        img_str = cv2.imencode(".jpg", frame)

        send_data = base64.b64encode(img_str[1].tostring())
        mqtt.publish('hello/world', send_data)

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img_str[1].tostring() + b'\r\n')

        # cv2.imshow("Frame", frame)
        # key = cv2.waitKey(1) & 0xFF
     
        # if the `q` key was pressed, break from the loop
        # if key == ord("q"):
        #     break
        if global_bench_camera_control == 1:
            if not inputQueue.empty():
                detections = inputQueue.get()
            if not outputQueue.empty():
                detections = outputQueue.get()
            break
        # update the FPS counter
        fps.update()
         
    # stop the timer and display FPS information
    fps.stop()
    print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

    data = {"elapsed": fps.elapsed(), "fps": fps.fps()}
    socketio.emit('fps_data', json.dumps(data))
     
    # do a bit of cleanup
    # cv2.destroyAllWindows()
    # vs.stop()

