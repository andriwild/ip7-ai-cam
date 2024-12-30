import logging
import numpy as np
import cv2
import time
from datetime import datetime

from source.interface.source import Source
from model.frame import Frame

logger = logging.getLogger(__name__)


class StaticFrameGenerator(Source):

    def __init__(self, name: str, width: int = 640, height: int = 480):
        logger.info("Initializing StaticFrameGenerator")
        super().__init__(name)
        self.width = width
        self.height = height
        self.frame_counter = 0
        self.bee_position = [self.width // 2, self.height // 2]  # Initial bee position
        self.direction = [5, 3]  # Movement direction

    def generate_screensaver_frame(self):
        logger.debug("Generating initial screensaver frame")
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        border = 30
        cv2.rectangle(frame, (border, border), (self.width - border, self.height - border), (0, 255, 0), 2)
        return frame

    def update_bee_position(self):
        for i in range(2):
            self.bee_position[i] += self.direction[i]
            if self.bee_position[i] <= 50 or self.bee_position[i] >= [self.width, self.height][i] - 50:
                self.direction[i] = -self.direction[i]  # Reverse direction on collision

    def get_frame(self) -> Frame:
        logger.debug("Getting frame from StaticFrameGenerator")
        frame = self.generate_screensaver_frame()
        timestamp = datetime.now()
        self.update_bee_position()

        # Draw a moving bee (circle) on the frame
        cv2.circle(
            frame, 
            tuple(self.bee_position), 
            20, 
            (0, 255, 255), 
            -1  # Filled circle
        )
        self.frame_counter += 1
        time.sleep(0.05)  # Simulate delay
        return Frame(
            frame_id=f"{self._name}_{timestamp}",
            source_id=self._name,
            frame=frame,
            timestamp=timestamp)

    def release(self):
        logger.info("Releasing StaticFrameGenerator")

