import time

from camera_adapter.ICamera import ICamera

class OpenCVCamera(ICamera):
    def __init__(self, device="/dev/video0", width=640, height=480):
        print("opencv init")
        import cv2
        self.cv2 = cv2
        self._capture = self.cv2.VideoCapture(device)
        self._capture.set(self.cv2.CAP_PROP_FRAME_WIDTH, width)
        self._capture.set(self.cv2.CAP_PROP_FRAME_HEIGHT, height)
        time.sleep(1)

    def get_frame(self):
        print("opencv get_frame")
        ret, frame = self._capture.read()
        if not ret:
            return None
        return self.cv2.cvtColor(frame, self.cv2.COLOR_BGR2RGB)

    def release(self):
        if self._capture is not None:
            self._capture.release()
            self._capture = None

    


