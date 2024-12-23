from model.result import Result
from sink.interface.sink import Sink


class Console(Sink):

    def put(self, result: Result) -> None:
        print(result.frame_id)

    def get_name(self) -> str:
        return "Console"
