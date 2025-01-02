from abc import ABC, abstractmethod

from model.detection import Detection
import numpy as np


class Operation(ABC):
    def __init__(self, name: str):
        self._name = name

    @abstractmethod
    def process(self, frame: np.ndarray) -> list[Detection]:
        pass

    def get_name(self) -> str:
        return self._name
