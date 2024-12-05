# https://pyimagesearch.com/2019/09/02/opencv-stream-video-to-web-browser-html-page/

# https://onnxruntime.ai/docs/tutorials/iot-edge/rasp-pi-cv.html

from cv2.typing import MatLike
from flask import Response, Flask, render_template
from flask_cors import CORS
from ultralytics import YOLO

import threading
import argparse
import datetime
import time
import cv2
import glob

outputFrame = None
lock = threading.Lock()

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

camera = None
model = YOLO("yolov8n.onnx")

def start_camera(camera_id=4):
    global camera
    camera = cv2.VideoCapture(camera_id)
    #camera = VideoStream(src=0).start()

    time.sleep(2.0)


def find_available_cameras():
    available_cameras = []
    for camera in glob.glob("/dev/video?"):
        c = cv2.VideoCapture(camera)
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
    return render_template("index.html")

@app.route("/video_feed")
def video_feed():
	# return the response generated along with the specific media
	# type (mime type)
	return Response(generate(),
		mimetype = "multipart/x-mixed-replace; boundary=frame")


def get_frame():
    global camera, outputFrame, lock
    while True:
        success, frame = camera.read()
        if not success or frame is None:
            break

        results = model(frame, verbose=False)
        annotated_frame = results[0].plot()

        timestamp = datetime.datetime.now()
        cv2.putText(
                annotated_frame, 
                timestamp.strftime("%A %d %B %Y %I:%M:%S%p"), 
                (10, frame.shape[0] - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.35, 
                (0, 0, 255), 
                1)

        with lock:
            outputFrame = annotated_frame.copy()

if __name__ == '__main__':
    cams = find_available_cameras()
    print(cams)
    start_camera()

    # construct the argument parser and parse command line arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=True,
                    help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=True,
                    help="ephemeral port number of the server (1024 to 65535)")
    ap.add_argument("-f", "--frame-count", type=int, default=32,
                    help="# of frames used to construct the background model")
    args = vars(ap.parse_args())
    # start a thread that will perform motion detection
    t = threading.Thread(target=get_frame)
    t.daemon = True
    t.start()
    # start the flask app
    app.run(host=args["ip"], port=args["port"], debug=True,
            threaded=True, use_reloader=False)
