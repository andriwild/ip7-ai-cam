from dataclasses import dataclass, field
from datetime import datetime
import numpy as np

@dataclass(frozen=True)
class Frame:
    frame_id: str
    source_id: str
    frame: np.ndarray
    timestamp: datetime = field(default_factory=datetime.now)
