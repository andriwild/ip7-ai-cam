import logging
import cv2
import time

from capture.interface.source import Source
from model.capture import Capture

logger = logging.getLogger(__name__)


class ImageGenerator(Source):

    NAME = "image"

    def __init__(self, width: int = 640, height: int = 480):
        logger.info("Initializing ImageGenerator")
        self._width = width
        self._height = height
        self._frame = cv2.imread("image.jpg")
        self._frame = cv2.resize(self._frame, (width, height))


    def get_capture(self) -> Capture:
        logger.debug("Getting frame from ImageGenerator")
        time.sleep(0.2)
        self._frame = cv2.imread("image.jpg")
        self._frame = cv2.resize(self._frame, (self._width, self._height))
        return Capture(self._frame)


    def release(self):
        logger.info("Releasing ImageGenerator")


    def get_name(self) -> str:
        logger.debug("Getting source name for ImageGenerator")
        return self.NAME
