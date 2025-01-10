from dataclasses import dataclass, field
from model.frame import Frame
from model.detection import Detection

@dataclass
class Result:
    frame: Frame
    predictions: list[Detection] = field(default_factory=list) 

    def add_detection(self, detection: list[Detection]):
        self.predictions.extend(detection)
