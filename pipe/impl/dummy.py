from pipe.interface.operation import Operation
from model.detection import Detection, Box
from model.model import Frame

import logging


logger = logging.getLogger(__name__)


class Dummy(Operation):

    def __init__(self, name: str, params = {}):
        super().__init__(name)
        logging.info(f"Initializing Dummy inference with name {name}")

    def process(self, frame: Frame) -> list[Detection]:
        boxes = []
        boxes.append(Box(xywhn=(0.5, 0.5, 0.5, 0.5), conf=1.0, label="dummy"))
        return boxes
