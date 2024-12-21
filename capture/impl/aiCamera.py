import time
import logging
from datetime import datetime

from capture.interface.source import Source
from model.frame import Frame
from model.result import Result
from controller.interfaces.operation import Operation
from picamera2 import Picamera2
from picamera2.devices import IMX500
from picamera2.devices.imx500 import postprocess_yolov8, NetworkIntrinsics

logger = logging.getLogger(__name__)

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
        self._camera = Picamera2(self._imx500.camera_num)
        intrinsics = NetworkIntrinsics()
        intrinsics.task = "object detection"
        config = self._camera.create_preview_configuration(
            main={"size": (self._width, self._height), "format": "RGB888"},
            controls={"FrameRate": intrinsics.inference_rate}
        )
        self._camera.start(config)
        print(intrinsics)
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
        logger.debug("Processing frame for inference")
        start_time = time.time()
        metadata = self._camera.capture_metadata()
        detections = postprocess_yolov8(metadata)
        print("AI Camera detections: ", detections)
        inference_time = time.time() - start_time
        result = Result(
            frame_id=frame.frame_id,
            frame=frame.frame,
            inference_time=inference_time
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
