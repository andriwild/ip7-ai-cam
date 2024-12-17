import json
import logging
import threading
from queue import Empty, Queue

import cv2
from flask import Response, Flask, render_template, request
from flask_cors import CORS

from config.configuration import Configuration
from controller.controller import Controller
from model.capture import Capture
from sink.interface.sink import Sink

logger = logging.getLogger(__name__)

class WebServer(Sink):
    def __init__(self, controller: Controller, config: Configuration):
        self.app = Flask(__name__)
        CORS(self.app)
        self.app.config['CORS_HEADERS'] = 'Content-Type'
        self._controller = controller
        self.config = config
        self._capture_queue = Queue(maxsize=5)
        self._setup_routes()

        threading.Thread(target=self.run, args=("0.0.0.0", 8000)).start()


    def put(self, capture: Capture) -> None:
        logger.debug("Putting capture in queue")
        if self._capture_queue.full():
            logger.info("capture queue is full")
            try:
                self._capture_queue.get_nowait()  # discard oldest frame
            except Empty:
                pass

        self._capture_queue.put(capture)


    def _setup_routes(self):
        @self.app.route("/sources", methods=['GET'])
        def get_sources():
            return ["static", "image", "cv", "pi"]


        @self.app.route('/source', methods=['POST'])
        def set_source():
            data = request.get_data()
            data = json.loads(data)
            logger.info(f"New source: {data['source']}")
            self.config.set_source(data["source"])
            return "Ok"


        @self.app.route("/models", methods=['GET'])
        def get_models():
            return ["-", "yolo11n.onnx", "yolo11n-pose.onnx", "yolo11n-seg.onnx"]


        @self.app.route('/models', methods=['POST'])
        def set_models():
            data = request.get_data()
            data = json.loads(data)
            logger.info(f"New Models: {data['models']}")
            self.config.set_models(data["models"])
            return "Ok"


        @self.app.route("/")
        def index():
            return render_template("index.html", server_url=request.host_url)


        @self.app.route("/video_feed")
        def video_feed():
            return Response(self._generate_frame(),
                            mimetype="multipart/x-mixed-replace; boundary=frame")

    def _generate_frame(self):
        while True:
            try:
                logger.debug("Getting capture from queue")
                capture = self._capture_queue.get()  # Wait up to 1 second for a capture
            except Empty:
                logger.warning("No captures available in queue")
                continue

            # encode the capture in JPEG format
            frame = capture.get_frame()
            (success, encoded_image) = cv2.imencode(".jpg", frame)

            if not success:
                logger.error("Error encoding frame")
                continue
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' +
                   bytearray(encoded_image) + b'\r\n')


    # based on: https://stackoverflow.com/questions/15562446/how-to-stop-flask-application-without-using-ctrl-c 
    def shutdown_server(self):
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            raise RuntimeError('Not running with the Werkzeug Server')
        func()


    def run(self, host: str, port: int):
        self.app.run(
            host=host,
            port=port,
            debug=True,
            threaded=True,
            use_reloader=False
        )
