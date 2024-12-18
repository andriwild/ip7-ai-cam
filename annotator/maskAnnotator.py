from controller.interfaces.operation import Operation
from model.capture import Capture
import numpy as np
import cv2
import torch

# developed by ChatGPT
class MaskAnnotator(Operation):

    def process(self, capture: Capture) -> Capture:
        frame = capture.get_frame()
        masks = capture.get_masks()

        if frame is None or masks is None or masks.data is None:
            return capture

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
        capture.set_frame(frame)
        return capture
