from ultralytics import YOLO

from step.interface.operation import Operation
import numpy as np
from model.detection import Mask, Detection


class UlSeg(Operation):

    def __init__(self, name: str, params):
        super().__init__(name)
        self._model_path = params.get("model_path", "./resources/ml_models/yolo11n-seg.onnx")
        self._model = YOLO(self._model_path)
        self._confidence = params.get("confidence_threshold", 0.5)

    def process(self, frame: np.ndarray) -> list[Detection]:
        results = self._model(frame, verbose=False, conf=self._confidence)
        mask = results[0].masks
        if mask is None:
            mask = []
        return [Mask(masks=mask)]

