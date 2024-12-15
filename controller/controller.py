from queue import Queue, Empty
import logging

from controller.interfaces.operation import Operation

logger = logging.getLogger(__name__)

class Controller:

    def __init__(self, annotate=True, buffer_size: int = 5):
        self._frame_queue = Queue(maxsize=buffer_size)
        self._annotate = annotate
        self.operations: list[Operation] = []


    def add_operation(self, operation: Operation) -> None:
        self.operations.append(operation)


    def remove_operation(self, operation: Operation) -> None:
        self.operations.remove(operation)



    def put(self, frame):
        if self._frame_queue.full():
            logger.info("frame queue is full")
            try:
                self._frame_queue.get_nowait()  # discard oldest frame
            except Empty:
                pass

        for operation in self.operations:
            frame = operation.process(frame)

        # if self._annotate:
        #    frame = self._annotate_frame(frame)

        self._frame_queue.put(frame)


    def get(self, block=True, timeout=None):
        return self._frame_queue.get(block=block, timeout=timeout)

