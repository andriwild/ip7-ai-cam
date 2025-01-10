import logging
import threading
from queue import Queue, Empty
from fastapi import FastAPI, Body, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from model.config import ConfigManager
from sink.interface.sink import Sink
from fastapi.staticfiles import StaticFiles
import cv2

logger = logging.getLogger(__name__)

class VideoFeedServer(Sink):
    def __init__(self, name: str, params = {}):
        super().__init__(name)

        self._host = params.get("host", "0.0.0.0")
        self._port = params.get("port", 8000)

        self._result_queue: Queue = Queue(maxsize=5)
        self._app = FastAPI()
        self._app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self._app.mount("/static", StaticFiles(directory="api/static"), name="static")
        self._templates = Jinja2Templates(directory="./api/templates/stream/")

        self._app.get("/video_feed")(self.video_feed)
        self._app.get("/")(self.index)
        self._running = False
        self._server_thread = threading.Thread(target=self._run_server)
        self.start()

    def _generate_frame(self):
        while self._running:
            try:
                result = self._result_queue.get(timeout=1)
            except Empty:
                continue

            if result is None:
                continue

            image = result.frame.frame
            for p in result.predictions:
                if p.annotate:
                    for data in p.infer_data:
                        image = data.draw(image)
            success, encoded_image = cv2.imencode(".jpg", image)
            if success:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" +
                    bytearray(encoded_image) +
                    b"\r\n"
                )

    def video_feed(self):
        return StreamingResponse(
            self._generate_frame(),
            media_type="multipart/x-mixed-replace; boundary=frame",
        )

    def index(self, request: Request):
        return self._templates.TemplateResponse("index.html", {"request": request})

    def _run_server(self):
        self._running = True
        import uvicorn
        uvicorn.run(self._app, host=self._host, port=self._port, log_level="info")

    def start(self):
        if not self._server_thread.is_alive():
            self._server_thread = threading.Thread(target=self._run_server, daemon=True)
            self._server_thread.start()

    def stop(self):
        self._running = False
        self._server_thread.join()

    def put(self, result):
        if self._result_queue.full():
            self._result_queue.get_nowait()
        self._result_queue.put(result)

    def release(self):
        self.stop()
        logger.info("VideoFeedServer released")

