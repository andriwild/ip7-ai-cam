from model.result import Result
from sink.interface.sink import Sink
import logging

logger = logging.getLogger(__name__)

class Console(Sink):
    def __init__(self, name: str, parameters: dict):
        super().__init__(name)
        self._parameters = parameters
        logger.info("Console initialized")

    def put(self, result: Result) -> None:
        logger.info(f"Frame {result.frame_id} processed")

    def release(self):
        logger.info("Console released")
