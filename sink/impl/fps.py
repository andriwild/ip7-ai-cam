import time
from sink.base.sink import Sink
from model.model import Result
import logging

logger = logging.getLogger(__name__)

class FPSConsole(Sink):
    def __init__(self, name: str, parameters: dict = {}):
        super().__init__(name)
        self._parameters = parameters
        self.alpha = self._parameters.get('alpha', 0.9)
        self.current_fps = 0.0
        self.last_time = None
        logger.info("FPSConsoleSink initialized")

    def put(self, result: Result) -> None:
        now = time.time()
        if self.last_time is not None:
            dt = now - self.last_time
            instant_fps = 1.0 / dt if dt > 0 else float('inf')
            # Exponentielles Glätten
            self.current_fps = (self.alpha * self.current_fps) + ((1 - self.alpha) * instant_fps)
        self.last_time = now
        logger.info(f"FPS (smoothed): {self.current_fps:.2f}")

    def release(self):
        logger.info("FPSConsoleSink released")

    def init(self):
        logger.info("FPSConsoleSink initialized")

