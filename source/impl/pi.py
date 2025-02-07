import time
import logging
from datetime import datetime

from source.base.source import Source
from model.model import Frame
from picamera2 import Picamera2

logger = logging.getLogger(__name__)

class PiCamera(Source):

    def __init__(self, name: str, params):
        logger.info("Initializing PiCamera")
        super().__init__(name)
        self._name = name
        self._width = params.get("width", 640)
        self._height = params.get("height", 640)


    def init(self):
        self._camera = Picamera2()
        self._camera.configure(
            self._camera.create_preview_configuration(
                main={"size": (self._width, self._height), "format": "RGB888"}
            )
        )
        self._camera.video_configuration.controls.FrameRate = 25.0
        self._camera.start()
        time.sleep(0.5)  # ensure the camera initializes properly


    def get_frame(self) -> Frame:
        logger.debug("Getting frame from PiCamera")

        if self._camera is None:
            self.init()
            logger.warning("PiCamera not initialized")

        assert self._camera is not None, "PiCamera not initialized when trying to get frame"

        frame = self._camera.capture_array()
        timestamp = datetime.now()

        return Frame(
            frame_id=f"{self._name}_{timestamp}",
            source_id=self._name,
            image=frame,
            timestamp=timestamp)


    def release(self):
        if self._camera is not None:
            logger.info("Releasing PiCamera")
            self._camera.stop()
            self._camera.close()
            self._camera = None

