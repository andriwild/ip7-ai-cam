# based on: https://pyimagesearch.com/2020/09/02/opencv-stream-video-to-web-browser-html-page/
# onnx runtime info: https://onnxruntime.ai/docs/tutorials/iot-edge/rasp-pi-cv.html



# TODO: was kann ein ultralytics model alles verarbeiten? Schnittstelle für model outputs (bounding boxen, ...)
import threading
import json
import argparse
import datetime
import cv2
import sys
from queue import Queue, Empty
from flask import Response, Flask, render_template, request
from flask_cors import CORS
from ultralytics import YOLO
from camera_adapter.ICamera import ICamera
from configuration import Configuration
from camera_adapter.CameraFactory import CameraFactory

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# Shared Resources
frame_queue = Queue(maxsize=5)  # Store up to 5 frames in memory
model = YOLO("ml_models/yolo11n.onnx")
confidence = 0.5
roi = None

config = Configuration()
camera_factory = None
frame_producer_thread = None
stop_producer_event = threading.Event()

class FrameProducer(threading.Thread):
    def __init__(self, camera: ICamera, frame_queue: Queue, stop_event: threading.Event):
        super().__init__(daemon=True)
        self.camera = camera
        self.frame_queue = frame_queue
        self.stop_event = stop_event

    def run(self):
        while not self.stop_event.is_set():
            print("producer get_frame")
            frame = self.camera.get_frame()
            if frame is None:
                # If the camera ends or fails, we could break or wait a moment
                break
            
            timestamp = datetime.datetime.now()
            cv2.putText(
                frame,
                timestamp.strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.35,
                (0, 0, 255),
                1
            )

            # Try to put a frame into the queue without blocking too long
            # If queue is full, we discard the oldest frame and put the new one.
            if self.frame_queue.full():
                try:
                    self.frame_queue.get_nowait()  # discard oldest frame
                except Empty:
                    pass
            self.frame_queue.put(frame)

def generate_frame():
    while True:
        try:
            frame = frame_queue.get(timeout=1.0)  # Wait up to 1 second for a frame
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

def on_update():
    print("on update callback - changing camera")

    global frame_producer_thread, stop_producer_event

    stop_producer_event.set()  # Stop the current producer
    if frame_producer_thread and frame_producer_thread.is_alive():
        print("waiting on thread", frame_producer_thread, frame_producer_thread.is_alive())
        frame_producer_thread.join()
    else:
        print("frame_producer_thread is None")
        
    # Reset the stop event for the new producer
    stop_producer_event = threading.Event()

    # Get the new camera instance from factory
    new_camera = camera_factory.get_camera()
    if new_camera is None:
        print("No camera available after update.")
        return
    else:
        print("new camera is not None")

    # Start a new producer thread with the updated camera
    start_frame_producer(new_camera)

def start_frame_producer(camera: ICamera):
    global frame_producer_thread
    print("start_frame_producer")
    frame_producer_thread = FrameProducer(camera, frame_queue, stop_producer_event)
    frame_producer_thread.start()
    print("started new thread")

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip", type=str, default="0.0.0.0", help="ip address of the server")
    parser.add_argument("-o", "--port", type=int, default=8000, help="ephemeral port number of the server")
    args = vars(parser.parse_args())
    print(args)

    camera_factory = CameraFactory(on_update)
    config.attach(camera_factory)

    # Initial camera setup
    config.set_camera("cv")
    initial_camera = camera_factory.get_camera()
    if initial_camera is None:
        print("No initial camera available. Exiting.")
        sys.exit(1)

    # Start producing frames
    start_frame_producer(initial_camera)


    app.run(
        host=args["ip"], 
        port=args["port"], 
        debug=True,
        threaded=True, 
        use_reloader=False
    )

