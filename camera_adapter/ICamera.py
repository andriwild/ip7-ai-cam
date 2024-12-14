from abc import ABC, abstractmethod

class ICamera(ABC):
    @abstractmethod
    def get_frame(self):
        pass

    @abstractmethod
    def release(self):
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass
