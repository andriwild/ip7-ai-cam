from datetime import datetime
import numpy as np

class Capture:

    def __init__(self, frame = None):
        self._frame = frame 
        self._detections = None
        self._timestamp = datetime.now()


    def get_frame(self):
        return self._frame


    def set_frame(self, frame):
        self._frame = frame


    def get_timestamp(self) -> datetime:
        return self._timestamp


    def get_detections(self):
        return self._detections


    def set_detection(self, detections):
        self._detections = detections


    def __str__(self):
        if self._frame is not None and isinstance(self._frame, np.ndarray):
            height, width = self._frame.shape[:2]
            bytes_size = self._frame.nbytes
            frame_info = (
                f"Image is set\n"
                f"  - Width: {width} px\n"
                f"  - Height: {height} px\n"
                f"  - Size: {bytes_size} bytes"
            )
        else:
            frame_info = "No image is set"

        detections_status = (
            f"Detections: {self._detections}" if self._detections else "No detections"
        )

        return (
            f"Capture Object:\n"
            f"  Timestamp: {self._timestamp}\n"
            f"  Frame Info:\n    {frame_info}\n"
            f"  {detections_status}"
        )
