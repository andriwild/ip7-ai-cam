from sink.interface.sink import Sink
from model.model import Result
import logging

logger = logging.getLogger(__name__)

class Console(Sink):
    def __init__(self, name: str, parameters: dict = {}):
        super().__init__(name)
        self._parameters = parameters
        logger.info("Console initialized")

    def put(self, result: Result) -> None:
        logger.info(f"Frame {result.frame.frame_id} processed")
        output_str = ""
        if result.detections:
            for det in result.detections:
                output_str += f"{det}"
        else:
            output_str = "No detections"

        logger.info(output_str)


    def release(self):
        logger.info("Console released")

    def init(self):
        logger.info("Console initialized")
