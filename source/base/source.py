from abc import ABC, abstractmethod
from model.model import Frame

class Source(ABC):

    def __init__(self, name: str):
        self._name = name

    @abstractmethod
    def get_frame(self) -> Frame:
        pass

    @abstractmethod
    def release(self):
        pass

    @abstractmethod
    def init(self):
        pass

    def get_name(self) -> str:
        return self._name
