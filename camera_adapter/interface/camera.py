from abc import ABC, abstractmethod

class Camera(ABC):
    @abstractmethod
    def get_frame(self):
        pass

    @abstractmethod
    def release(self):
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass
