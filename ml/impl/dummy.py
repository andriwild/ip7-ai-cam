from torch._prims_common import Tensor
from ml.interface.operation import Operation
from model.detection import Detection
from model.detection import Box

import logging

logger = logging.getLogger(__name__)


class Dummy(Operation):

    def __init__(self, name: str, params):
        super().__init__(name)
        logging.info(f"Initializing Dummy inference with name {name}")

    def process(self, frame) -> list[Detection]:
        boxes = []
        boxes.append(Box(xywhn=(0.5, 0.5, 0.2, 0.2), conf=0.5, label=0))
        return boxes
