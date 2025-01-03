import logging

import numpy as np
from ultralytics import YOLO
from ultralytics.engine.results import Results

from ml.interface.operation import Operation
from model.detection import Box
from model.detection import Detection

logger = logging.getLogger(__name__)


def extract_boxes(result: Results) -> list[Box]:
    ul_boxes = result.boxes

    xywhn = ul_boxes.xywhn  # boxes in [x, y, width, height] normalized format
    conf = ul_boxes.conf if ul_boxes.conf is not None else np.ones(xywhn.shape[0])  # default to 1 if no confidence
    labels = ul_boxes.cls if ul_boxes.cls is not None else [0] * xywhn.shape[0]  # default class 0

    boxes: list[Box] = []
    for (box, score, label) in zip(xywhn, conf, labels):
        boxes.append(Box(xywhn=box, conf=float(score), label=label))
    return boxes


class UlDetect(Operation):

    def __init__(self, name: str, params):
        logger.info(f"Initializing UlObjectDetection with name {name}")
        super().__init__(name)
        self._model_path = params.get("model_path", "./resources/ml_models/yolo11n.onnx")
        self._confidence = params.get("confidence_threshold", 0.5)
        self._model = YOLO(self._model_path)
        logger.info(f"Loaded model from {self._model_path} with confidence {self._confidence}")


    def process(self, frame: np.ndarray) -> list[Detection]:
        results: list[Results] = self._model(frame, verbose=False, conf=self._confidence)
        logger.info(f"ul speed:  {results[0].speed}")
        return extract_boxes(results[0])

