# https://github.com/poojatambe/Yolov5-inference-on-ONNXRuntime-and-opencv-DNN/blob/main/Yolov5_infer_opencv.py
import onnxruntime as ort
import cv2
import numpy as np
import torch
from typing import List
from model.detection import Box
from step.interface.operation import Operation
import yaml
import logging


logger = logging.getLogger(__name__)

class ONNXInference(Operation):
    def __init__(self, name: str, params):
        """
        Initialize the YOLOv8 ONNX inference.

        :param model_path: Path to the ONNX model file.
        :param input_size: Input size of the model (assumed square).
        :param conf_threshold: Confidence threshold for detections.
        """
        super().__init__(name)
        self.model_path = params.get("model_path")
        print("model path: ", self.model_path)
        self.input_size = 640
        self.conf_threshold = params.get("confidence", 0.5)
        self.nms_threshold = 0.5
        self.model = cv2.dnn.readNetFromONNX(self.model_path)
        label_path= params.get("label_path", "resources/labels/coco.yaml")

        with open(label_path, 'r') as stream:
            self.class_labels = yaml.safe_load(stream)

        logger.info(f"Initalized ONNXInference with model {self.model_path} and confidence {self.conf_threshold}")



    def xywh_to_xywhn(self, xywh, frame_width, frame_height):
        """
        Convert absolute bounding box format (xywh) to normalized format (xywhn).
        
        :param xywh: List or array [x_center, y_center, width, height] in absolute values.
        :param frame_width: Width of the frame/image.
        :param frame_height: Height of the frame/image.
        :return: Normalized bounding box [x_center_norm, y_center_norm, width_norm, height_norm].
        """
        x_center, y_center, width, height = xywh
        x_center_norm = x_center / frame_width
        y_center_norm = y_center / frame_height
        width_norm = width / frame_width
        height_norm = height / frame_height
        return (x_center_norm, y_center_norm, width_norm, height_norm)


    def process(self, frame: np.ndarray) -> List[Box]:
         height, width, _ = frame.shape
         length = max(height, width)

         # Create square padded image
         padded_image = np.zeros((length, length, 3), dtype=np.uint8)
         padded_image[:height, :width] = frame

         # Scale factor for bounding boxes
         scale = length / 640

         # Preprocess the image
         blob = cv2.dnn.blobFromImage(padded_image, scalefactor=1 / 255.0, size=(640, 640), swapRB=True)
         self.model.setInput(blob)

         # Perform inference
         outputs = self.model.forward()
         outputs = np.array([cv2.transpose(outputs[0])])
         rows = outputs.shape[1]

         boxes = []
         confidences = []
         class_ids = []

         for i in range(rows):
             class_scores = outputs[0][i][4:]
             _, max_score, _, (x, max_class_index) = cv2.minMaxLoc(class_scores)
             if max_score >= self.conf_threshold:
                 box = [
                     outputs[0][i][0] - (0.5 * outputs[0][i][2]),
                     outputs[0][i][1] - (0.5 * outputs[0][i][3]),
                     outputs[0][i][2],
                     outputs[0][i][3],
                 ]
                 boxes.append(box)
                 confidences.append(max_score)
                 class_ids.append(max_class_index)

         # Apply NMS
         indices = cv2.dnn.NMSBoxes(boxes, confidences, self.conf_threshold, self.nms_threshold)

         results = []
         for i in indices:
             index = i[0]
             box = boxes[index]

             # Convert to normalized xywhn format
             x_center = (box[0] + box[2] / 2) / length
             y_center = (box[1] + box[3] / 2) / length
             width = box[2] / length
             height = box[3] / length

             xywhn = torch.tensor([x_center, y_center, width, height])
             conf = confidences[index]
             label = class_ids[index]

             results.append(Box(xywhn=xywhn, conf=conf, label=label))

         return results
