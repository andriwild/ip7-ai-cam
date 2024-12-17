import time
import logging

from capture.interface.source import Source

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


    def get_frame(self):
        logger.debug("Getting frame from PiCamera")
        return self._camera.capture_array()


    def release(self):
        if self._camera is not None:
            logger.info("Releasing PiCamera")
            self._camera.stop()
            self._camera.close()
            self._camera = None


    def get_name(self) -> str:
        logger.debug("Getting source name for PiCamera")
        return self.NAME
