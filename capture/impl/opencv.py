import time
import logging
from datetime import datetime


from capture.interface.source import Source
from model.frame import Frame

logger = logging.getLogger(__name__)

class OpenCVCamera(Source):

    NAME = "cv"

    def __init__(self, device: str = "/dev/video0", width: int = 640, height: int = 480):  # Improved typing
        logger.info("Initializing OpenCVCamera")
        import cv2
        self.cv2 = cv2
        self._capture = self.cv2.VideoCapture(device)
        self._capture.set(self.cv2.CAP_PROP_FRAME_WIDTH, width)
        self._capture.set(self.cv2.CAP_PROP_FRAME_HEIGHT, height)
        time.sleep(1)  # Ensure the camera initializes properly


    def get_frame(self) -> Frame:
        logger.debug("Getting frame from OpenCVCamera")
        timestamp = datetime.now()
        frame = None
        if self._capture is None:
            logger.warning("OpenCVCamera not initialized")
        else:
            ret, frame = self._capture.read()
            if not ret:
                logger.warning("Failed to retrieve frame from OpenCVCamera")
        return Frame(
            frame_id=f"{self.NAME}_{timestamp}",
            source_id=self.NAME,
            frame=frame,
            timestamp=timestamp)


    def release(self):
        if self._capture is not None:
            logger.info("Releasing OpenCVCamera")
            self._capture.release()
            self._capture = None


    def get_name(self) -> str:
        logger.debug("Getting source name for OpenCVCamera")
        return self.NAME
