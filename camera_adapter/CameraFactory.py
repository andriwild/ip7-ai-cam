import importlib.util
from ICamera import ICamera

class CameraFactory:
    def __init__(self, device="/dev/video0", width=640, height=480):
        self._camera = self._create_camera(device, width, height)
        if self._camera is None:
            raise RuntimeError("No supported camera interface found.")

    def _create_camera(self, device, width, height):

        if self._is_module_available("picamera2"):
            from PiCamera import PiCamera
            camera = PiCamera(width=width, height=height)
            test_frame = camera.get_frame()
            if test_frame is not None:
                print("Using libcamera camera strategy.")
                return camera
            camera.release()
        else:
            print("picamera2 no available")

        if self._is_module_available("cv2"):
            from OpenCVCamera import OpenCVCamera
            camera = OpenCVCamera(device=device, width=width, height=height)
            # We can check if the camera works by trying to get one frame
            test_frame = camera.get_frame()
            if test_frame is not None:
                print("Using OpenCV camera strategy.")
                return camera
            camera.release()
        else:
            print("cv2 not available")


        # If neither works, return None
        return None

    def _is_module_available(self, module_name):
        spec = importlib.util.find_spec(module_name)
        return spec is not None

    def get_camera(self) -> ICamera:
        if self._camera is not None:
            return self._camera
        else:
            raise RuntimeError("No supported camera interface found.")
