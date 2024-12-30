import logging
import time
from datetime import datetime

from source.interface.source import Source
from model.frame import Frame

logger = logging.getLogger(__name__)

class OpenCVCamera(Source):

    def __init__(self, name: str, device: str = "/dev/video0", width: int = 640, height: int = 720):  # Improved typing
        logger.info("Initializing OpenCVCamera")
        self._name = name
        import cv2
        self.cv2 = cv2
        self._device = device
        self._capture = self.cv2.VideoCapture(device)
        self._capture.set(self.cv2.CAP_PROP_FRAME_WIDTH, width)
        self._capture.set(self.cv2.CAP_PROP_FRAME_HEIGHT, height)
        time.sleep(1)  # Ensure the camera initializes properly


    def get_frame(self) -> Frame:
        logger.debug("Getting frame from OpenCVCamera")
        timestamp = datetime.now()
        frame = None
        if self._capture is None:
            self._capture = self.cv2.VideoCapture(self._device)
            time.sleep(1)
            logger.warning("OpenCVCamera not initialized")
        ret, frame = self._capture.read()
        if not ret:
            logger.warning("Failed to retrieve frame from OpenCVCamera")
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
