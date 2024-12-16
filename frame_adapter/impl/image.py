import logging
import numpy as np
import cv2
import time

from frame_adapter.interface.camera import Camera

logger = logging.getLogger(__name__)


class ImageGenerator(Camera):

    NAME = "image"

    def __init__(self, width: int = 640, height: int = 480):
        logger.info("Initializing ImageGenerator")
        self._width = width
        self._height = height
        self._frame = cv2.imread("image.jpg")
        self._frame = cv2.resize(self._frame, (width, height))


    def get_frame(self):
        logger.debug("Getting frame from ImageGenerator")
        return self._frame


    def release(self):
        logger.info("Releasing ImageGenerator")


    def get_name(self) -> str:
        logger.debug("Getting camera name for ImageGenerator")
        return self.NAME
