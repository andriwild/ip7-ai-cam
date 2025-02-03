from abc import ABC, abstractmethod

from model.model import Result


class Sink(ABC):
    """
    Base class for Sink classes to send the results to.
    """

    def __init__(self, name: str):
        self._name = name


    @abstractmethod
    def put(self, result: Result) -> None:
        """
        Put the result into the sink.
        """
        pass


    def get_name(self) -> str:
        """
        Return the name of the sink.
        """
        return self._name


    @abstractmethod
    def release(self) -> None:
        """
        Function called from the framework when the sink is released.
        If the sink has resources to release, they should be released here.
        """
        pass


    @abstractmethod
    def init(self) -> None:
        """
        Function called from the framework when the sink is initialized.
        """
        pass
