import os
from flask import render_template, request, send_from_directory, url_for, redirect, flash, Response, send_file
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
from sockets.real_time_object_detection import bench
from sockets.pi_object_detection import bench_rt
import matplotlib.pyplot as plt
from io import BytesIO

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
    return render_template('query.html', header='CONTROL PANEL')

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

@app.route('/fig')
def fig():
    # #fig = draw_polygons(cropzonekey)
    # fig = plt.plot([1,2,3,4], [1,2,3,4])
    # #img = StringIO()
    # img = BytesIO()
    # #fig.savefig(img)
    # plt.savefig(img)
    # img.seek(0)

    x = []
    y1 = []
    y2 = []

    x.append(1)
    y1.append(33102)
    y2.append(0.9802)
    # y1 = np.sin(x);
    # y2 = 0.01 * np.cos(x);

    fig = plt.figure()
    ax1 = fig.add_subplot(111)
    ax1.plot(x, y1, linestyle='--', marker='o', color='b')
    ax1.set_ylabel('Duration(ms)', fontsize=14)

    ax2 = ax1.twinx()
    ax2.plot(x, y2, '--ro')
    ax2.set_ylabel('accuracy', color='r', fontsize=14)
    for tl in ax2.get_yticklabels():
        tl.set_color('r')
    img = BytesIO()
    ax1.set_xlabel('iterations', fontsize=14)
    plt.savefig(img)
    img.seek(0)

    return send_file(img, mimetype='image/png')

@app.route('/update_configs', methods=['POST'])
def update_configs():
    changes = request.form['text'].replace('\r', '').replace('\n', '')
    # check if key exists before updating

    if 'toMaster' in request.form:
        print(changes)
        os.chdir("/home/pi/random_pi_forest/distRF/bin/master_node/")
        command = 'jq \'. + {{{0}}}\' configs.json > configs.tmp && mv configs.tmp configs.json'.format(changes)
        os.system(command)
        mqtt.publish('master/config/flask', changes)
        flash('Successfully sent to master')
    elif 'toSlaves' in request.form:
        if 'nodeName' in changes:
            flash('Don\'t change nodeName for slaves')
            return redirect(url_for('index'))
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

@app.route('/benchmark_vid')
def benchmark_vid():
    mqtt.subscribe('hello/server')
    print('subscribe to hello/server')
    return render_template('benchmark_vid.html')

# Can use either bench() or bench_rt()
@app.route('/benchmark')
def benchmark():
    num = request.cookies.get('number_of_nodes2')
    print('nodes: {}', num)
    return Response(bench(Camera()),
                    mimetype='multipart/x-mixed-replace; boundary=frame')