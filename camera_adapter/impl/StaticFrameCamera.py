from time import sleep
import numpy as np

from camera_adapter.ICamera import ICamera

class StaticFrameCamera(ICamera):

    NAME = "static"

    def __init__(self, width=640, height=480):
        self.static_frame = np.random.randint(0, 10, (width, height, 3), dtype=np.uint8)

    def get_frame(self):
        sleep(0.5)
        return  self.static_frame

    def release(self):
        pass

    def get_name(self) -> str:
        return self.NAME

