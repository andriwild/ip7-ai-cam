import time
import logging
from datetime import datetime

from source.interface.source import Source
from model.frame import Frame

logger = logging.getLogger(__name__)

class PiCamera(Source):

    def __init__(self, name: str, params):
        logger.info("Initializing PiCamera")
        super().__init__(name)
        self._name = name
        self._width = params.get("width", 640)
        self._height = params.get("height", 640)
        from picamera2 import Picamera2
        self._camera = Picamera2()
        self._camera.configure(
            self._camera.create_preview_configuration(
                main={"size": (self._width, self._height), "format": "RGB888"}
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
            frame_id=f"{self._name}_{timestamp}",
            source_id=self._name,
            frame=frame,
            timestamp=timestamp)


    def release(self):
        if self._camera is not None:
            logger.info("Releasing PiCamera")
            self._camera.stop()
            self._camera.close()
            self._camera = None

