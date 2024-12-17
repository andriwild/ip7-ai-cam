
from abc import ABC, abstractmethod

from model.capture import Capture


class Operation(ABC):

    @abstractmethod
    def process(self, capture : Capture) -> Capture:
        pass
