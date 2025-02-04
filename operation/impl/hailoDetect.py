from operation.base.operation import Operation
from model.model import Frame
from model.detection import Detection, Box
from picamera2.devices import Hailo
import logging
from utilities.labelLoader import load_labels
from utilities.formatConverter import letterbox


logger = logging.getLogger(__name__)

class HailoObjectDetection(Operation):

    def __init__(self, name: str, params):
        super().__init__(name)

        model= params.get("model_path", "./resources/ml_models/flower_n_hailo8l.hef")
        label_path= params.get("label_path")
        self._labels = load_labels(label_path)
        self._model = Hailo(model)
        self.conf_threshold = params.get('confidence_threshold', 0.5)
        self.input_size = (640, 640)


    def process(self, frame: Frame) -> list[Detection]:
        h_img, w_img = frame.image.shape[:2]
        lb_img, ratio, (pad_left, pad_top) = letterbox(frame.image, self.input_size)
    
        inference_results = self._model.run(lb_img)  # returns a list of inference results (multiple images)
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
                   if len(detection) >= 5:  # detection present
                       if detection[4] > self.conf_threshold:
                           # Extract normalized yxyx coordinates
                           y1_norm, x1_norm, y2_norm, x2_norm = detection[:4]
    
                           # Denormalize to letterboxed image dimensions
                           y1 = y1_norm * self.input_size[1]
                           x1 = x1_norm * self.input_size[0]
                           y2 = y2_norm * self.input_size[1]
                           x2 = x2_norm * self.input_size[0]
    
                           # Remove padding and scale back to original image size
                           x1 = (x1 - pad_left) / ratio
                           x2 = (x2 - pad_left) / ratio
                           y1 = (y1 - pad_top) / ratio
                           y2 = (y2 - pad_top) / ratio
    
                           # Convert yxyx to xywhn format in the original image dimensions
                           x_center = (x1 + x2) / 2
                           y_center = (y1 + y2) / 2
                           width = x2 - x1
                           height = y2 - y1
    
                           # Normalize to original image dimensions
                           result.append(
                               Box(
                                   xywhn=(
                                       x_center / w_img,  # Normalize to original width
                                       y_center / h_img,  # Normalize to original height
                                       width / w_img,     # Normalize to original width
                                       height / h_img     # Normalize to original height
                                   ),
                                   conf=detection[4],
                                   label=self._labels[idx]
                               )
                           )
    
        return result
