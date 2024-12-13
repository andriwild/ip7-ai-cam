import time

from camera_adapter.ICamera import ICamera

class OpenCVCamera(ICamera):
    def __init__(self, device="/dev/video0", width=640, height=480):
        import cv2
        self.cv2 = cv2
        self._capture = self.cv2.VideoCapture(device)
        self._capture.set(self.cv2.CAP_PROP_FRAME_WIDTH, width)
        self._capture.set(self.cv2.CAP_PROP_FRAME_HEIGHT, height)
        time.sleep(1)

    def get_frame(self):
        ret, frame = self._capture.read()
        if not ret:
            return None
        return frame

    def release(self):
        if self._capture is not None:
            self._capture.release()

    

