import threading
import cv2
import datetime
import logging

from camera_adapter.cameraFactory import CameraFactory
from configuration import Configuration
from observer.subject import Subject
from observer.observer import Observer
from queue import Queue, Empty

logger = logging.getLogger(__name__)

class FrameProvider(Observer):

    def __init__(self, frame_queue: Queue):
        self.frame_queue = frame_queue
        self._stop_event = threading.Event()
        self._frame_factory = CameraFactory()
        self._camera = self._frame_factory.default_camera()
        self._thread = None
        logger.info("FrameProvider initialized with default camera")


    def _run(self):
        logger.info("FrameProvider run method started")

        while not self._stop_event.is_set():
            frame = self._camera.get_frame()

            if frame is None:
                break

            timestamp = datetime.datetime.now()
            cv2.putText(
                frame,
                timestamp.strftime("%A %d %B %Y %I:%M:%S%p"),
                (10, frame.shape[0] - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.35,
                (0, 0, 255),
                1
            )

            if self.frame_queue.full():
                logger.info("frame queue is full")
                try:
                    self.frame_queue.get_nowait()  # discard oldest frame
                except Empty:
                    pass
            self.frame_queue.put(frame)

        logger.info("FrameProvider run method stopped")


    def start(self):
        if self._thread and self._thread.is_alive():
            logger.warning("FrameProvider thread is already running")
            return

        logger.info("Starting FrameProvider thread")
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()


    def stop(self):
        logger.info("Stopping FrameProvider thread")
        self._stop_event.set()
        if self._thread:
            self._thread.join()
            self._thread = None


    def update(self, subject: Subject) -> None:
        if not isinstance(subject, Configuration):
            logger.error("Expected subject to be an instance of Configuration")
            raise TypeError("Expected subject to be an instance of Configuration")

        new_camera_name: str = subject.get_camera()
        logger.info(f"Updating camera to {new_camera_name}")

        if self._camera.get_name() == new_camera_name:
            logger.info("Camera already set to the desired configuration")
            return

        self.stop()  # Stop the current thread

        if self._camera is not None:
            self._camera.release()
        self._camera = self._frame_factory.set_camera_by_name(new_camera_name)

        logger.info(f"Camera updated to {new_camera_name}.")

        test_frame = self._camera.get_frame()
        if test_frame is None:
            logger.error(f"Camera could not be updated to {new_camera_name}, setting to default camera")
            self._camera = self._frame_factory.default_camera()

        self.start()  # Restart the thread
