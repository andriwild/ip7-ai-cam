import time
import logging

from camera_adapter.interface.camera import Camera

logger = logging.getLogger(__name__)

class OpenCVCamera(Camera):

    NAME = "cv"

    def __init__(self, device: str = "/dev/video0", width: int = 640, height: int = 480):  # Improved typing
        logger.info("Initializing OpenCVCamera")
        import cv2
        self.cv2 = cv2
        self._capture = self.cv2.VideoCapture(device)
        self._capture.set(self.cv2.CAP_PROP_FRAME_WIDTH, width)
        self._capture.set(self.cv2.CAP_PROP_FRAME_HEIGHT, height)
        time.sleep(1)  # Ensure the camera initializes properly

    def get_frame(self):
        logger.debug("Getting frame from OpenCVCamera")
        ret, frame = self._capture.read()
        if not ret:
            logger.warning("Failed to retrieve frame from OpenCVCamera")
            return None
        return self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2RGB)

    def release(self):
        if self._capture is not None:
            logger.info("Releasing OpenCVCamera")
            self._capture.release()
            self._capture = None

    def get_name(self) -> str:
        logger.debug("Getting camera name for OpenCVCamera")
        return self.NAME
