import queue
import time
from collections import deque


class FpsQueue:
    """
    A wrapper around Python's queue.Queue that keeps track of
    timestamps for put and get operations, allowing FPS measurement
    without letting the list of timestamps grow unbounded.
    """
    def __init__(self, maxsize=0, maxlen=1000):
        """
        :param maxsize: Maxsize for the underlying queue.
        :param maxlen:  Max number of timestamps to store for put/get.
        """
        self._queue = queue.Queue(maxsize)
        # Use deque with a fixed max length
        self._put_timestamps = deque(maxlen=maxlen)
        self._get_timestamps = deque(maxlen=maxlen)
        self.maxsize = maxsize

    def put(self, item, block=True, timeout=None):
        """Put an item into the queue and record its timestamp."""
        self._queue.put(item, block, timeout)
        self._put_timestamps.append(time.time())

    def get(self, block=True, timeout=None):
        """Get an item from the queue and record its timestamp."""
        item = self._queue.get(block, timeout)
        self._get_timestamps.append(time.time())
        return item

    def get_put_fps(self, window_size=30):
        """
        Return the approximate FPS of the put operations,
        calculated from the last `window_size` timestamps.
        """
        if len(self._put_timestamps) < 2:
            return 0.0

        # We’ll consider only the most recent `window_size` timestamps 
        times = list(self._put_timestamps)[-window_size:]
        if len(times) < 2:
            return 0.0

        total_time = times[-1] - times[0]  # time between oldest & newest
        if total_time <= 0:
            return 0.0

        # The number of intervals is (len(times) - 1)
        return (len(times) - 1) / total_time

    def get_get_fps(self, window_size=30):
        """
        Return the approximate FPS of the get operations,
        calculated from the last `window_size` timestamps.
        """
        if len(self._get_timestamps) < 2:
            return 0.0

        times = list(self._get_timestamps)[-window_size:]
        if len(times) < 2:
            return 0.0
        
        total_time = times[-1] - times[0]
        if total_time <= 0:
            return 0.0

        return (len(times) - 1) / total_time

    def qsize(self):
        """Expose the queue size if you need it."""
        return self._queue.qsize()

    def empty(self):
        """Expose the empty state of the underlying queue."""
        return self._queue.empty()
