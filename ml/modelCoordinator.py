import logging
from configuration import Configuration
from controller.interfaces.operation import Operation
from ml.impl.ultralytics import UltralyticsInference
from observer.observer import Observer
from observer.subject import Subject

logger = logging.getLogger(__name__)

class ModelCoordinator(Observer, Operation):

    MODEL_PATH = "resources/ml_models"

    def __init__(self):
        self._models: list[Operation] = []


    def _model_from_name(self, model_name: str) -> Operation | None:
        model = None
        match model_name: 
            case "yolo11n.onnx" | "yolo11n-pose.onnx" | "yolo11n-seg.onnx":
                model = UltralyticsInference(self.MODEL_PATH, model_name)
            case _:
                logger.error(f"Model {model_name} not found")
        return model


    def update(self, subject: Subject) -> None:
        if not isinstance(subject, Configuration):
            logger.error("Expected subject to be an instance of Configuration")
            raise TypeError("Expected subject to be an instance of Configuration")

        model_names: list[str] = subject.get_models()
        logger.info(f"Models updated: {model_names}")

        self._models = []

        for name in model_names:
            model = self._model_from_name(name)
            if model:
                self._models.append(model)


    def process(self, frame):
        for model in self._models:
            frame = model.process(frame)
        return frame


