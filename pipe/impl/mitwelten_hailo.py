from pipe.base.operation import Operation
from picamera2.devices import Hailo
from model.detection import Detection, Box
from model.model import Frame
from pipe.impl.hailoDetect import HailoObjectDetection
from utilities.decorator import Log_time
from utilities.labelLoader import load_labels
from utilities.formatConverter import letterbox
import numpy as np
import cv2
import logging
import time

logger = logging.getLogger(__name__)

class Mitwelten(Operation):
    def __init__(self, name: str, params = {}):
        logger.info(f"Initializing Mitwelten inference with name {name}")
        super().__init__(name)

        pollinator_params     = params.get("pollinator_params", {})
        pollinator_model      = pollinator_params.get("pollinator_model", "./resources/ml_models/yolov8n_pollinator_ep50_v1.hef")
        pollinator_label_path = pollinator_params.get("label_path")
        self._pollinator_input_size = pollinator_params.get("input_size", 640)
        self.pollinator_batch_size = pollinator_params.get("batch_size", 8)

        self.conf_threshold = pollinator_params.get('confidence_threshold', 0.5)
        self.input_size = (640, 640)
        self._pollinator_labels = load_labels(pollinator_label_path)

        self.flower_hailo_model     = HailoObjectDetection('flower_inference', params.get("flower_params", {}))
        self.pollinator_hailo_model = Hailo(pollinator_model, batch_size=self.pollinator_batch_size)
        logger.info(f"Initialized Mitwelten inference with name {name}")
        

    @Log_time("Mitwelten Hailo Inference")
    def process(self, frame: Frame) -> list[Detection]:
        start = time.time()
        result_boxes: list[Box] = []
        flower_detections: list[Box] = self.flower_hailo_model.process(frame)
        result_boxes.extend(flower_detections)

        orig_height, orig_width = frame.image.shape[:2]

        cropped_flowers = []
        letterbox_data = []

        for flower_detection in flower_detections:
            fh = flower_detection.xywhn[3]
            fw = flower_detection.xywhn[2]
            fy = flower_detection.xywhn[1]
            fx = flower_detection.xywhn[0]

            x1 = int((fx - fw/2) * orig_width)
            y1 = int((fy - fh/2) * orig_height)
            x2 = int((fx + fw/2) * orig_width)
            y2 = int((fy + fh/2) * orig_height)

            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(orig_width, x2), min(orig_height, y2)

            cropped_image = frame.image[y1:y2, x1:x2]

            letterboxed_img, ratio, (pad_left, pad_top) = letterbox(cropped_image, (self._pollinator_input_size, self._pollinator_input_size))

            cropped_flowers.append(letterboxed_img)

            letterbox_data.append({
                'ratio': ratio,
                'pad_left': pad_left,
                'pad_top': pad_top,
                'orig_x1': x1,
                'orig_y1': y1,
            })

        result = []
        for i in range(0, len(cropped_flowers), self.pollinator_batch_size):
            sub_batch_frames = cropped_flowers[i : i + self.pollinator_batch_size]
            sub_batch_letterbox_data = letterbox_data[i : i + self.pollinator_batch_size]

            inference_results = self.pollinator_hailo_model.run(sub_batch_frames)

            for j, inference in enumerate(inference_results):
                data     = sub_batch_letterbox_data[j]
                ratio    = data['ratio']
                pad_left = data['pad_left']
                pad_top  = data['pad_top']
                offset_x = data['orig_x1']
                offset_y = data['orig_y1']

                for idx, class_detections in enumerate(inference[0]):
                    for detection in class_detections:
                        if len(detection) >= 5:
                            conf = detection[4]
                            if conf > 0.14:
                                # yxyx (normalized)
                                y1_norm, x1_norm, y2_norm, x2_norm = detection[:4]

                                # calc letterbox size
                                x1_l = x1_norm * self.input_size[0]
                                x2_l = x2_norm * self.input_size[0]
                                y1_l = y1_norm * self.input_size[1]
                                y2_l = y2_norm * self.input_size[1]

                                # remove and rescale padding
                                x1_un = (x1_l - pad_left) / ratio
                                x2_un = (x2_l - pad_left) / ratio
                                y1_un = (y1_l - pad_top)  / ratio
                                y2_un = (y2_l - pad_top)  / ratio

                                # offset for the original coordinates
                                x1_final = x1_un + offset_x
                                x2_final = x2_un + offset_x
                                y1_final = y1_un + offset_y
                                y2_final = y2_un + offset_y

                                # In xywhn
                                x_center = (x1_final + x2_final) / 2
                                y_center = (y1_final + y2_final) / 2
                                w = x2_final - x1_final
                                h = y2_final - y1_final

                                result.append(
                                    Box(
                                        xywhn=(
                                            x_center / orig_width,
                                            y_center / orig_height,
                                            w / orig_width,
                                            h / orig_height
                                        ),
                                        conf=conf,
                                        label=self._pollinator_labels[idx]
                                    )
                                )

        result_boxes.extend(result)

        print(f"{self._name},{len(flower_detections)},{time.time() - start}")

        return result_boxes
