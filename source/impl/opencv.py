import logging
import time
from datetime import datetime

from source.interface.source import Source
from model.frame import Frame

logger = logging.getLogger(__name__)

class OpenCVCamera(Source):

    def __init__(self, name: str, params = {}):
        logger.info("Initializing OpenCVCamera")
        super().__init__(name)

        self._name = name
        import cv2
        self.cv2 = cv2
        self._device = params.get("device", "/dev/video0")
        self._capture = self.cv2.VideoCapture(self._device)
        self._capture.set(self.cv2.CAP_PROP_FRAME_WIDTH, params.get("width", 640))
        self._capture.set(self.cv2.CAP_PROP_FRAME_HEIGHT, params.get("height", 640))
        time.sleep(0.5)  # Ensure the camera initializes properly
        logger.info("OpenCVCamera initialized")


    def get_frame(self) -> Frame:
        logger.debug("Getting frame from OpenCVCamera")
        timestamp = datetime.now()
        if self._capture is None:
            logger.warning("OpenCVCamera not initialized")
            self._capture = self.cv2.VideoCapture(self._device)
            time.sleep(1)
        ret, frame = self._capture.read()
        if not ret:
            logger.warning("Failed to retrieve frame from OpenCVCamera")
            time.sleep(1)
        return Frame(
            frame_id=f"{self._name}_{timestamp}",
            source_id=self._name,
            frame=frame,
            timestamp=timestamp)


    def release(self):
        if self._capture is not None:
            logger.info("Releasing OpenCVCamera")
            self._capture.release()
            self._capture = None


    def get_name(self) -> str:
        logger.debug("Getting source name for OpenCVCamera")
        return self._name
