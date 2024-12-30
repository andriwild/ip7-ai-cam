import time
import logging
from datetime import datetime

import cv2
import numpy as np

from source.interface.source import Source
from model.frame import Frame
from ml.interface.operation import Operation
from model.result import BoxResult
from model.resultWrapper import BoxWrapper

logger = logging.getLogger(__name__)

class Detection:
    """
    Repräsentiert einen einzelnen Detektions-Output
    """
    def __init__(self, box, category, conf):
        self.box = box         # (x, y, width, height)
        self.category = category
        self.conf = conf

class AiCamera(Source, Operation):

    NAME = "ai"

    def __init__(
        self,
        width: int = 640,
        height: int = 640,
        #model_path: str = "/usr/share/imx500-models/imx500_network_ssd_mobilenetv2_fpnlite_320x320_pp.rpk",
        model_path: str = "resources/ml_models/network.rpk",
        threshold: float = 0.5,
        iou: float = 0.5
    ):
        logger.info("Initializing AiCamera")

        from picamera2 import Picamera2
        from picamera2.devices import IMX500
        from picamera2.devices.imx500 import (NetworkIntrinsics, postprocess_nanodet_detection)

        self._IMX500 = IMX500
        self._postprocess_nanodet_detection = postprocess_nanodet_detection
        self._NetworkIntrinsics = NetworkIntrinsics

        self._model_path = model_path
        self._threshold = threshold
        self._iou = iou

        self._imx500 = self._IMX500(self._model_path)
        self._intrinsics = self._imx500.network_intrinsics
        if not self._intrinsics:
            self._intrinsics = self._NetworkIntrinsics()
            self._intrinsics.task = "object detection"

        self._camera = Picamera2(self._imx500.camera_num)

        self.last_detection = None

        config = self._camera.create_preview_configuration(
            #main={"size": (width, height), "format": "RGB888"},
            main={"format": "RGB888"},
            buffer_count=4,  # Je nach Bedarf mehr Buffer
            controls={"FrameRate": self._intrinsics.inference_rate if self._intrinsics.inference_rate else 10}
        )

        self._camera.start(config)
        time.sleep(1)

        logger.info("AiCamera initialization complete.")

    def get_frame(self) -> Frame:
        """
        Liest das aktuelle Kamerabild als numpy-Array aus, führt eine Inferenz durch (über Metadata),
        zeichnet ggf. gefundene Bounding Boxen ins Bild und gibt ein Frame-Objekt zurück.
        """
        logger.debug("Getting frame from AiCamera")

        metadata = self._camera.capture_metadata()

        detections = self._parse_detections(metadata)

        self.last_detection = self._imx500.get_outputs(metadata, add_batch=True)

        frame_data = self._camera.capture_array("main")

        frame_data_annotated = self._draw_detections(frame_data, detections)

        timestamp = datetime.now()
        return Frame(
            frame_id=f"{self.NAME}_{timestamp}",
            source_id=self.NAME,
            frame=frame_data_annotated,
            timestamp=timestamp
        )

    def process(self, frame: Frame):
        boxes = BoxWrapper(boxes=[])
        if self.last_detection is not None:
            boxes = BoxWrapper.from_ai_cam(self.last_detection)

        return BoxResult(
                frame.frame_id, 
                frame.frame,
                boxes=boxes
                )


    def _parse_detections(self, metadata: dict):
        if metadata is None:
            return []

        np_outputs = self._imx500.get_outputs(metadata, add_batch=True)
        if np_outputs is None:
            return []

        # [0] -> Boxes, [1] -> Scores, [2] -> Classes
        boxes, scores, classes = np_outputs[0][0], np_outputs[1][0], np_outputs[2][0]

        valid_indices = np.where(scores >= self._threshold)[0]
        boxes   = boxes[valid_indices]
        scores  = scores[valid_indices]
        classes = classes[valid_indices]


        img_h, img_w = self._camera.stream_configuration("main")["size"][::-1]
        print("frame size: ", img_h, img_w)
        # img_h = 640
        # img_w = 640

        detections = []
        for (y0, x0, y1, x1), score, category in zip(boxes, scores, classes):
            # Auf Pixel skalieren
            top_left_y = int(y0 * img_h)
            top_left_x = int(x0 * img_w)
            br_y       = int(y1 * img_h)
            br_x       = int(x1 * img_w)

            width_box  = br_x - top_left_x
            height_box = br_y - top_left_y

            detections.append(
                Detection(
                    box=(top_left_x, top_left_y, width_box, height_box),
                    category=int(category),
                    conf=float(score)
                )
            )

        return detections

    def _draw_detections(self, frame_data: np.ndarray, detections: list) -> np.ndarray:
        labels = self._intrinsics.labels or []
        overlay = frame_data.copy()

        for detection in detections:
            x, y, w, h = detection.box
            category_text = ""
            if detection.category < len(labels) and labels[detection.category]:
                category_text = labels[detection.category]
            else:
                category_text = f"ID {detection.category}"

            label = f"{category_text} ({detection.conf:.2f})"

            cv2.rectangle(
                overlay,
                (x, y),
                (x + w, y + h),
                color=(255, 255, 255),
                thickness=2
            )

            (text_width, text_height), baseline = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
            )
            text_x = x + 5
            text_y = max(y + 15, 15)

            cv2.rectangle(
                overlay,
                (text_x, text_y - text_height),
                (text_x + text_width, text_y + baseline),
                (255, 255, 255),
                -1  # filled
            )
            alpha = 0.4
            cv2.addWeighted(overlay, alpha, frame_data, 1 - alpha, 0, frame_data)

            cv2.putText(
                frame_data, label, (text_x, text_y),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1
            )

        return frame_data

    def release(self):
        """
        Gibt die Kamera-Ressourcen frei.
        """
        if self._camera is not None:
            logger.info("Releasing AiCamera")
            self._camera.stop()
            self._camera.close()
            self._camera = None
            self._imx500 = None


    def get_name(self) -> str:
        logger.debug("Getting source name for AiCamera")
        return self.NAME
