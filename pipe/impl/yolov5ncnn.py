import ncnn
import cv2
import numpy as np
from model.detection import Box
from model.model import Frame
from utilities.labelLoader import load_labels
from pipe.base.operation import Operation
import logging

logger = logging.getLogger(__name__)

class Yolov5ncnn(Operation):
    def __init__(self, name: str, params):
        logger.info(f"Initializing NCNNInference")
        super().__init__(name)

        self.conf_threshold = params.get('confidence_threshold', 0.5)
        self.nms_threshold=params.get('nms_threshold', 0.5)
        self.classes_file= params.get("label_path")
        size = params.get("input_size", 640)
        self.input_size= (size, size)
        self.classes = load_labels(self.classes_file)

        self._net = ncnn.Net()
        self._net.opt.use_vulkan_compute = params.get("use_gpu", False)
        self._net.opt.num_threads = params.get("num_threads", 4)

        param_file = params.get("param_file ", "resources/ml_models/flower_n_sim.ncnn.param")
        bin_file = params.get("bin_file", "resources/ml_models/flower_n_sim.ncnn.bin")

        self._net.load_param(param_file)
        self._net.load_model(bin_file)
        logger.info(f"Initialized NCNNInference with confidence {self.conf_threshold}")



    def process(self, frame: Frame) -> list[Box]:

        height, width, _ = frame.image.shape
        length = max(height, width)
    
        padded_image = np.zeros((length, length, 3), dtype=np.uint8)
        padded_image[:height, :width] = frame.image
    
        target_size = self.input_size[0]
        scale = length / float(target_size)
    
        mat_in = ncnn.Mat.from_pixels_resize(
            padded_image,
            ncnn.Mat.PixelType.PIXEL_BGR2RGB,
            length,
            length, 
            target_size,
            target_size
        )
        mat_in.substract_mean_normalize([0.0, 0.0, 0.0], [1/255.0, 1/255.0, 1/255.0])
    
        ex = self._net.create_extractor()
        ex.input("in0", mat_in)
    
        ret, mat_out = ex.extract("out0")
        if ret != 0:
            logger.error("Error during inference")
            return []
    
        out_np = np.array(mat_out)
    
        boxes = []
        confidences = []
        class_ids = []
    
        num_rows = out_np.shape[0]  # N
        for i in range(num_rows):
            row = out_np[i]
            cx, cy, w, h = row[0], row[1], row[2], row[3]
            obj_conf = row[4]
            class_conf = row[5:]  # alle Klassen
    
            class_id = np.argmax(class_conf)
            best_class_score = class_conf[class_id]
            score = obj_conf * best_class_score
    
            if score >= self.conf_threshold:
                x1 = cx - (w / 2)
                y1 = cy - (h / 2)
                box = [x1, y1, w, h]
    
                boxes.append(box)
                confidences.append(float(score))
                class_ids.append(int(class_id))
    
        indices = cv2.dnn.NMSBoxes(boxes, confidences, self.conf_threshold, self.nms_threshold)
        indices = np.array(indices).flatten()
        
        results = []
        for idx in indices:
            x, y, w, h = boxes[idx]
            x_center = (x + w / 2) * scale
            y_center = (y + h / 2) * scale
            w_ = w * scale
            h_ = h * scale
    
            x_center_n = x_center / width 
            y_center_n = y_center / height 
            w_n = w_ / width
            h_n = h_ / height
    
            xywhn = np.array([x_center_n, y_center_n, w_n, h_n])
            conf = confidences[idx]
            label = class_ids[idx]
    
            results.append(Box(xywhn=xywhn, conf=conf, label=label))
    
        return results
    
