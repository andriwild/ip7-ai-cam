from abc import ABC, abstractmethod

from model.frame import Frame
from pipeline.pipeline import Result


class Inference(ABC):

    @abstractmethod
    def infer(self, frame: Frame) -> Result:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

