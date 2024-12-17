import logging
import numpy as np
import cv2
import time

from capture.interface.source import Source

logger = logging.getLogger(__name__)


class ImageGenerator(Source):

    NAME = "image"

    def __init__(self, width: int = 640, height: int = 480):
        logger.info("Initializing ImageGenerator")
        self._width = width
        self._height = height
        self._frame = cv2.imread("image.jpg")
        self._frame = cv2.resize(self._frame, (width, height))


    def get_frame(self):
        logger.debug("Getting frame from ImageGenerator")
        time.sleep(0.2)
        return self._frame


    def release(self):
        logger.info("Releasing ImageGenerator")


    def get_name(self) -> str:
        logger.debug("Getting source name for ImageGenerator")
        return self.NAME
