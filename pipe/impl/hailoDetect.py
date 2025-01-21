from pipe.base.operation import Operation
from model.model import Frame
from model.detection import Detection, Box
from picamera2.devices import Hailo
import cv2
import logging
import numpy as np
from utilities.labelLoader import load_labels
from utilities.formatConverter import yxyxn_to_xywhn, letterbox


logger = logging.getLogger(__name__)

class HailoObjectDetection(Operation):

    def __init__(self, name: str, params):
        super().__init__(name)

        model= params.get("model_path", "./resources/ml_models/flower_n_hailo8l.hef")
        label_path= params.get("label_path")
        self._labels = load_labels(label_path)
        self._model = Hailo(model)
        self._confidence = params.get("confidence", 0.7)
        self.conf_threshold = params.get('confidence_threshold', 0.5)
        self.score_threshold = params.get('score_threshold', 0.25)
        self.nms_threshold = params.get('nms_threshold', 0.5)
        self.input_size = (640, 640)


    def process(self, frame: Frame) -> list[Detection]:
        #frame_r = cv2.resize(frame.image, (640, 640))
        #results = self._model.run(frame_r)
        #detections = extract_detections(results, self._labels, self._confidence)
        #return detections
        h_img, w_img = frame.image.shape[:2]
        lb_img, ratio, (pad_left, pad_top) = letterbox(frame.image, self.input_size)

        out = self._model.run(lb_img)


        bboxes, confidences, class_ids = [], [], []
        n_detections = out.shape[1]
        for i in range(n_detections):
            det = out[0][i]
            conf = det[4]
            if conf >= self.conf_threshold:
                scores = det[5:]
                cls_id = np.argmax(scores)
                if scores[cls_id] >= self.score_threshold:
                    cx, cy, w, h = det[0], det[1], det[2], det[3]
                    x = cx - (w / 2)
                    y = cy - (h / 2)
                    bboxes.append([x, y, w, h])
                    confidences.append(float(conf))
                    class_ids.append(cls_id)

        indices = cv2.dnn.NMSBoxes(bboxes, confidences, self.conf_threshold, self.nms_threshold)
        detections = []
        if len(indices) > 0:
            for idx in indices.flatten():
                x, y, w, h = bboxes[idx]
                c = confidences[idx]
                cid = class_ids[idx]
                # Undo letterbox
                x_ol = (x - pad_left) / ratio
                y_ol = (y - pad_top) / ratio
                w_ol = w / ratio
                h_ol = h / ratio
                # Convert to center and normalize
                cx_ol = x_ol + w_ol / 2
                cy_ol = y_ol + h_ol / 2
                cx_n = cx_ol / w_img
                cy_n = cy_ol / h_img
                w_n = w_ol / w_img
                h_n = h_ol / h_img
                detections.append(Box((cx_n, cy_n, w_n, h_n), c, self.classes[cid]))

        return detections


        

# def extract_detections(hailo_output, labels, threshold=0.5):
#     boxes = []
#     for class_id, detections in enumerate(hailo_output):
#         for detection in detections:
#             score = detection[4]
#             if score >= threshold:
#                 y0, x0, y1, x1 = detection[:4]
#                 xywhn = yxyxn_to_xywhn(y0, x0, y1, x1)
#                 boxes.append(Box(xywhn=xywhn, conf=score, label=labels[class_id]))
#     return boxes
