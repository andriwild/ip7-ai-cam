from ultralytics import YOLO

from controller.interfaces.operation import Operation
from model.capture import Capture


class UlPose(Operation):

    def __init__(self, model_path: str = "yolo11n-pose.onnx", confidence: float = 0.5):
        self._model = YOLO(model_path)
        self._confidence = confidence

    def process(self, capture: Capture) -> Capture:
        frame = capture.get_frame()
        if frame is None:
            return capture
        results = self._model(frame, verbose=False, conf=self._confidence)
        capture.add_keypoints(results[0].keypoints)
        return capture
