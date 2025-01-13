from datetime import datetime
from sink.interface.sink import Sink
from model.model import Result
import logging

logger = logging.getLogger(__name__)

class TimeMeasurement(Sink):
    def __init__(self, name: str, parameters: dict = {}):
        super().__init__(name)
        self._parameters = parameters
        logger.info("TimeMeasurement initialized")

    def put(self, result: Result) -> None:
        logger.info(datetime.now() -  result.frame.timestamp)


    def release(self):
        logger.info("TimeMeasurement released")

    def init(self):
        logger.info("TimeMeasurement initialized")
