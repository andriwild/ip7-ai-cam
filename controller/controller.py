from queue import Queue, Empty
import logging

from controller.interfaces.operation import Operation
from model.frame import Frame

logger = logging.getLogger(__name__)

class Controller:

    def __init__(self, annotate=True, buffer_size: int = 5):
        self._capture_queue: Queue[Frame] = Queue(maxsize=buffer_size)
        self._annotate = annotate
        self._operations: list[Operation] = []


    def add_operation(self, operation: Operation) -> None:
        self._operations.append(operation)


    def add_operations(self, operations: list[Operation]) -> None:
        self._operations.extend(operations)


    def remove_operation(self, operation: Operation) -> None:
        self._operations.remove(operation)


    def put(self, frame: Frame):
        if self._capture_queue.full():
            logger.info("frame queue is full")
            try:
                self._capture_queue.get_nowait()  # discard oldest frame
            except Empty:
                pass

        self._capture_queue.put(frame)


    def get(self, block=True, timeout=None):
        frame = self._capture_queue.get(block=block, timeout=timeout)

        result = None
        for operation in self._operations:
            result = operation.process(frame)

        return result

