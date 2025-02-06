import logging
import threading
from queue import Queue, Empty
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from sink.base.sink import Sink
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

        #BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        #assets_path = os.path.join(BASE_DIR, "static/assets")
        self._app.mount("/static", StaticFiles(directory="static/assets"), name="static")
        self._templates = Jinja2Templates(directory="./static/templates/stream/")

        self._app.get("/video_feed")(self.video_feed)
        self._app.get("/")(self.index)
        self._stop_event = threading.Event()
        self._server_thread = threading.Thread(target=self._run_server)
        self.start()

    def _generate_frame(self):
        while not self._stop_event.is_set():
            try:
                result = self._result_queue.get(timeout=1)
            except Empty:
                continue

            if result is None:
                continue

            image = result.frame.image
            for d in result.detections:
                image = d.draw(image)
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
        import uvicorn
        uvicorn.run(self._app, host=self._host, port=self._port, log_level="info")


    def start(self):
        self._stop_event.clear()
        if not self._server_thread.is_alive():
            self._server_thread = threading.Thread(target=self._run_server, daemon=True)
            self._server_thread.start()


    def stop(self):
        self._stop_event.set()


    def put(self, result):
        if self._result_queue.full():
            self._result_queue.get_nowait()
        self._result_queue.put(result)


    def release(self):
        self.stop()
        logger.info("VideoFeedServer released")

    def init(self):
        self.start()
        logger.info("VideoFeedServer initialized")
