from ultralytics import YOLO

from controller.interfaces.operation import Operation
from model.frame import Frame
from model.result import Result, BoxResult
from model.resultWrapper import BoxWrapper
from ultralytics.engine.results import Results


class UlObjectDetection(Operation):

    def __init__(self, model_path: str = "resources/ml_models/yolo11n.onnx", confidence: float = 0.5):
        self._model = YOLO(model_path)
        self._confidence = confidence

    def process(self, frame: Frame) -> Result:
        results: list[Results] = self._model(frame.frame, verbose=False, conf=self._confidence)
        box_wrapper = BoxWrapper.from_ultralytics(results[0])
        speed : dict[str, float | None] = results[0].speed
        return BoxResult(
            frame_id = frame.frame_id,
            frame = frame.frame,
            inference_time=speed["inference"],
            preprocess_time=speed["preprocess"],
            postprocess_time=speed["postprocess"],
            boxes=box_wrapper
        )

    def get_name(self) -> str:
        return "Ultralytics Object Detection"
