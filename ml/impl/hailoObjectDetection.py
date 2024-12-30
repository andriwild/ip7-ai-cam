from ml.interface.operation import Operation
from model.frame import Frame
from model.result import Result, BoxResult
from model.resultWrapper import BoxWrapper
from picamera2.devices import Hailo
import cv2

class HailoObjectDetection(Operation):

    def __init__(self, model_path: str ="/usr/share/hailo-models/yolov8s_h8l.hef", confidence: float = 0.5):
        print("init hailo")
        self._model = Hailo(model_path)
        self._confidence = confidence
        model_h, model_w, _ = self._model.get_input_shape()
        print("hailo size: ", model_h, model_w)

    def process(self, frame: Frame) -> Result:
        print("process hailo inference")
        print(frame.frame.shape[1], frame.frame.shape[0])
        frame_r = cv2.resize(frame.frame, (640, 640))
        results = self._model.run(frame_r)
        detections = extract_detections(results, frame.frame.shape[1], frame.frame.shape[0], [0] * 80, threshold=self._confidence)
        print(detections)
        box_wrapper = BoxWrapper()
        return BoxResult(
                frame_id = frame.frame_id,
                frame = frame.frame,
                boxes=box_wrapper
                )

def extract_detections(hailo_output, w, h, class_names, threshold=0.5):
    """Extract detections from the HailoRT-postprocess output."""
    results = []
    for class_id, detections in enumerate(hailo_output):
        for detection in detections:
            score = detection[4]
            if score >= threshold:
                y0, x0, y1, x1 = detection[:4]
                bbox = (int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h))
                results.append([class_names[class_id], bbox, score])
    return results
