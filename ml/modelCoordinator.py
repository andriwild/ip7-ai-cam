import logging
from configuration import Configuration
from controller.interfaces.operation import Operation
from observer.observer import Observer
from observer.subject import Subject

logger = logging.getLogger(__name__)

class ModelCoordinator(Observer, Operation):

    def __init__(self):
        self._models = []

    def update(self, subject: Subject) -> None:
        if not isinstance(subject, Configuration):
            logger.error("Expected subject to be an instance of Configuration")
            raise TypeError("Expected subject to be an instance of Configuration")

        self._models = subject.get_models()
        logger.info(f"Models updated: {self._models}")


    def process(self, frame):
        pass


