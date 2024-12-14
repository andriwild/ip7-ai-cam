import logging
from observer.subject import Subject
from observer.observer import Observer

logger = logging.getLogger(__name__)

class Configuration(Subject):

    def __init__(self):
        self._camera = "static"
        self._observers = []
        logger.info("Configuration initialized with default camera 'static'")


    def get_camera(self) -> str:
        logger.debug(f"Getting camera: {self._camera}")
        return self._camera


    def set_camera(self, value):
        logger.info(f"Setting camera to {value}")
        self._camera = value
        self.notify()


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
