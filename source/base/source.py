from abc import ABC, abstractmethod
from model.model import Frame

class Source(ABC):
    """
    Base class for Source classes to get the frames from.
    """

    def __init__(self, name: str):
        self._name = name

    @abstractmethod
    def get_frame(self) -> Frame:
        """
        Get the next frame from the source.
        """
        pass

    @abstractmethod
    def release(self):
        """
        Function called from the framework when the source is released.
        If the source has resources to release, they should be released here.
        """
        pass

    @abstractmethod
    def init(self):
        """
        Function called from the framework when the source is initialized.
        If the source has resources to initialize, they should be initialized here.
        """
        pass

    def get_name(self) -> str:
        """
        Return the name of the source
        """
        return self._name
