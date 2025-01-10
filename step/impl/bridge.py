from step.interface.operation import Operation
import numpy as np
from model.detection import Detection


class Bridge(Operation):
    def __init__(self, name: str, params = {}):
        super().__init__(name)

    def process(self, frame: np.ndarray) -> list[Detection]:
        return []


