# based on: https://pyimagesearch.com/2020/09/02/opencv-stream-video-to-web-browser-html-page/
# onnx runtime info: https://onnxruntime.ai/docs/tutorials/iot-edge/rasp-pi-cv.html



# TODO: was kann ein ultralytics model alles verarbeiten? Schnittstelle für model outputs (bounding boxen, ...)
import threading
import json
import argparse
import cv2
import logging
from queue import Queue, Empty
from flask import Response, Flask, render_template, request
from flask_cors import CORS
from ultralytics import YOLO
from camera_adapter.cameraController import FrameProvider
from configuration import Configuration

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Shared Resources
frame_queue = Queue(maxsize=5)  # Store up to 5 frames in memory
model = YOLO("ml_models/yolo11n.onnx")
confidence = 0.5
roi = None

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def generate_frame():
    while True:
        try:
            frame = frame_queue.get(timeout=1.0)  # Wait up to 1 second for a frame
            print(f"fetched frame: None={frame is None}")
        except Empty:
            print("No frames available in queue.")
            continue

        # encode the frame in JPEG format
        (success, encodedImage) = cv2.imencode(".jpg", frame)
        if not success:
            continue
        yield (b'--frame\r\n' 
               b'Content-Type: image/jpeg\r\n\r\n' + 
               bytearray(encodedImage) + b'\r\n')


@app.route("/cameras", methods=['GET'])
def get_cameras():
    return ["cv", "pi"]


@app.route('/camera', methods=['POST'])
def set_camera():
    data = request.get_data()
    data = json.loads(data)
    print("New Camera: ",data['camera'])
    config.set_camera(data["camera"])
    return "Ok"


@app.route("/")
def index():
    return render_template("index.html", server_url=request.host_url)


@app.route("/video_feed")
def video_feed():
    return Response(generate_frame(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


def main(host: str, port: int)-> None:
    frame_provider = FrameProvider(frame_queue)
    config = Configuration()

    config.attach(frame_provider)

    frame_provider.start()

    app.run(
        host=host, 
        port=port, 
        debug=True,
        threaded=True, 
        use_reloader=False
    )



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip", type=str, default="0.0.0.0", help="ip address of the server")
    parser.add_argument("-o", "--port", type=int, default=8000, help="ephemeral port number of the server")
    args = vars(parser.parse_args())
    main(args["ip"], args["port"])

