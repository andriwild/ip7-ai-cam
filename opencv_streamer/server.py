# https://pyimagesearch.com/2019/09/02/opencv-stream-video-to-web-browser-html-page/

# https://onnxruntime.ai/docs/tutorials/iot-edge/rasp-pi-cv.html

from flask import Response, Flask, render_template, request
from flask_cors import CORS
from ultralytics import YOLO
from metadata import get_cpu_usage, get_temperature, get_storage_usage

import threading
import argparse
import datetime
import time
import cv2
import glob
import json as JSON

outputFrame = None
lock = threading.Lock()

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

camera = None
available_cameras = []
model = YOLO("yolo11n.onnx")
confidence = 0.5
roi = None

def start_camera(camera_id=0):
    global camera
    camera = cv2.VideoCapture("/dev/video0")
    r = camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    print(r)
    r = camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
    print(r)
    r = camera.set(cv2.CAP_PROP_FPS, 60)
    print(r)
    r = camera.set(cv2.CAP_PROP_ZOOM, 1)
    print(r)
    r = camera.set(cv2.CAP_PROP_AUTOFOCUS, 1)
    print(r)
    #camera = VideoStream(src=0).start()

    time.sleep(2.0)


def find_available_cameras():
    available_cameras = []
    for camera in glob.glob("/dev/video?"):
        c = cv2.VideoCapture(camera)
        c.set(cv2.CAP_PROP_FPS, 30)
        print(f"camera {camera}: {c.isOpened()}")
        if c.isOpened():
            available_cameras.append(camera)
    return available_cameras


def generate():
    global outputFrame, lock
    while True:
        with lock:
            if outputFrame is None:
                print("outputFrame is None")
                exit(1)
            # encode the frame in JPEG format
            (success, encodedImage) = cv2.imencode(".jpg", outputFrame)
            # ensure the frame was successfully encoded
            if not success:
                continue
        # yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
              bytearray(encodedImage) + b'\r\n')


@app.route("/")
def index():
    return render_template("index.html", server_url=request.host_url)


@app.route("/cameras", methods=['GET'])
def get_cameras():
    return available_cameras


@app.route('/camera', methods=['POST'])
def set_camera():
    data = request.get_data()
    data = JSON.loads(data)
    print("New Camera: ",data['camera'])
    with lock:
        global camera
        camera.release()

        time.sleep(1)
        camera = cv2.VideoCapture(data['camera'])
        time.sleep(1)
        if camera.isOpened():
            print("OK")
        return "OK", 200


@app.route("/model", methods=['POST'])
def set_model():
    data = request.get_data()
    data = JSON.loads(data)
    print("New Model: ",data['model'])
    with lock:
        global model
        model = YOLO(data['model'])
        return "OK", 200


@app.route("/roi", methods=['POST'])
def set_roi():
    global roi
    data = request.get_data()
    data = JSON.loads(data)
    if data['roi'] is None or data["roi"] == "":
        roi = None
    else:
        with lock:
            roi = data['roi']
    return "OK", 200


@app.route("/confidence", methods=['GET'])
def get_confidence():
    return JSON.dumps({"confidence": confidence})


@app.route("/confidence", methods=['POST'])
def set_confidence():
    global confidence
    data = request.get_data()
    data = JSON.loads(data)
    print("New Confidence: ",data['confidence'])
    confidence = float(data['confidence'])
    return "OK", 200


@app.route("/resolution", methods=['POST'])
def set_resolution():
    global camera
    try:
        data = request.get_data()
        data = JSON.loads(data)

        width_str, height_str = data["resolution"].split('x')
        width = int(width_str)
        height = int(height_str)
    except ValueError:
        return "No valid format. Use e.g. 640x640", 400

    with lock:
        camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    return f"Camera resolution set to {width}x{height}."


@app.route("/meta", methods=['GET'])
def get_meta():
    return JSON.dumps({
        "cpu": get_cpu_usage(),
        "temp": get_temperature(),
        "storage": get_storage_usage()
    })

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")


def get_frame():
    global camera, outputFrame, lock
    while True:
        with lock:
            success, frame = camera.read()
            if not success or frame is None:
                break

        if roi is not None:
            # TODO: parse before storing in roi
            y = int(float(roi["y"]))
            x = int(float(roi["x"]))
            h = y + int(float(roi["h"]))
            w = x + int(float(roi["w"]))
            frame = frame[y:h, x:w]

        results = model(frame, verbose=False, conf=confidence)
        frame = results[0].plot()

        timestamp = datetime.datetime.now()
        cv2.putText(
                frame,
                timestamp.strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.35,
                (0, 0, 255),
                1)

        with lock:
            outputFrame = frame.copy()

if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, default="0.0.0.0",
                    help="ip address of the server")
    ap.add_argument("-o", "--port", type=int, default=8000,
                    help="ephemeral port number of the server")

    args = vars(ap.parse_args())

    available_cameras = find_available_cameras()
    start_camera(available_cameras[0])

    t = threading.Thread(target=get_frame)
    t.daemon = True
    t.start()

    app.run(
            host=args["ip"], 
            port=args["port"], 
            debug=True,
            threaded=True, 
            use_reloader=False
            )
