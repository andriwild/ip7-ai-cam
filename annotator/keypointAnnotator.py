from step.interface.operation import Operation
from model.capture import Capture
import cv2

class KeypointAnnotator(Operation):

    def process(self, capture: Capture) -> Capture:
        frame = capture.get_frame()
        keypoints = capture.get_keypoints()

        if frame is None or keypoints is None or keypoints.data is None:
            return capture

        for keypoint in keypoints.data:
            for x, y, conf in keypoint:
                if conf > 0.5:  # Draw only if confidence is sufficient
                    cv2.circle(frame, (int(x), int(y)), 3, (0, 0, 255), -1)  # Red keypoints

        capture.set_frame(frame)
        return capture
