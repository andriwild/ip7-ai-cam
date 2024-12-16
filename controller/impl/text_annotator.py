import cv2
import datetime

from controller.interfaces.operation import Operation


class TextAnnotator(Operation):

    def process(self, frame):
        timestamp = datetime.datetime.now()
        cv2.putText(
              frame,
              timestamp.strftime("%A %d %B %Y %I:%M:%S%p"),
              (10, frame.shape[0] - 10),
              cv2.FONT_HERSHEY_SIMPLEX,
              0.35,
              (100, 100, 255),
              1)
        return frame
