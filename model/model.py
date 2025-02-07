from model.detection import Detection
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np

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
