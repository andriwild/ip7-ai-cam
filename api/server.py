import json
import logging
from queue import Queue, Empty

import cv2
from flask import Response, Flask, render_template, request
from flask_cors import CORS

from configuration import Configuration
from controller.controller import Controller

logger = logging.getLogger(__name__)

class WebServer:
    def __init__(self, controller: Controller, config: Configuration):
        self.app = Flask(__name__)
        CORS(self.app)
        self.app.config['CORS_HEADERS'] = 'Content-Type'
        self._controller = controller
        self.config = config

        self._setup_routes()

    def _setup_routes(self):
        @self.app.route("/cameras", methods=['GET'])
        def get_cameras():
            return ["cv", "pi"]

        @self.app.route('/camera', methods=['POST'])
        def set_camera():
            data = request.get_data()
            data = json.loads(data)
            logger.info(f"New Camera: {data['camera']}")
            self.config.set_camera(data["camera"])
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
                frame = self._controller.get(timeout=1.0)  # Wait up to 1 second for a frame
                logger.debug(f"fetched frame: None={frame is None}")
            except Empty:
                logger.warning("No frames available in queue")
                continue

            # encode the frame in JPEG format
            (success, encodedImage) = cv2.imencode(".jpg", frame)
            if not success:
                continue
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' +
                   bytearray(encodedImage) + b'\r\n')

    def run(self, host: str, port: int):
        self.app.run(
            host=host,
            port=port,
            debug=True,
            threaded=True,
            use_reloader=False
        )
