from abc import ABC, abstractmethod

from model.frame import Frame
from model.result import Result


class Operation(ABC):

    @abstractmethod
    def process(self, frame: Frame) -> Result:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass
