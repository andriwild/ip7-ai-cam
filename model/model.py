from model.detection import Detection
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np


@dataclass
class Step:
    def __init__(self, name, class_name, file_path, input, output, parameters=None):
        self.name = name
        self.class_name = class_name
        self.file_path = file_path
        self.input = input
        self.output = output
        self.parameters = parameters or {}


@dataclass(frozen=True)
class Frame:
    frame_id: str
    source_id: str
    image: np.ndarray
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Result:
    frame: Frame
    detections: list[Detection] = field(default_factory=list) 

    def add_detection(self, detection: list[Detection]):
        self.detections.extend(detection)
