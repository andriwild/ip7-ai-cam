from pipe.base.operation import Operation
from pprint import pprint
from model.model import Frame
from model.detection import Detection, Box
import logging
from utilities.formatConverter import letterbox
from utilities.labelLoader import load_labels
from pathlib import Path
from termcolor import cprint
from utilities.hailo.object_detection import infer
from utilities.hailo.utils import load_input_images, validate_images

from pathlib import Path
from PIL import Image
import numpy as np
from hailo_platform import HEF, VDevice, FormatType, HailoSchedulingAlgorithm

logger = logging.getLogger(__name__)



def extract_detections(raw_output, confidence_threshold=0.5):
    detections = []
    raw_data = raw_output['yolov8s/yolov8_nms_postprocess']
    num_detections = int(raw_data[0])  # First value is the number of detections

    for i in range(num_detections):
        offset = 1 + i * 7  # Each detection is 7 values: class, score, bbox (x1, y1, x2, y2)
        class_id = int(raw_data[offset])
        score = raw_data[offset + 1]
        bbox = raw_data[offset + 2:offset + 6]

        if score >= confidence_threshold:
            detections.append({
                "class_id": class_id,
                "bbox": {
                    "x1": float(bbox[0]),
                    "y1": float(bbox[1]),
                    "x2": float(bbox[2]),
                    "y2": float(bbox[3]),
                }
            })

    return detections

class HailoObjectDetection(Operation):

    def __init__(self, name: str, params):
        super().__init__(name)

        model= params.get("model_path", "./resources/ml_models/flower_n_hailo8l.hef")
        label_path= params.get("label_path")
        self._labels = load_labels(label_path)
        self._confidence = params.get("confidence", 0.7)
        self.conf_threshold = params.get('confidence_threshold', 0.5)
        self.score_threshold = params.get('score_threshold', 0.25)
        self.nms_threshold = params.get('nms_threshold', 0.5)
        self.input_size = (640, 640)

        self.hef = HEF(model)
        params = VDevice.create_params()
        params.scheduling_algorithm = HailoSchedulingAlgorithm.ROUND_ROBIN
        self.target = VDevice(params)

        self.infer_model = self.target.create_infer_model(model)
        self.input_shape = self.hef.get_input_vstream_infos()[0].shape
        self.output_buffers = self._prepare_output_buffers()

    def _prepare_output_buffers(self):
        output_info = self.hef.get_output_vstream_infos()
        return {
            output.name: np.empty(
                self.infer_model.output(output.name).shape,
                dtype=np.float32
            )
            for output in output_info
        }


    def process(self, frame: Frame) -> list[Detection]:
        preprocessed_image = letterbox(frame.image)

        configured_model = self.infer_model.configure()


        bindings = configured_model.create_bindings(
            output_buffers=self.output_buffers
        )
        # 2) Input-Bild setzen
        bindings.input().set_buffer(preprocessed_image)
        # 3) Infer durchführen
        configured_model.run([bindings], timeout=1000)
        # 4) Kopie der Ergebnisse anfertigen und zurückgeben
        r = {
            name: np.copy(buffer)
            for name, buffer in self.output_buffers.items()
        }
        pprint(extract_detections(r, self.conf_threshold))
        return []

