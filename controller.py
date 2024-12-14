from queue import Queue, Empty
import cv2
import datetime
import logging

logger = logging.getLogger(__name__)

class Controller:

    def __init__(self, annotate=True, buffer_size: int = 5):
        self._frame_queue = Queue(maxsize=buffer_size)
        self._annotate = annotate

    def put(self, frame):
        if self._frame_queue.full():
            logger.info("frame queue is full")
            try:
                self._frame_queue.get_nowait()  # discard oldest frame
            except Empty:
                pass

        if self._annotate:
           frame = self._annotate_frame(frame)

        self._frame_queue.put(frame)


    def get(self, block=True, timeout=None):
        return self._frame_queue.get(block=block, timeout=timeout)


    def _annotate_frame(self, frame):
        timestamp = datetime.datetime.now()
        cv2.putText(
              frame,
              timestamp.strftime("%A %d %B %Y %I:%M:%S%p"),
              (10, frame.shape[0] - 10),
              cv2.FONT_HERSHEY_SIMPLEX,
              0.35,
              (0, 0, 255),
              1)
        return frame


