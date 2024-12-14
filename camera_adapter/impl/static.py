import logging
import numpy as np
from time import sleep

from camera_adapter.interface.camera import Camera

logger = logging.getLogger(__name__)

class StaticFrameGenerator(Camera):

    NAME = "static"

    def __init__(self, width=640, height=480):
        self.static_frame = np.random.randint(0, 10, (width, height, 3), dtype=np.uint8)

    def get_frame(self):
        sleep(0.5)
        logger.debug("Getting frame from static frame generator")
        return self.static_frame

    def release(self):
        logger.info("Releasing static frame generator")
        pass

    def get_name(self) -> str:
        logger.debug("Getting camera name for static frame generator")
        return self.NAME

