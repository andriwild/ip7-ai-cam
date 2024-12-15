
from abc import ABC, abstractmethod

class Operation(ABC):

    @abstractmethod
    def process(self, frame):
        pass
