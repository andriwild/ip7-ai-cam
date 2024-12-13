import numpy as np

from camera_adapter.ICamera import ICamera

class StaticImageCamera(ICamera):
    def __init__(self, width=640, height=480):
        self.static_frame = np.random.randint(0, 255, (width, height, 3), dtype=np.uint8)

    def get_frame(self):
        return  self.static_frame

    def release(self):
        pass

