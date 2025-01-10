from abc import ABC, abstractmethod

from model.model import Result


class Sink(ABC):

    def __init__(self, name: str):
        self._name = name


    @abstractmethod
    def put(self, result: Result) -> None:
        pass


    def get_name(self) -> str:
        return self._name


    @abstractmethod
    def release(self) -> None:
        pass
