import logging
import time
import cv2
from cv2 import VideoCapture

from datetime import datetime

from source.interface.source import Source
from model.model import Frame

logger = logging.getLogger(__name__)

class Webcam(Source):
    def __init__(self, name: str, params: dict):
        super().__init__(name)
        self._device = params.get("device", "/dev/video0")
        self._width = params.get("width", 480)
        self._height = params.get("height", 640)
        self._fps = params.get("fps", 30)
        self._capture = None
        self._initialized = False
        logger.info("Webcam created")


    def init(self):
        logger.info("Initializing Webcam")
        self._capture = VideoCapture(self._device)
        self._capture.set(cv2.CAP_PROP_FRAME_WIDTH,  self._width)
        self._capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)

        time.sleep(0.5)  # ensure the camera initializes properly
        self._initialized = True
        logger.info("Webcam initialized")


    def get_frame(self) -> Frame:
        logger.debug("Getting frame from Webcam")

        if self._capture is None:
            logger.warning("Webcam not initialized")
            self.init()

        assert self._capture is not None, "Webcam not initialized when trying to get frame"

        success, frame = self._capture.read()
        timestamp = datetime.now()

        if not success:
            logger.warning("Failed to retrieve frame from Webcam")

        return Frame(
            frame_id=f"{self._name}_{timestamp}",
            source_id=self._name,
            frame=frame,
            timestamp=timestamp)


    def release(self):
        if self._capture is not None:
            logger.info("Releasing Webcam")
            self._capture.release()
            self._capture = None
