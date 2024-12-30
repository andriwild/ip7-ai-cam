import cv2

from ml.interface.operation import Operation
from model.capture import Capture


class TextAnnotator(Operation):

    def process(self, capture: Capture):
        frame = capture.get_frame()
        if frame is None:
            return capture

        cv2.putText(
              frame,
              capture.get_timestamp().strftime("%A %d %B %Y %I:%M:%S%p"),
              (10, frame.shape[0] - 10),
              cv2.FONT_HERSHEY_SIMPLEX,
              0.35,
              (100, 100, 255),
              1)
        capture.set_frame(frame)
        return capture
