import time
import logging
from datetime import datetime
import numpy as np
from picamera2 import Picamera2
from picamera2.devices import IMX500
from model.frame import Frame

logger = logging.getLogger(__name__)

class AiCamera:

    NAME = "ai"

    def __init__(self, model_path: str, threshold: float = 0.55, max_detections: int = 10):
        logger.info("Initializing AiCamera")

        self.threshold = threshold
        self.max_detections = max_detections

        # Load IMX500 AI camera
        self._imx500 = IMX500(model_path)

        # Set up network intrinsics
        self._intrinsics = self._imx500.network_intrinsics
        self._intrinsics.task = "object detection"
        self._intrinsics.update_with_defaults()

        # Initialize Picamera2
        self._camera = Picamera2(self._imx500.camera_num)
        self._config = self._camera.create_preview_configuration(
            controls={"FrameRate": self._intrinsics.inference_rate}, buffer_count=12
        )

        self._camera.start(self._config)
        time.sleep(1)  # Ensure initialization

    def get_frame(self) -> Frame:
        logger.debug("Getting frame and detections from AiCamera")
        timestamp = datetime.now()
        metadata = self._camera.capture_metadata()

        # Perform detection
        np_outputs = self._imx500.get_outputs(metadata, add_batch=True)
        if np_outputs is None:
            logger.warning("No detections found in the current frame")
            return Frame(
                frame_id=f"{self.NAME}_{timestamp}",
                source_id=self.NAME,
                frame=None,
                timestamp=timestamp,
                detections=[]
            )

        boxes, scores, classes = self._parse_detections(np_outputs)
        detections = self._format_detections(boxes, scores, classes, metadata)

        # Capture frame data
        frame_data = self._camera.capture_array()

        return Frame(
            frame_id=f"{self.NAME}_{timestamp}",
            source_id=self.NAME,
            frame=frame_data,
            timestamp=timestamp,
            detections=detections
        )

    def _parse_detections(self, outputs):
        boxes, scores, classes = outputs[0][0], outputs[1][0], outputs[2][0]
        boxes = np.array_split(boxes, 4, axis=1)  # Split box coordinates
        return zip(*boxes), scores, classes

    def _format_detections(self, boxes, scores, classes, metadata):
        from picamera2.devices.imx500 import postprocess_nanodet_detection
        
        if self._intrinsics.postprocess == "nanodet":
            boxes, scores, classes = postprocess_nanodet_detection(
                outputs=outputs[0], conf=self.threshold, iou_thres=0.65, max_out_dets=self.max_detections
            )
        
        return [
            {
                "box": box.tolist(),
                "score": score,
                "class": cls
            }
            for box, score, cls in zip(boxes, scores, classes) if score > self.threshold
        ]

    def release(self):
        if self._camera is not None:
            logger.info("Releasing AiCamera")
            self._camera.stop()
            self._camera.close()
            self._camera = None

    def get_name(self) -> str:
        logger.debug("Getting source name for AiCamera")
        return self.NAME
