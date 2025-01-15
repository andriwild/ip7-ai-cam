from datetime import datetime
from sink.base.sink import Sink
from model.model import Result
import logging

logger = logging.getLogger(__name__)

class TimeMeasurement(Sink):
    def __init__(self, name: str, parameters: dict = {}):
        super().__init__(name)
        self._parameters = parameters
        self._last_frame_time = None
        logger.info("TimeMeasurement initialized")

    def put(self, result: Result) -> None:
        if self._last_frame_time is not None:
            logger.info(datetime.now() -  self._last_frame_time)

        self._last_frame_time = datetime.now()


    def release(self):
        logger.info("TimeMeasurement released")

    def init(self):
        logger.info("TimeMeasurement initialized")
