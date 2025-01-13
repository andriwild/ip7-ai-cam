from step.interface.operation import Operation
from model.detection import Detection
from model.model import Frame


class Bridge(Operation):
    def __init__(self, name: str, params = {}):
        super().__init__(name)

    def process(self, frame: Frame) -> list[Detection]:
        return []


