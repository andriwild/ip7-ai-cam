import logging

from ultralytics import YOLO
from ultralytics.engine.results import Results

from ml.interface.operation import Operation
from model.frame import Frame
from model.result import Result, BoxResult
from model.resultWrapper import BoxWrapper

logger = logging.getLogger(__name__)

class UlObjectDetection(Operation):

    def __init__(self, name: str,  model_path: str = "resources/ml_models/yolo11n.onnx", confidence: float = 0.5):
        logger.info(f"Initializing UlObjectDetection with name {name}")
        self._name = name
        self._model = YOLO(model_path)
        self._confidence = confidence
        logger.info(f"Loaded model from {model_path} with confidence {confidence}")


    def process(self, frame: Frame) -> Result:
        logger.info(f"Processing frame {frame.frame_id}")
        results: list[Results] = self._model(frame.frame, verbose=False, conf=self._confidence)
        box_wrapper = BoxWrapper.from_ultralytics(results[0])
        speed : dict[str, float | None] = results[0].speed
        logger.info(f"Processed frame {frame.frame_id} in {speed['inference']} seconds")
        return BoxResult(
            frame_id = frame.frame_id,
            frame = frame.frame,
            inference_time=speed["inference"],
            preprocess_time=speed["preprocess"],
            postprocess_time=speed["postprocess"],
            boxes=box_wrapper
        )

    def get_name(self) -> str:
        return self._name
