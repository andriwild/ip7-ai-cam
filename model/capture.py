from datetime import datetime
import numpy as np
from ultralytics.engine.results import Boxes, Masks, Keypoints

class Capture:

    def __init__(self, frame = None):
        self._frame = frame 
        self._boxes : Boxes | None = None
        self._masks : Masks | None = None
        self._keypoints : Keypoints | None  = None
        self._timestamp = datetime.now()


    def get_frame(self):
        return self._frame


    def set_frame(self, frame):
        self._frame = frame


    def get_timestamp(self) -> datetime:
        return self._timestamp


    def add_box(self, boxes: Boxes):
        self._boxes = boxes


    def get_boxes(self) -> Boxes | None:
        return self._boxes


    def add_mask(self, masks: Masks):
        self._masks = masks


    def get_masks(self) -> Masks | None:
        return self._masks


    def add_keypoints(self, keypoints: Keypoints):
        self._keypoints = keypoints


    def get_keypoints(self) -> Keypoints | None:
        return self._keypoints


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
            f"Detections: {self._boxes}" if self._boxes else "No detections"
        )

        return (
            f"Capture Object:\n"
            f"  Timestamp: {self._timestamp}\n"
            f"  Frame Info:\n    {frame_info}\n"
            f"  {detections_status}"
        )
