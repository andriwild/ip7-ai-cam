from ultralytics import YOLO

from ml.interface.operation import Operation
from model.frame import Frame
from model.result import Result
from model.result import KeypointResult
from model.resultWrapper import KeypointWrapper


class UlPose(Operation):

    def __init__(self, model_path: str = "yolo11n-pose.onnx", confidence: float = 0.5):
        self._model = YOLO(model_path)
        self._confidence = confidence

    def process(self, frame: Frame) -> Result:
        results = self._model(frame.frame, verbose=False, conf=self._confidence)
        keypoint_wrapper = KeypointWrapper.from_ultralytics(results[0])
        speed : dict[str, float | None] = results[0].speed
        return KeypointResult(
            frame_id = frame.frame_id,
            frame = frame.frame,
            inference_time=speed["inference"],
            preprocess_time=speed["preprocess"],
            postprocess_time=speed["postprocess"],
            keypoint=keypoint_wrapper
        )

