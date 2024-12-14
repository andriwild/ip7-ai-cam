import importlib.util
import logging

from camera_adapter.ICamera import ICamera
from camera_adapter.impl.StaticFrameCamera import StaticFrameCamera

logger = logging.getLogger(__name__)

class CameraFactory():

    def __init__(self):
        self._camera = StaticFrameCamera()
        logger.info("CameraFactory initialized with StaticFrameCamera")


    def _create_camera(self, name: str, device: str, width: int, height: int) -> ICamera:
        logger.info(f"Creating camera: {name} with device {device}, width {width}, height {height}")

        camera = StaticFrameCamera()

        match name:
            case "pi":
                if self._is_module_available("picamera2"):
                    from camera_adapter.impl.PiCamera import PiCamera
                    camera = PiCamera(width=width, height=height)
                    test_frame = camera.get_frame()
                    if test_frame is not None:
                        logger.info("Using libcamera camera strategy")
                    else:
                        camera.release()
                        logger.warning("libcamera camera strategy not available")
                else:
                    logger.warning("picamera2 not available")

            case "cv":
                if self._is_module_available("cv2"):
                    logger.info("Setting OpenCV camera")
                    from camera_adapter.impl.OpenCVCamera import OpenCVCamera
                    camera = OpenCVCamera(device=device, width=width, height=height)
                    test_frame = camera.get_frame()
                    if test_frame is not None:
                        logger.info("Using OpenCV camera strategy")
                    else:
                        camera.release()
                        logger.warning("OpenCV camera strategy not available")
                else:
                    logger.warning("cv2 not available")

            case _:
                logger.info("Setting to static frame camera")

        return camera


    def _is_module_available(self, module_name: str) -> bool:
        spec = importlib.util.find_spec(module_name)
        available = spec is not None
        logger.debug(f"Module {module_name} available: {available}")
        return available


    def get_camera(self) -> ICamera:
        logger.debug("Getting current camera")
        return self._camera


    def set_camera_by_name(self, camera_name: str) -> ICamera:
        logger.info(f"Setting camera by name: {camera_name}")
        self._camera = self._create_camera(camera_name, "/dev/video0", 640, 480)
        return self._camera


    def default_camera(self) -> ICamera:
        logger.info("Setting default camera to 'static'")
        return self.set_camera_by_name("static")
