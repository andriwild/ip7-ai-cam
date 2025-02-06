from abc import ABC, abstractmethod
from dataclasses import dataclass
from torch._prims_common import Tensor
import numpy as np
import cv2
import torch


class Detection(ABC):

    @abstractmethod
    def draw(frame: np.ndarray) -> np.ndarray:
        pass

    @abstractmethod
    def to_json(self) -> dict:
        pass


@dataclass
class Box(Detection):
    xywhn: Tensor  # Normalized x, y, width, height
    conf: float
    label: str

    def draw(self, frame: np.ndarray, color = (0,0,255)) -> np.ndarray:

        height, width = frame.shape[:2]
        x_center, y_center, w, h = self.xywhn
        x1 = int((x_center - w / 2) * width)
        y1 = int((y_center - h / 2) * height)
        x2 = int((x_center + w / 2) * width)
        y2 = int((y_center + h / 2) * height)

        label_text = f"{self.label}: {self.conf:.2f}"

        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 4)
        cv2.putText(frame, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 1)
        return frame

    def __str__(self):
        return f"Box: {self.xywhn}, {self.conf}, {self.label}"

    def to_json(self)-> str:
        return {
            "xywhn": [self.xywhn[0].item(), self.xywhn[1].item(), self.xywhn[2].item(), self.xywhn[3].item()],
            "conf": self.conf,
            "label": self.label
        }


@dataclass
class Mask(Detection):
    masks: np.ndarray

    def draw(self, frame: np.ndarray) -> np.ndarray:

        masks = self.masks
        if masks:
            mask_data = masks.data.cpu().numpy() if isinstance(masks.data, torch.Tensor) else masks.data

            # Draw each mask on the frame with transparency
            overlay = frame.copy()
            for mask in mask_data:
                color = (0, 255, 0)
                mask_binary = (mask > 0.5).astype(np.uint8) * 255
                contours, _ = cv2.findContours(mask_binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

                # Apply the mask area with transparency
                mask_indices = mask > 0.5
                overlay[mask_indices] = (0.3 * np.array(color) + 0.7 * overlay[mask_indices]).astype(np.uint8)
                for contour in contours:
                    cv2.drawContours(overlay, [contour], -1, color, 2)

            # Blend the overlay with the original frame
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        return frame

    def __str__(self):
        return f"Mask: {self.masks}"

    def to_json(self):
        return {
            "masks": self.masks
        }


@dataclass
class Keypoint(Detection):
    keypoints: np.ndarray 

    def draw(self, frame: np.ndarray) -> np.ndarray:

        for keypoint in self.keypoints.data:
            for x, y, conf in keypoint:
                if conf > 0.5:  # Draw only if confidence is sufficient
                    cv2.circle(frame, (int(x), int(y)), 3, (0, 0, 255), -1)  # Red keypoints
        return frame
        


    def __str__(self):
        return f"Keypoint: {self.keypoints}"

    def to_json(self):
        return {
            "keypoints": self.keypoints
        }
