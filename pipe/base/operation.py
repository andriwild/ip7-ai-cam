from abc import ABC, abstractmethod

from model.detection import Detection
from model.model import Frame


class Operation(ABC):
    """
    Base class for Operation classes to process the frames with and returns a result.
    """
    def __init__(self, name: str):
        self._name = name

    @abstractmethod
    def process(self, frame: Frame) -> list[Detection]:
        """
        Process the frame (e.g. ML Task) and return the detections (e.g. Boxes).
        """
        pass

    def get_name(self) -> str:
        """
        Return the name of the operation.
        """
        return self._name
