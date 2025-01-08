from step.interface.operation import Operation
from model.frame import Frame
from model.detection import Detection, Box
from picamera2.devices import Hailo
import cv2
import logging
import numpy as np
import yaml
from utilities.labelLoader import load_lables_from_file
from utilities.formatConverter import yxyxn_to_xywhn

logger = logging.getLogger(__name__)

class HailoObjectDetection(Operation):

    def __init__(self, name: str, params):
        super().__init__(name)

        self._model = Hailo("/usr/share/hailo-models/yolov8s_h8l.hef")
        self._confidence = params.get("confidence", 0.5)
        label_path= params.get("label_path")
        self._labels = load_lables_from_file(label_path)

        model_h, model_w, _ = self._model.get_input_shape()

    def process(self, frame: np.ndarray) -> list[Detection]:
        frame_r = cv2.resize(frame, (640, 640))
        results = self._model.run(frame_r)
        detections = extract_detections(results, self._labels, self._confidence)
        return detections
        

def extract_detections(hailo_output, labels, threshold=0.5):
    boxes = []
    for class_id, detections in enumerate(hailo_output):
        for detection in detections:
            score = detection[4]
            if score >= threshold:
                y0, x0, y1, x1 = detection[:4]
                xywhn = yxyxn_to_xywhn(y0, x0, y1, x1)
                boxes.append(Box(xywhn=xywhn, conf=score, label=labels[class_id]))
    return boxes
