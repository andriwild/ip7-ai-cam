from ml.interface.operation import Operation
from model.capture import Capture
import numpy as np
import cv2
import yaml
import logging

logger = logging.getLogger(__name__)

class BoxAnnotator(Operation):

    LABEL_PATH = "resources/labels"

    def __init__(self):
        with open(f"{self.LABEL_PATH}/coco.yaml", 'r') as stream:
            self.cooc_labels = yaml.safe_load(stream)
            logger.info(f"Labels loaded")


    def process(self, capture: Capture) -> Capture:
        frame = capture.get_frame()
        boxes = capture.get_boxes()

        if frame is None or boxes is None or boxes.xywhn is None:
            return capture

        height, width = frame.shape[:2]
        xywhn = boxes.xywhn
        conf = boxes.conf if boxes.conf is not None else np.ones(xywhn.shape[0])  # default to 1 if no confidence
        cls = boxes.cls if boxes.cls is not None else [0] * xywhn.shape[0]  # default class 0

        def map_conf_to_color(conf):
            red = int(255 * (1 - conf))
            green = int(255 * conf)
            return (0, green, red)  # BGR

        for _i, (box, score, label) in enumerate(zip(xywhn, conf, cls)):
            x_center, y_center, w, h = box
            x1 = int((x_center - w / 2) * width)
            y1 = int((y_center - h / 2) * height)
            x2 = int((x_center + w / 2) * width)
            y2 = int((y_center + h / 2) * height)

            def map_to_label(label):
                return self.cooc_labels["names"][int(label)]

            color = map_conf_to_color(score)
            label_text = f"Class {map_to_label(int(label))}: {score:.2f}"

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            break

        capture.set_frame(frame)
        return capture
