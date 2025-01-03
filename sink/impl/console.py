from sink.interface.sink import Sink
from pipeline.pipeline import Result
from model.detection import Box
import logging

logger = logging.getLogger(__name__)

class Console(Sink):
    def __init__(self, name: str, parameters: dict):
        super().__init__(name)
        self._parameters = parameters
        logger.info("Console initialized")

    def put(self, result: Result) -> None:
        logger.info(f"Frame {result.frame.frame_id} processed")
        # output_str = ""
        # for prediction in result.predictions:
        #     output_str += f"\nPrediction: {prediction.model_name}\n"
        #     if len(prediction.infer_data) == 0:
        #         output_str += "  No data\n"

        #     for data in prediction.infer_data:
        #         if isinstance(data,Box):
        #             output_str += f"  {data.label} - confidence={data.conf}\n"
        # logger.info(output_str)


    def release(self):
        logger.info("Console released")
