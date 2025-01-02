import logging

from ultralytics import YOLO
from ultralytics.engine.results import Results

from ml.interface.operation import Operation
from model.detection import Detection
from model.detection import Box
import numpy as np

logger = logging.getLogger(__name__)

class UlObjectDetection(Operation):

    def __init__(self, name: str, params):
        logger.info(f"Initializing UlObjectDetection with name {name}")
        self._model_path = "resources/ml_models/yolo11n.onnx"
        self._name = name
        self._model = YOLO(self._model_path)
        self._confidence = params.get("confidence", 0.5)
        logger.info(f"Loaded model from {self._model_path} with confidence {self._confidence}")


    def process(self, frame: np.ndarray) -> list[Detection]:
        results: list[Results] = self._model(frame, verbose=False, conf=self._confidence)
        return self.extract_boxes(results[0])


    def extract_boxes(self, result: Results) -> list[Box]:
        ul_boxes = result.boxes

        xywhn = ul_boxes.xywhn  # boxes in [x, y, width, height] normalized format
        conf = ul_boxes.conf if ul_boxes.conf is not None else np.ones(xywhn.shape[0])  # default to 1 if no confidence
        labels = ul_boxes.cls if ul_boxes.cls is not None else [0] * xywhn.shape[0]  # default class 0

        boxes: list[Box] = []
        for (box, score, label) in zip(xywhn, conf, labels):
            boxes.append(Box(xywhn=box, conf=float(score), label=int(label)))
        return boxes

