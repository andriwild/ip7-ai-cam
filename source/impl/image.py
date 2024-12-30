import logging
import time
from datetime import datetime

import cv2

from source.interface.source import Source
from model.frame import Frame

logger = logging.getLogger(__name__)


class ImageGenerator(Source):

    NAME = "static_image"

    def __init__(self, width: int = 640, height: int = 480):
        logger.info("Initializing ImageGenerator")
        self._width = width
        self._height = height


    def get_frame(self) -> Frame:
        logger.debug("Getting frame from ImageGenerator")
        time.sleep(0.2)
        frame = cv2.imread("image.jpg")
        frame = cv2.resize(frame, (self._width, self._height))
        timestamp = datetime.now()
        return Frame(
            frame_id=f"{self.NAME}_{timestamp}",
            source_id=self.NAME,
            frame=frame,
            timestamp=timestamp)


    def release(self):
        logger.info("Releasing ImageGenerator")


    def get_name(self) -> str:
        logger.debug("Getting source name for ImageGenerator")
        return self.NAME
