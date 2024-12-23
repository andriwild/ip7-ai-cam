import logging
from config.configuration import Configuration
from controller.interfaces.operation import Operation
from ml.impl.hailoObjectDetection import HailoObjectDetection
from ml.impl.ulSeg import UlSeg
from ml.impl.ulPose import UlPose
from ml.impl.ulObjectDetection import UlObjectDetection
from model.frame import Frame
from model.result import Result
from observer.observer import Observer
from observer.subject import Subject
from capture.impl.aiCamera import AiCamera

logger = logging.getLogger(__name__)

class ModelCoordinator(Observer, Operation):

    MODEL_PATH = "resources/ml_models"

    def __init__(self, ai_camera: AiCamera):
        self._operation = None
        self._ai_camera = ai_camera
        logger.info("ModelCoordinator initialized")

    def _model_from_name(self, model_name: str) -> Operation | None:
        model = None
        match model_name: 
            case "yolo11n.onnx":
                model = UlObjectDetection(f"{self.MODEL_PATH}/{model_name}")
            case "yolo11n-pose.onnx":
                model = UlPose(f"{self.MODEL_PATH}/{model_name}")
            case "yolo11n-seg.onnx":
                model = UlSeg(f"{self.MODEL_PATH}/{model_name}")
            case "hailo":
                model = HailoObjectDetection()
            case "ai_camera":
                model = self._ai_camera
            case "-":
                model = None
            case _:
                logger.error(f"Model {model_name} not found")
        return model


    def update(self, subject: Subject) -> None:
        if not isinstance(subject, Configuration):
            logger.error("Expected subject to be an instance of Configuration")
            raise TypeError("Expected subject to be an instance of Configuration")

        model_names: list[str] = subject.get_models()
        logger.info(f"Models updated: {model_names}")

        self._operation = None

        model = self._model_from_name(model_names[0])
        if model:
            self._operation = model


    def process(self, frame: Frame):
        if self._operation is None:
            return Result(frame.frame_id, frame.frame, 0, 0, 0)
        result = self._operation.process(frame)

        return result


