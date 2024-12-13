import importlib.util
from camera_adapter.ICamera import ICamera
from configuration import Configuration
from observer.Subject import Observer


class CameraFactory(Observer):

    def __init__(self, on_update):
        self._on_udpate = on_update
        self._camera = None

    def _create_camera(self, name, device, width, height):
        print("create camera: ", name)

        match(name):
            case "pi":
                if self._is_module_available("picamera2"):
                    from camera_adapter.impl.PiCamera import PiCamera
                    camera = PiCamera(width=width, height=height)
                    test_frame = camera.get_frame()
                    if test_frame is not None:
                        print("Using libcamera camera strategy.")
                        return camera
                    camera.release()
                else:
                    print("picamera2 no available")

            case "cv":
                if self._is_module_available("cv2"):
                    print("set opencv camera")
                    from camera_adapter.impl.OpenCVCamera import OpenCVCamera
                    camera = OpenCVCamera(device=device, width=width, height=height)
                    # We can check if the camera works by trying to get one frame
                    test_frame = camera.get_frame()
                    if test_frame is not None:
                        print("Using OpenCV camera strategy.")
                        return camera
                    camera.release()
                else:
                    print("cv2 not available")

            case _:
                return None

    def update(self, subject: Configuration):
        if self._camera is not None:
            self._camera.release()
            self._camera = None
        self._camera = self._create_camera(subject.get_camera(), "/dev/video0", 640, 480)
        self._on_udpate()


    def _is_module_available(self, module_name):
        spec = importlib.util.find_spec(module_name)
        return spec is not None

    def get_camera(self) -> ICamera:
        print("CameraFactory get_camera")
        if self._camera is not None:
            return self._camera
        else:
            raise RuntimeError("No supported camera interface found.")
