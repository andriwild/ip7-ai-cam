from pipe.base.operation import Operation
from model.model import Frame
from model.detection import Detection, Box
from picamera2.devices import Hailo
import logging
from utilities.labelLoader import load_labels
from utilities.formatConverter import letterbox, yxyx_to_xywhn


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
        h_img, w_img = frame.image.shape[:2]
        lb_img, ratio, (pad_left, pad_top) = letterbox(frame.image, self.input_size)

        inference_results = self._model.run(lb_img) # returns a list of inference results (multiple images)
        result = []

        # Example inference data:
        # [
        #        [   
        #            array([[    0.38879,     0.85377,     0.53032,      1.0008,      0.2549]], dtype=float32), 
        #            array([], shape=(0, 5), dtype=float64), 
        #            array([[    0.38995,     0.85229,     0.53108,      1.0039,     0.31765], [    0.20061,     0.73043,     0.31478,     0.83216,      0.3098]], dtype=float32)
        #        ]
        # ] 

        for inference in inference_results:
           for idx, class_detections in enumerate(inference):
               for detection in class_detections:
                   if len(detection) >= 5: # detection present
                       if detection[4] > self.conf_threshold:
                            result.append(
                                    Box(
                                        xywhn=yxyx_to_xywhn(detection[:4], w_img, h_img), 
                                        conf=detection[4], 
                                        label=self._labels[idx])
                                    )

        print("Result", result)
        return result

