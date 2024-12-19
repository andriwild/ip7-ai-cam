import time
import logging
from datetime import datetime

from capture.interface.source import Source
from model.frame import Frame

logger = logging.getLogger(__name__)

class PiCamera(Source):

    NAME = "pi"

    def __init__(self, width: int = 640, height: int = 480):  # Improved typing
        logger.info("Initializing PiCamera")
        from picamera2 import Picamera2
        self._camera = Picamera2()
        self._camera.configure(
            self._camera.create_preview_configuration(
                main={"size": (width, height), "format": "RGB888"}
            )
        )
        self._camera.start()
        time.sleep(1)  # Ensure the camera initializes properly


    def get_frame(self) -> Frame:
        logger.debug("Getting frame from PiCamera")
        timestamp = datetime.now()
        frame = None
        if self._camera is None:
            logger.warning("PiCamera not initialized")
        else:
            frame = self._camera.capture_array()
        return Frame(
            frame_id=f"{self.NAME}_{timestamp}",
            source_id=self.NAME,
            frame=frame,
            timestamp=timestamp)


    def release(self):
        if self._camera is not None:
            logger.info("Releasing PiCamera")
            self._camera.stop()
            self._camera.close()
            self._camera = None


    def get_name(self) -> str:
        logger.debug("Getting source name for PiCamera")
        return self.NAME
