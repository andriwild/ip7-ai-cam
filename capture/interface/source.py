from abc import ABC, abstractmethod
from model.capture import Capture

class Source(ABC):
    @abstractmethod
    def get_capture(self) -> Capture:
        pass

    @abstractmethod
    def release(self):
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass
