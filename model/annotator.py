from abc import abstractmethod
import numpy as np
import cv2
import logging
from model.resultWrapper import BoxWrapper, MaskWrapper, KeypointWrapper, Wrapper

logger = logging.getLogger(__name__)

class DrawingStrategy:
    @abstractmethod
    def draw(self, frame: np.ndarray, data: Wrapper):
        raise NotImplementedError("Subclasses must implement draw.")


class BoxDrawingStrategy(DrawingStrategy):
    def draw(self, frame: np.ndarray, data: Wrapper):

        if not isinstance(data, BoxWrapper):
            raise TypeError("BoxDrawingStrategy can only draw BoxWrapper instances.")

        height, width = frame.shape[:2]
        for box in data.boxes:
            x_center, y_center, w, h = box.xywhn
            x1 = int((x_center - w / 2) * width)
            y1 = int((y_center - h / 2) * height)
            x2 = int((x_center + w / 2) * width)
            y2 = int((y_center + h / 2) * height)

            def map_conf_to_color(conf):
                red = int(255 * (1 - conf))
                green = int(255 * conf)
                return (0, green, red)  # BGR

            def map_to_label(label):
                return int(label)
            #return self.cooc_labels["names"][int(label)]

            color = map_conf_to_color(box.conf)
            label_text = f"Class {map_to_label(int(box.label))}: {box.conf:.2f}"

            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
            cv2.putText(frame, label_text, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        return frame


class MaskDrawingStrategy(DrawingStrategy):
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


class KeypointDrawingStrategy(DrawingStrategy):
    def draw(self, frame: np.ndarray, data: Wrapper):

        if not isinstance(data, KeypointWrapper):
            raise TypeError("KeypointDrawingStrategy can only draw KeypointWrapper instances.")

        for keypoint in data.keypoints:
            for x, y, conf in keypoint:
                if conf > 0.5:  # Draw only if confidence is sufficient
                    cv2.circle(frame, (int(x), int(y)), 3, (0, 0, 255), -1)  # Red keypoints

        return frame
