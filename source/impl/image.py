import logging
import time
from datetime import datetime

import cv2

from source.interface.source import Source
from model.frame import Frame

logger = logging.getLogger(__name__)


class ImageGenerator(Source):

    def __init__(self, name: str, params):
        logger.info("Initializing ImageGenerator")
        super().__init__(name)
        self._name = name
        self._width = params.get("width", 640)
        self._height = params.get("height", 640)


    def get_frame(self) -> Frame:
        logger.debug("Getting frame from ImageGenerator")
        time.sleep(0.2)
        frame = cv2.imread("image.jpg")
        frame = cv2.resize(frame, (self._width, self._height))
        timestamp = datetime.now()
        return Frame(
            frame_id=f"{self._name}_{timestamp}",
            source_id=self._name,
            frame=frame,
            timestamp=timestamp)


    def release(self):
        logger.info("Releasing ImageGenerator")

