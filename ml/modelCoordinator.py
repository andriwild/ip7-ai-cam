import logging
from config.configuration import Configuration
from controller.interfaces.operation import Operation
from ml.impl.ulSeg import UlSeg
from ml.impl.ulPose import UlPose
from ml.impl.ulObjectDetection import UlObjectDetection
from model.capture import Capture
from observer.observer import Observer
from observer.subject import Subject

logger = logging.getLogger(__name__)

class ModelCoordinator(Observer, Operation):

    MODEL_PATH = "resources/ml_models"

    def __init__(self):
        self._operations: list[Operation] = []
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

        self._operations = []

        for name in model_names:
            model = self._model_from_name(name)
            if model:
                self._operations.append(model)


    def process(self, capture: Capture):
        for model in self._operations:
            capture = model.process(capture)

        return capture


