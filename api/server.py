import logging
import threading
from queue import Queue, Empty

import cv2
import uvicorn
from fastapi import FastAPI, Request, Body
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from model.config import ConfigManager
from sink.interface.sink import Sink
from pipeline.pipeline import Result

logger = logging.getLogger(__name__)

class WebServer(Sink):
    def __init__(self, name: str, parameters: dict):
        super().__init__(name)

        self._host = parameters["host"]
        self._port = parameters["port"]
        self._result_queue: Queue[Result] = Queue(maxsize=5)
        self._producer = None


        self._app = FastAPI()

        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )


        self._app.mount("/static", StaticFiles(directory="api/static"), name="static")
        self._templates = Jinja2Templates(directory="./api/templates")

        self._configure_routes()

        self._server_thread = threading.Thread(target=self._run_server)
        self._server = None
        self._running = False

        logger.info("WebServer initialized.")
        self.start()

    def _configure_routes(self):
        logger.info("Configuring FastAPI routes...")

        @self._app.get("/config")
        def get_config():
            config = ConfigManager().get_config()
            return JSONResponse(content=config)

        @self._app.post("/source")
        def set_source(data: dict = Body(...)):
            if self._producer is None:
                return JSONResponse(
                    content={"status": "error", "message": "Kafka producer not available"},
                    status_code=500,
                )
            source_val = data.get("source")
            if source_val:
                self._producer.send(
                    "pipeline-settings",
                    {"setting": "source", "value": source_val},
                )
                self._producer.flush()
                return JSONResponse(content={"status": "ok", "source": source_val})
            return JSONResponse(
                content={"status": "error", "message": "No sources provided"}, status_code=400
            )

        @self._app.post("/sinks")
        def set_sinks(data: dict = Body(...)):
            if self._producer is None:
                return JSONResponse(
                    content={"status": "error", "message": "Kafka producer not available"},
                    status_code=500,
                )
            sinks_val = data.get("sinks")
            if sinks_val:
                self._producer.send(
                    "pipeline-settings",
                    {"setting": "sinks", "value": sinks_val},
                )
                self._producer.flush()
                return JSONResponse(content={"status": "ok", "sinks": sinks_val})
            return JSONResponse(
                content={"status": "error", "message": "No sinks provided"}, status_code=400
            )

        @self._app.get("/video_feed")
        def video_feed():
            return StreamingResponse(
                self._generate_frame(),
                media_type="multipart/x-mixed-replace; boundary=frame",
            )

        @self._app.get("/")
        def index(request: Request):
            return self._templates.TemplateResponse("index.html", {"request": request})

        logger.info("Routes configured.")

    def _generate_frame(self):
        while self._running:
            try:
                logger.info("get new frame")
                result = self._result_queue.get()
                logger.info("new frame received")
            except Empty:
                continue

            if not result:
                continue

            image = result.frame.frame

            for p in result.predictions:
                if p.annotate:
                    for data in p.infer_data:
                        image = data.draw(image)
            success, encoded_image = cv2.imencode(".jpg", image)
            if not success:
                logger.error("Error encoding frame")
                continue

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" +
                bytearray(encoded_image) +
                b"\r\n"
            )

    def _run_server(self):
        logger.info("Starting Uvicorn server...")
        self._running = True

        config = uvicorn.Config(
            self._app,
            host=self._host,
            port=self._port,
            log_level="info",
        )
        self._server = uvicorn.Server(config)

        logger.info(f"Server starting on {self._host}:{self._port}...")
        self._server.run()

    def start(self):
        logger.info("Starting server (FastAPI + Uvicorn)...")
        if self._server_thread.is_alive():
            logger.info("Server is already running.")
            return

        self._server_thread = threading.Thread(target=self._run_server, daemon=True)
        logger.info("Starting server thread...")
        self._server_thread.start()

    def stop(self):
        logger.info("Stopping server...")

        if not self._server:
            logger.info("Server is not running.")
            return

        logger.info("Signaling server to stop...")
        self._running = False

        self._server.should_exit = True

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

    def release(self):
        logger.info("Releasing resources...")
        self.stop()
