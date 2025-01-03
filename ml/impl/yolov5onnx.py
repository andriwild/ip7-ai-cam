import cv2
import numpy as np
from ml.interface.operation import Operation
from model.detection import Box
from utilities.formatConverter import letterbox


class Yolov5onnx(Operation):
    def __init__(self, name: str, params):
        super().__init__(name)
        self.conf_threshold = params.get('confidence_threshold', 0.5)
        self.score_threshold=0.25
        self.nms_threshold=params.get('nms_threshold', 0.5)
        self.model= params.get("model_path")
        self.classes_file= params.get("lable_path")
        self.net = cv2.dnn.readNetFromONNX(self.model)
        self.classes= self.class_name()
        self.input_size= (640, 640)
         

    def class_name(self):
        classes=[]
        file= open(self.classes_file,'r')
        while True:
            name=file.readline().strip('\n')
            classes.append(name)
            if not name:
                break
        return classes

    def process(self, frame: np.ndarray) -> list[Box]:
        h_img, w_img = frame.shape[:2]
        lb_img, ratio, (pad_left, pad_top) = letterbox(frame, self.input_size)
        blob = cv2.dnn.blobFromImage(lb_img, 1/255.0, self.input_size, (0, 0, 0), swapRB=True, crop=False)
        self.net.setInput(blob)
        out = self.net.forward()

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

