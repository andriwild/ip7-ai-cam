from model.result import Result
from sink.interface.sink import Sink
import logging

logger = logging.getLogger(__name__)

class Console(Sink):
    def __init__(self, name: str):
        self._name = name
        logger.info("Console initialized")

    def put(self, result: Result) -> None:
        logger.info(f"Frame {result.frame_id} processed")

    def get_name(self) -> str:
        return self._name

    def release(self):
        logger.info("Console released")
