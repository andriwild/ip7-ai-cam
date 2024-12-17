from abc import ABC, abstractmethod

from model.capture import Capture


class Sink(ABC):

    @abstractmethod
    def put(self, capture: Capture) -> None:
        pass
