import threading
import logging

from capture.sourceFactory import SourceFactory
from config.configuration import Configuration
from controller.controller import Controller
from capture.interface.source import Source
from observer.subject import Subject
from observer.observer import Observer

logger = logging.getLogger(__name__)

class CaptureProducer(Observer):

    def __init__(self, controller: Controller):
        self._controller = controller
        self._stop_event = threading.Event()
        self._source_factory = SourceFactory()
        self._source: Source = self._source_factory.default_source()
        self._thread = None
        logger.info("CaptureProducer initialized with default source")


    def _run(self):
        logger.info("CaptureProducer run method started")

        while not self._stop_event.is_set():
            capture = self._source.get_frame()
            self._controller.put(capture)

        logger.info("CaptureProducer run method stopped")


    def start(self):
        if self._thread and self._thread.is_alive():
            logger.warning("CaptureProducer thread is already running")
            return

        logger.info("Starting CaptureProducer thread")
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()


    def stop(self):
        logger.info("Stopping CaptureProducer thread")
        self._stop_event.set()
        if self._thread:
            self._thread.join()
            self._thread = None


    def update(self, subject: Subject) -> None:
        if not isinstance(subject, Configuration):
            logger.error("Expected subject to be an instance of Configuration")
            raise TypeError("Expected subject to be an instance of Configuration")

        new_source_name: str = subject.get_source()
        logger.info(f"Updating source to {new_source_name}")

        if self._source.get_name() == new_source_name:
            logger.info("Source ealready set to the desired configuration")
            return

        self.stop()  # Stop the current thread

        if self._source is not None:
            self._source.release()
        self._source = self._source_factory.set_source_by_name(new_source_name)

        logger.info(f"Source updated to {new_source_name}.")

        test_capture = self._source.get_frame()
        if test_capture is None:
            logger.error(f"Source could not be updated to {new_source_name}, setting to default source")
            self._source = self._source_factory.default_source()

        self.start()  # Restart the thread
