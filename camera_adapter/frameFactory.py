import importlib.util
import logging

from camera_adapter.interface.camera import Camera
from camera_adapter.impl.static import StaticFrameGenerator

logger = logging.getLogger(__name__)

class FrameFactory:

    def __init__(self):
        self._camera = StaticFrameGenerator()
        logger.info("CameraFactory initialized with StaticFrameCamera")


    def _create_camera(self, name: str, device: str, width: int, height: int) -> Camera:
        logger.info(f"Creating camera: {name} with device {device}, width {width}, height {height}")

        camera = StaticFrameGenerator()

        match name:
            case "pi":
                if self._is_module_available("picamera2"):
                    from camera_adapter.impl.pi import PiCamera
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
                    from camera_adapter.impl.opencv import OpenCVCamera
                    camera = OpenCVCamera(device=device, width=width, height=height)
                    test_frame = camera.get_frame()
                    if test_frame is not None:
                        logger.info("Using OpenCV camera strategy")
                    else:
                        camera.release()
                        logger.warning("OpenCV camera strategy not available")
                else:
                    logger.warning("cv2 not available")

            case "image":
                logger.info("Setting image camera")
                from camera_adapter.impl.image import ImageGenerator
                camera = ImageGenerator(width=width, height=height)
            case _:
                logger.info("Setting to static frame camera")

        return camera


    def _is_module_available(self, module_name: str) -> bool:
        spec = importlib.util.find_spec(module_name)
        available = spec is not None
        logger.debug(f"Module {module_name} available: {available}")
        return available


    def get_camera(self) -> Camera:
        logger.debug("Getting current camera")
        return self._camera


    def set_camera_by_name(self, camera_name: str) -> Camera:
        logger.info(f"Setting camera by name: {camera_name}")
        self._camera = self._create_camera(camera_name, "/dev/video0", 640, 480)
        return self._camera


    def default_camera(self) -> Camera:
        logger.info("Setting default camera to 'static'")
        return self.set_camera_by_name("static")
