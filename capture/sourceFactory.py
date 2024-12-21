import importlib.util
import logging

from capture.interface.source import Source
from capture.impl.static import StaticFrameGenerator

logger = logging.getLogger(__name__)

class SourceFactory:

    def __init__(self):
        self._source = StaticFrameGenerator()
        logger.info("SourceFactory initialized with StaticFrameSource")


    def _create_source(self, name: str, device: str, width: int, height: int) -> Source:
        logger.info(f"Creating source: {name} with device {device}, width {width}, height {height}")

        source = StaticFrameGenerator()

        match name:
            case "ai_camera":
                if self._is_module_available("picamera2"):
                    from capture.impl.aiCamera import AiCamera
                    source = AiCamera("resources/ml_models/yolov8n.imx", width=width, height=height)
                    test_capture = source.get_frame()
                    if test_capture.frame is not None:
                        logger.info("Using libsource source strategy")
                    else:
                        source.release()
                        logger.warning("libsource source strategy not available")
                else:
                    logger.warning("pisource2 not available")

            case "pi":
                if self._is_module_available("picamera2"):
                    from capture.impl.pi import PiCamera
                    source = PiCamera(width=width, height=height)
                    test_capture = source.get_frame()
                    if test_capture.frame is not None:
                        logger.info("Using libsource source strategy")
                    else:
                        source.release()
                        logger.warning("libsource source strategy not available")
                else:
                    logger.warning("pisource2 not available")

            case "default":
                if self._is_module_available("cv2"):
                    logger.info("Setting OpenCV source")
                    from capture.impl.opencv import OpenCVCamera
                    source = OpenCVCamera(device=device, width=width, height=height)
                    test_capture = source.get_frame()
                    if test_capture.frame is not None:
                        logger.info("Using OpenCV source strategy")
                    else:
                        source.release()
                        logger.warning("OpenCV source strategy not available")
                else:
                    logger.warning("cv2 not available")

            case "image":
                logger.info("Setting image source")
                from capture.impl.image import ImageGenerator
                source = ImageGenerator(width=width, height=height)
            case _:
                logger.info("Setting to static frame source")

        return source


    def _is_module_available(self, module_name: str) -> bool:
        spec = importlib.util.find_spec(module_name)
        available = spec is not None
        logger.debug(f"Module {module_name} available: {available}")
        return available


    def get_source(self) -> Source:
        logger.debug("Getting current source")
        return self._source


    def set_source_by_name(self, source_name: str) -> Source:
        logger.info(f"Setting source by name: {source_name}")
        self._source = self._create_source(source_name, "/dev/video0", 640, 480)
        return self._source


    def default_source(self) -> Source:
        logger.info("Setting default source to 'static'")
        return self.set_source_by_name("static")
