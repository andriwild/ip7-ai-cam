from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Optional
from model.annotator import BoxDrawingStrategy, MaskDrawingStrategy, KeypointDrawingStrategy
from model.resultWrapper import BoxWrapper, MaskWrapper, KeypointWrapper
import numpy as np

import logging
logger = logging.getLogger(__name__)

@dataclass
class Result:
    frame_id: str
    frame: np.ndarray
    inference_time: Optional[float] = None
    preprocess_time: Optional[float] = None
    postprocess_time: Optional[float] = None

    def set_inference_time(self, time: float):
        self.inference_time = time

    def set_preprocess_time(self, time: float):
        self.preprocess_time = time

    def set_postprocess_time(self, time: float):
        self.postprocess_time = time

    def draw(self, frame: np.ndarray):
        logger.info("Draw method not implemented for Result.")
        return frame


@dataclass
class BoxResult(Result):
    boxes: BoxWrapper = field(default_factory=BoxWrapper) 

    def draw(self, frame: np.ndarray):
        logger.info("Drawing boxes")
        return BoxDrawingStrategy().draw(frame, self.boxes)


@dataclass
class MaskResult(Result):
    masks: MaskWrapper = field(default_factory=MaskWrapper)

    def draw(self, frame: np.ndarray):
        return MaskDrawingStrategy().draw(frame, self.masks)


@dataclass
class KeypointResult(Result):
    keypoint: KeypointWrapper = field(default_factory=KeypointWrapper)

    def draw(self, frame: np.ndarray):
        return KeypointDrawingStrategy().draw(frame, self.keypoint)
