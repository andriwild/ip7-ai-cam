from abc import ABC, abstractmethod

from model.result import Result


class Sink(ABC):

    @abstractmethod
    def put(self, result: Result) -> None:
        pass

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def release(self) -> None:
        pass
