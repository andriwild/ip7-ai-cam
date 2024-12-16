import logging
from observer.subject import Subject
from observer.observer import Observer

logger = logging.getLogger(__name__)

class Configuration(Subject):

    def __init__(self):
        self._camera = "static"
        self._models = ["yolo11n.onnx"] # TODO: remove default model
        self._observers = []
        logger.info("Configuration initialized with default camera 'static'")


    # Observer pattern methods
    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)
        logger.info(f"Observer {observer} attached")


    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)
        logger.info(f"Observer {observer} detached")


    def notify(self) -> None:
        logger.info("Notifying observers")
        for observer in self._observers:
            observer.update(self)


    # camera property
    def get_camera(self) -> str:
        logger.debug(f"Getting camera: {self._camera}")
        return self._camera


    def set_camera(self, camera_name):
        logger.info(f"Setting camera to {camera_name}")
        self._camera = camera_name
        self.notify()


    # model property
    def get_models(self) -> list[str]:
        logger.debug(f"Getting models: {self._models}")
        return self._models


    def set_models(self, models: list[str]):
        logger.info(f"Setting models to {models}")
        self._models = models
        self.notify()

