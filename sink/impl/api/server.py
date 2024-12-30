import logging
import threading
from queue import Queue, Empty

import cv2
from flask import Flask, request, jsonify, Response, render_template
from flask_cors import CORS
from werkzeug.serving import make_server

from config.config import ConfigManager
from kafkaUtil.helper import get_kafka_producer
from model.result import Result
from sink.interface.sink import Sink

logger = logging.getLogger(__name__)

class WebServer(Sink):
    def __init__(self, name: str, host="0.0.0.0", port=8000):
        self._name = name
        self._host = host
        self._port = port
        self._result_queue = Queue(maxsize=5)
        self._producer = get_kafka_producer("localhost:29092")

        self._app = Flask(__name__, template_folder="./sink/impl/api/templates")
        CORS(self._app)
        self._app.config['CORS_HEADERS'] = 'Content-Type'

        self._configure_routes()
        self._server_thread = threading.Thread(target=self._run_server)
        self._server = None
        self._running = False
        logger.info("WebServer initialized.")
        self.start()

    def _configure_routes(self):
        logger.info("Configuring routes...")
        @self._app.route("/available", methods=['GET'])
        def get_available():
            return jsonify(ConfigManager().get_config())

        @self._app.route("/source", methods=['POST'])
        def set_source():
            data = request.get_json() or {}
            source_val = data.get("source")
            if source_val:
                self._producer.send("pipeline-settings", {
                    "setting": "source",
                    "value": source_val
                })
                self._producer.flush()
                return jsonify({"status": "ok", "source": source_val})
            else:
                return jsonify({"status": "error", "message": "No sources provided"})

        @self._app.route("/sinks", methods=['POST'])
        def set_sinks():
            data = request.get_json() or {}
            sinks_val = data.get("sinks")
            if sinks_val:
                self._producer.send("pipeline-settings", {
                    "setting": "sink",
                    "value": sinks_val
                })
                self._producer.flush()
                return jsonify({"status": "ok", "sinks": sinks_val})
            else:
                return jsonify({"status": "error", "message": "No sinks provided"})

        @self._app.route("/video_feed")
        def video_feed():
            return Response(
                self._generate_frame(),
                mimetype="multipart/x-mixed-replace; boundary=frame"
            )

        @self._app.route("/")
        def index():
            return render_template("index.html")

        logger.info("Routes configured.")

    def _generate_frame(self):
        while self._running:
            try:
                result = self._result_queue.get(timeout=1)
            except Empty:
                continue

            if not result:
                continue

            frame = result.draw(result.frame)
            success, encoded_image = cv2.imencode(".jpg", frame)
            if not success:
                logger.error("Error encoding frame")
                continue

            yield (b"--frame\r\n"
                   b"Content-Type: image/jpeg\r\n\r\n" +
                   bytearray(encoded_image) +
                   b"\r\n")

    def _run_server(self):
        logger.info("Starting server...")
        self._server = make_server(self._host, self._port, self._app)
        self._running = True
        logger.info(f"Starting server on {self._host}:{self._port}...")
        self._server.serve_forever()

    def start(self):
        logger.info("Starting server...")
        if self._server_thread.is_alive():
            logger.info("Server is already running.")
            return

        self._server_thread = threading.Thread(target=self._run_server)
        logger.info("Starting server thread...")
        self._server_thread.start()

    def stop(self):
        logger.info("Stopping server...")
        if not self._server:
            logger.info("Server is not running.")
            return

        logger.info("Stopping server...")
        self._running = False
        self._server.shutdown()
        self._server_thread.join()
        self._server = None
        logger.info("Server stopped.")

    def put(self, result: Result):
        if self._result_queue.full():
            logger.info("Result queue is full, discarding oldest frame")
            try:
                self._result_queue.get_nowait()
            except Empty:
                pass

        self._result_queue.put(result)

    def get_name(self):
        return self._name

    def release(self):
        logger.info("Releasing resources...")
        self.stop()
