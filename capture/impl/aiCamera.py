import time
import logging
from datetime import datetime

from capture.interface.source import Source
from model.frame import Frame
from model.result import Result
from controller.interfaces.operation import Operation
from model.resultWrapper import BoxWrapper
from model.result import BoxResult
from picamera2 import Picamera2
from picamera2.devices import IMX500
from picamera2.devices.imx500 import (NetworkIntrinsics,postprocess_yolov8_detection)
import numpy as np

logger = logging.getLogger(__name__)

class Detection:
    def __init__(self, coords, category, conf, metadata, picam2, imx500):
        """Create a Detection object, recording the bounding box, category and confidence."""
        self.category = category
        self.conf = conf
        self.box = imx500.convert_inference_coords(coords, metadata, picam2)

class AiCamera(Source, Operation):

    NAME = "ai_camera"

    def __init__(self, model_path: str, width: int = 640, height: int = 640):
        logger.info("Initializing AiCamera with model: %s", model_path)
        self._camera = None
        self._model_path = model_path
        self._width = width
        self._height = height
        self._initialize_camera()

    def _initialize_camera(self):
        logger.info("Setting up Picamera2 with IMX500")
        self._imx500 = IMX500(self._model_path)
        intrinsics = NetworkIntrinsics()
        intrinsics.task = "object detection"
        intrinsics.cpu = {"bbox_normalization": "true", "bbox_order": "yx"}
        intrinsics.update_with_defaults()
        print(intrinsics)
        self._camera = Picamera2(self._imx500.camera_num)

        config = self._camera.create_preview_configuration(
            main={"size": (self._width, self._height), "format": "RGB888"},
            controls={"FrameRate": intrinsics.inference_rate},
        )
        self._camera.start(config)
        time.sleep(1)  # Ensure the camera initializes properly

    def get_frame(self) -> Frame:
        logger.debug("Capturing frame from AiCamera")
        timestamp = datetime.now()
        frame = self._camera.capture_array()
        return Frame(
            frame_id=f"{self.NAME}_{timestamp}",
            source_id=self.NAME,
            frame=frame,
            timestamp=timestamp
        )

    def process(self, frame: Frame) -> Result:
        logger.info("Processing frame for inference")
        metadata = self._camera.capture_metadata()
        np_outputs = self._imx500.get_outputs(metadata, add_batch=True)
        input_w, input_h = self._imx500.get_input_size()
        box_wrapper = BoxWrapper()
        if np_outputs:
            boxes, scores, classes = np_outputs[0][0], np_outputs[1][0], np_outputs[2][0]
            boxes = boxes / input_h
            boxes = np.array_split(boxes, 4, axis=1)
            boxes = zip(*boxes)
            last_detections = [
                Detection(box, category, score, metadata, self._camera, self._imx500)
                for box, score, category in zip(boxes, scores, classes)
                if score > 0.6
            ]
            print(last_detections)

            boxes = np_outputs[0][0]    # Shape: (300, 4)
            scores = np_outputs[1][0]   # Shape: (300,)
            classes = np_outputs[2][0]  # Shape: (300,)
            valid_mask = scores > 0.6
            
            # Filterung der Arrays anhand der Maske
            filtered_boxes = boxes[valid_mask]
            filtered_scores = scores[valid_mask]
            filtered_classes = classes[valid_mask]
            filtered_boxes = [self._imx500.convert_inference_coords(box, metadata, self._camera) for box in filtered_boxes]
    
            result_tuple = (filtered_boxes, filtered_scores, filtered_classes)
            box_wrapper = BoxWrapper.from_ai_cam(result_tuple)
        result = BoxResult(
            frame_id=frame.frame_id,
            frame=frame.frame,
            inference_time=0,
            boxes=box_wrapper
        )
        return result

    def release(self):
        if self._camera is not None:
            logger.info("Releasing AiCamera")
            self._camera.stop()
            self._camera.close()
            self._camera = None

    def get_name(self) -> str:
        logger.debug("Getting source name for AiCamera")
        return self.NAME

