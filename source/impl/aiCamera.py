import time
import logging
from datetime import datetime

import numpy as np

from source.base.source import Source
from model.model import Frame
from operation.base.operation import Operation
from model.singleton import SingletonMeta
from model.detection import Box, Detection

logger = logging.getLogger(__name__)

class AiCamDetection:
    def __init__(self, box, category, conf):
        self.box = box
        self.category = category
        self.conf = conf

class AiCamera(Source, Operation, metaclass=SingletonMeta):

    def __init__( self, name: str, parameters):

        logger.info("Initializing AiCamera")
        super().__init__(name)

        from picamera2.devices import IMX500
        from picamera2.devices.imx500 import (NetworkIntrinsics, postprocess_nanodet_detection)

        self._IMX500 = IMX500
        self._postprocess_nanodet_detection = postprocess_nanodet_detection
        self._NetworkIntrinsics = NetworkIntrinsics

        model_path_str: str = "/usr/share/imx500-models/imx500_network_ssd_mobilenetv2_fpnlite_320x320_pp.rpk"
        self._model_path = model_path_str
        self._threshold = parameters.get("confidence", 0.5)
        self._iou = 0.5
        self._last_detections = {}
        self._camera = None
        self._imx500 = None


    def init(self):
        self._imx500 = self._IMX500(self._model_path)
        self._intrinsics = self._imx500.network_intrinsics
        if not self._intrinsics:
            self._intrinsics = self._NetworkIntrinsics()
            self._intrinsics.task = "object detection"

        from picamera2 import Picamera2
        self._camera = Picamera2(self._imx500.camera_num)


        config = self._camera.create_preview_configuration(
            #main={"size": (width, height), "format": "RGB888"},
            main={"format": "RGB888"},
            buffer_count=4,
            controls={"FrameRate": self._intrinsics.inference_rate if self._intrinsics.inference_rate else 10}
        )

        self._camera.start(config)
        time.sleep(1)

        logger.info("AiCamera initialization complete.")


    def get_frame(self) -> Frame:
        logger.debug("Getting frame from AiCamera")

        if self._camera is None:
            self.init()

        assert self._camera is not None, "Camera not initialized"
        metadata = self._camera.capture_metadata()
        timestamp = datetime.now()
        self._last_detections.update({
            timestamp: self._imx500.get_outputs(metadata, add_batch=True)
            })
        frame_data = self._camera.capture_array("main")

        return Frame(
            frame_id=f"{self._name}_{timestamp}",
            source_id=self._name,
            image=frame_data,
            timestamp=timestamp
        )


    def process(self, frame) -> list[Detection]:
        detection = self._last_detections.get(frame.timestamp)
        if detection is not None:
            boxes, scores, classes = detection[0][0], detection[1][0], detection[2][0]

            valid_indices = np.where(scores >= 0.5)[0]
            boxes   = boxes[valid_indices]
            scores  = scores[valid_indices]
            classes = classes[valid_indices]

            box_list = []
            for (y0, x0, y1, x1), conf, label_id in zip(boxes, scores, classes):
                w = (x1 - x0)
                h = (y1 - y0)
                x_center = x0 + w / 2
                y_center = y0 + h / 2

                box_list.append(
                    Box(
                        xywhn=(x_center, y_center, w, h),
                        label=int(label_id),
                        conf=float(conf)
                    )
                )

            self._last_detections.pop(frame.timestamp)
            return box_list
        return []


    def release(self):
        if self._camera is not None:
            logger.info("Releasing AiCamera")
            self._camera.stop()
            self._camera.close()
            self._camera = None
            self._last_detection = None
            self._imx500 = None

