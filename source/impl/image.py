import logging
import time
import os
from datetime import datetime

import cv2

from source.interface.source import Source
from model.model import Frame

logger = logging.getLogger(__name__)


class ImageGenerator(Source):

    def __init__(self, name: str, params):
        logger.info("Initializing ImageGenerator")
        super().__init__(name)
        self._name = name
        self._fps = params.get("fps", 1)
        self._image_path = params.get("image_path", "resources/images/image.jpg")
        self._images = []
        self._current_index = 0
        self._frame_interval = 1 / self._fps

        if os.path.isdir(self._image_path):
            logger.info(f"Loading images from directory: {self._image_path}")
            self._images = self._load_images_from_directory(self._image_path)
        elif os.path.isfile(self._image_path):
            logger.info(f"Single image specified: {self._image_path}")
            self._images = [self._image_path]
        else:
            logger.error(f"Invalid path specified: {self._image_path}")
            raise ValueError(f"Invalid path: {self._image_path}")

    def _load_images_from_directory(self, directory):
        images = []
        for root, _, files in os.walk(directory):
            for file in sorted(files):
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.tiff')):
                    images.append(os.path.join(root, file))
        return images

    def get_frame(self) -> Frame:
        if not self._images:
            logger.error("No images available for processing")
            raise RuntimeError("No images to process")

        start_time = time.time()

        image_path = self._images[self._current_index]
        logger.debug(f"Processing image: {image_path}")

        frame = cv2.imread(image_path)
        timestamp = datetime.now()

        frame_id = os.path.basename(image_path)  # Use image name as frame_id

        self._current_index = (self._current_index + 1) % len(self._images)

        elapsed_time = time.time() - start_time
        sleep_time = max(0, self._frame_interval - elapsed_time)
        time.sleep(sleep_time)

        return Frame(
            frame_id=frame_id,
            source_id=self._name,
            frame=frame,
            timestamp=timestamp
        )

    def release(self):
        logger.info("Releasing ImageGenerator")
