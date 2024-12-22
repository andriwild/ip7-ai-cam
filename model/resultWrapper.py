from abc import ABC, abstractmethod
from typing import List, Any, Tuple
import numpy as np
from dataclasses import dataclass, field
import torch

from torch._prims_common import Tensor
from ultralytics.engine.model import Results

class Wrapper(ABC):

    @classmethod
    @abstractmethod
    def from_ultralytics(cls, result: Results):
        raise NotImplementedError("Subclasses must implement from_ultralytics.")

    @classmethod
    @abstractmethod
    def from_ai_cam(cls, result: Any):
        raise NotImplementedError("Subclasses must implement from_ultralytics.")

@dataclass
class Box:
    xywhn: Tensor  # Normalized x, y, width, height
    conf: float
    label: int


@dataclass
class BoxWrapper(Wrapper):
    boxes: List[Box] = field(default_factory=list) 

    @classmethod
    def from_ultralytics(cls, result: Results):
        """Extracts relevant properties from ultralytics Boxes."""

        ul_boxes = result.boxes
        if ul_boxes is None:
            return cls(boxes=[])

        xywhn = ul_boxes.xywhn  # boxes in [x, y, width, height] normalized format
        conf = ul_boxes.conf if ul_boxes.conf is not None else np.ones(xywhn.shape[0])  # default to 1 if no confidence
        labels = ul_boxes.cls if ul_boxes.cls is not None else [0] * xywhn.shape[0]  # default class 0

        boxes: list[Box] = []
        for (box, score, label) in zip(xywhn, conf, labels):
            boxes.append(Box(xywhn=box, conf=float(score), label=int(label)))

        return cls(boxes=boxes)

    @classmethod
    def from_ai_cam(cls, result: Tuple[np.ndarray, np.ndarray, np.ndarray]):
        """Extracts relevant properties from ultralytics Boxes."""
        return cls(boxes=[Box(xywhn=box, conf=score, label=label) for box, score, label in zip(*result)])



@dataclass
class MaskWrapper(Wrapper):
    masks: np.ndarray  # Mask data as a numpy array

    @classmethod
    def from_ultralytics(cls, result: Results):
        """Extracts relevant properties from ultralytics Masks."""
        masks = result.masks

        if masks is None:
            return cls(masks=np.array([]))

        mask_data = masks.data.cpu().numpy() if isinstance(masks.data, torch.Tensor) else masks.data

        return cls(masks=mask_data)


@dataclass
class KeypointWrapper(Wrapper):
    keypoints: np.ndarray  # Keypoint data as a numpy array

    @classmethod
    def from_ultralytics(cls, result: Results):
        """Extracts relevant properties from ultralytics Keypoints."""
        keypoints = result.keypoints

        if keypoints is None:
            return cls(keypoints=np.array([]))

        return cls(keypoints=keypoints.data)

