import logging

import numpy as np
from ultralytics import YOLO
from ultralytics.engine.results import Results

from model.model import Frame
from pipe.interface.operation import Operation
from model.detection import Box, Detection
from utilities.labelLoader import load_lables_from_file

logger = logging.getLogger(__name__)



class UlDetect(Operation):

    def __init__(self, name: str, params):
        logger.info(f"Initializing UlObjectDetection with name {name}")
        super().__init__(name)
        self._model_path = params.get("model_path", "./resources/ml_models/yolo11n.onnx")
        self._confidence = params.get("confidence_threshold", 0.5)
        self._model = YOLO(self._model_path)
        self._label_path= params.get("lable_path", "./resources/ml_models/coco.txt")
        self._labels = load_lables_from_file(self._label_path)
        logger.info(f"Loaded model from {self._model_path} with confidence {self._confidence}")


    def process(self, frame: Frame) -> list[Detection]:
        results: list[Results] = self._model(frame.image, verbose=False, conf=self._confidence)
        return self._extract_boxes(results)


    def _extract_boxes(self, result: Results) -> list[Box]:

        ul_boxes = result[0].boxes
    
        xywhn = ul_boxes.xywhn  # boxes in [x, y, width, height] normalized format
        conf = ul_boxes.conf if ul_boxes.conf is not None else np.ones(xywhn.shape[0])  # default to 1 if no confidence
        label_idxs = ul_boxes.cls if ul_boxes.cls is not None else [0] * xywhn.shape[0]  # default class 0
    
        boxes: list[Box] = []
        for (box, score, label_idx) in zip(xywhn, conf, label_idxs):
            boxes.append(Box(xywhn=box, conf=float(score), label=self._labels[int(label_idx)]))
        return boxes
