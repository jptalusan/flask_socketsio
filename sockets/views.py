import os
from flask import render_template, request, send_from_directory, url_for, redirect, flash, Response
from werkzeug.utils import secure_filename
from flask import current_app
import subprocess
import json
from sockets import app
from sockets import mqtt
from sockets import Camera
import jsonpickle
import base64
import numpy as np
from sockets import socketio, mqtt

from imutils.video import VideoStream
from imutils.video import FPS

import imutils
import time
import cv2

global_bench_camera_control = 0

@socketio.on('bench_switch')
def bench_switch(flag):
    global global_bench_camera_control
    global_bench_camera_control = flag

def gen(camera):
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'csv', 'jpg', 'jpeg', 'png'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('query.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        if 'upload' not in request.files:
            flash('No file part')
            return redirect(url_for('index'))
            #redirect
        f = request.files['upload']
        if f.filename == '':
            flash('No selected file')
            return redirect(url_for('index'))
            #redirect
        if f and allowed_file(f.filename):
            filename = secure_filename(f.filename)
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename = filename))
        return redirect(url_for('index'))

@app.route('/update_configs', methods=['POST'])
def update_configs():
    changes = request.form['text']

    # check if key exists before updating
    # with open('configs.json') as json_data:
    #     d = json.load(json_data)

    if 'toMaster' in request.form:
        print(changes)
        os.chdir("/home/pi/random_pi_forest/distRF/bin/master_node/")
        command = 'jq \'. + {{{0}}}\' configs.json > configs.tmp && mv configs.tmp configs.json'.format(changes)
        os.system(command)
        mqtt.publish('master/config/flask', changes)
        flash('Successfully sent to master')
    elif 'toSlaves' in request.form:
        print(changes)
        # os.chdir("/home/pi/random_pi_forest/distRF/bin/slave_node/")
        # command = 'jq \'. + {{{0}}}\' configs.json > configs.tmp && mv configs.tmp configs.json'.format(changes)
        # os.system(command)
        mqtt.publish('slave/config', changes)
        flash('Successfully sent to slaves')
    else:
        return redirect(url_for('index'))
        # test

    # proc = subprocess.Popen(["cat /home/pi/random_pi_forest/distRF/bin/master_node/configs.json | tr '\n' ' '"], stdout=subprocess.PIPE, shell=False)
    proc = subprocess.Popen(["cat /home/pi/random_pi_forest/distRF/bin/master_node/configs.json"], stdout=subprocess.PIPE, shell=True)
    # proc = subprocess.Popen(["jq '.' mock.json"], stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()


    pairs = out.decode('utf-8').split('\n')
    # return render_template('json_response.html', pairs=pairs)
    return redirect(url_for('index'))

@app.route('/uploads/<path:filename>', methods=['GET', 'POST'])
def uploaded_file(filename):
    uploads = os.path.join(current_app.root_path, 'uploads')
    print(uploads)
    return send_from_directory(directory = uploads, filename = filename)

@app.route('/live')
def live():
    return render_template('live.html')

@app.route('/img_test')
def img_test():
    return render_template('test.html')

def gen2(camera):
    camera.resolution = (640, 480)
    frame = camera.get_frame()
    yield frame

@app.route('/api/test', methods=['POST'])
def test():
    r = request
    
    # convert string of image data to uint8
    nparr = np.fromstring(r.data, np.uint8)
    # decode image
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    cv2.imwrite(os.path.join(app.config['UPLOAD_FOLDER'],'person.jpg'), img)
    # do some fancy processing here....

    data = np.array(img)

    # build a response dict to send back to client
    socketio.emit('detected_image', r.data)
    # socketio.emit('detected_image', b64)
    response = {'message': 'image received: size={}x{}'.format(img.shape[1], img.shape[0])}
    # encode response using jsonpickle
    response_pickled = jsonpickle.encode(response)

    return Response(response=response_pickled, status=200, mimetype="application/json")

@app.route('/image.jpg')
def shot():
    return Response(gen2(Camera()), mimetype='image/jpeg')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

def bench(camera):
    # while True:
        # frame = camera.get_frame()
        # yield (b'--frame\r\n'
        #        b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
    CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
        "bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
        "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
        "sofa", "train", "tvmonitor"]
    COLORS = np.random.uniform(0, 255, size=(len(CLASSES), 3))
     
    # # load our serialized model from disk
    # print("[INFO] loading model...")
    net = cv2.dnn.readNetFromCaffe('/home/pi/git/flask_socketsio/sockets/MobileNetSSD_deploy.prototxt', '/home/pi/git/flask_socketsio/sockets/MobileNetSSD_deploy.caffemodel')

    # # initialize the video stream, allow the camera sensor to warm up,
    # # and initialize the FPS counter
    # print("[INFO] starting video stream...")
    # # vs = VideoStream(src=0).start()
    # vs = VideoStream(usePiCamera=True).start()
    time.sleep(2.0)
    fps = FPS().start()

    # timer = time.time()
    # frame_cnt = 0

    # loop over the frames from the video stream
    while True:
        # grab the frame from the threaded video stream and resize it
        # to have a maximum width of 400 pixels
        # frame = vs.read()
        test = camera.get_frame()
        frame = cv2.imdecode(np.fromstring(test, dtype=np.uint8), 1)
        frame = imutils.resize(frame, width=400)
        
        # frame_cnt = frame_cnt + 1
        
        # grab the frame dimensions and convert it to a blob
        (h, w) = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)),
            0.007843, (300, 300), 127.5)
     
        # pass the blob through the network and obtain the detections and
        # predictions
        net.setInput(blob)
        detections = net.forward()

        # loop over the detections
        for i in np.arange(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with
            # the prediction
            confidence = detections[0, 0, i, 2]

            # filter out weak detections by ensuring the `confidence` is
            # greater than the minimum confidence
            if confidence > 0.2:
                # extract the index of the class label from the
                # `detections`, then compute the (x, y)-coordinates of
                # the bounding box for the object
                idx = int(detections[0, 0, i, 1])
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")

                # draw the prediction on the frame
                label = "{}: {:.2f}%".format(CLASSES[idx],
                    confidence * 100)
                cv2.rectangle(frame, (startX, startY), (endX, endY),
                    COLORS[idx], 2)
                y = startY - 15 if startY - 15 > 15 else startY + 15
                cv2.putText(frame, label, (startX, y),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS[idx], 2)

        img_str = cv2.imencode(".jpg", frame)
        # update the FPS counter
        fps.update()

        # elapsed_time = (time.time() - timer)
        # data = {"elapsed": elapsed_time, "fps": (frame_cnt/elapsed_time)}
        # socketio.emit('fps_data', json.dumps(data))

        # show the output frame
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img_str[1].tostring() + b'\r\n')
        # cv2.imshow("Frame", frame)
        # key = cv2.waitKey(1) & 0xFF
     
        # if the `q` key was pressed, break from the loop
        if global_bench_camera_control == 1:
            break
     
    # stop the timer and display FPS information
    fps.stop()
    print("[INFO] elapsed time: {:.2f}".format(fps.elapsed()))
    print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))
    data = {"elapsed": fps.elapsed(), "fps": fps.fps()}
    socketio.emit('fps_data', json.dumps(data))

@app.route('/benchmark_vid')
def benchmark_vid():
    return render_template('benchmark_vid.html')

@app.route('/benchmark')
def benchmark():
    return Response(bench(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')