from abc import ABC, abstractmethod

from model.detection import Detection
from model.model import Frame


class Operation(ABC):
    def __init__(self, name: str):
        self._name = name

    @abstractmethod
    def process(self, frame: Frame) -> list[Detection]:
        pass

    def get_name(self) -> str:
        return self._name
