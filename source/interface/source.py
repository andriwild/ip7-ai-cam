from abc import ABC, abstractmethod
from model.frame import Frame

class Source(ABC):
    @abstractmethod
    def get_frame(self) -> Frame:
        pass

    @abstractmethod
    def release(self):
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass
