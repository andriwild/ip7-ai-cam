from abc import abstractmethod
import numpy as np
import cv2
import logging
from model.detection import Box
from model.resultWrapper import BoxWrapper, MaskWrapper, KeypointWrapper, Wrapper

logger = logging.getLogger(__name__)



class MaskDrawingStrategy:
    def draw(self, frame: np.ndarray, data: Wrapper):

        if not isinstance(data, MaskWrapper):
            raise TypeError("MaskDrawingStrategy can only draw MaskWrapper instances.")

        # Draw each mask on the frame with transparency
        overlay = frame.copy()
        for mask in data.masks:
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


class KeypointDrawingStrategy:
    def draw(self, frame: np.ndarray, data: Wrapper):

        if not isinstance(data, KeypointWrapper):
            raise TypeError("KeypointDrawingStrategy can only draw KeypointWrapper instances.")

        for keypoint in data.keypoints:
            for x, y, conf in keypoint:
                if conf > 0.5:  # Draw only if confidence is sufficient
                    cv2.circle(frame, (int(x), int(y)), 3, (0, 0, 255), -1)  # Red keypoints

        return frame
