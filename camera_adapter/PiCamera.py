import time

from ICamera import ICamera

class PiCamera(ICamera):
    def __init__(self, width=640, height=480):
        from picamera2 import Picamera2
        self.Picamera2 = Picamera2
        self._camera = self.Picamera2()
        self._camera.configure(
                self._camera.create_preview_configuration(
                    main={ "size": (width, height), "format": "RGB888" }
                    )
                )
        time.sleep(1)

    def get_frame(self):
        return self._camera.capture_array()

    def release(self):
        if self._camera is not None:
            self._camera.stop()

