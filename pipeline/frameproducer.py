import logging
import threading
import time

from model.config import ConfigManager
from model.fps_queue import FpsQueue
from model.loadConfig import LoadConfig
from model.observer.observer import Observer
from model.observer.subject import Subject
from utilities.classLoader import ClassLoader

logger = logging.getLogger(__name__)


class FrameProducer(Observer):
    def __init__(self, queue: FpsQueue):
        self._queue = queue
        self._source_instance = None
        self._current_source_name = None
        self._stop_event = threading.Event()
        self._thread = None


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


    def _instantiate_source(self, load_config: LoadConfig):
        src_cls = ClassLoader.get_class_from_file(load_config.file_path, load_config.class_name)
        if not src_cls:
            logger.error(f"Failed to load class {load_config.class_name} from {load_config.file_path}")
            exit(1)
        params = load_config.parameters if load_config.parameters else {}
        return src_cls(load_config.name, params)


    def _run(self):
        logger.info("CaptureProducer run method started")
        while not self._stop_event.is_set():
            if self._source_instance:
                frame = self._source_instance.get_frame()
                if frame is not None:
                    self._queue.put(frame)
        logger.info("CaptureProducer run method stopped")


    def update(self, subject: Subject) -> None:
        if not isinstance(subject, ConfigManager):
            logger.error("not instance of SettingsManager")
            return

        new_source_name = subject.get_setting("source")
        if not new_source_name:
            logger.warning("No new source name")
            return

        if new_source_name == self._current_source_name:
            logger.info(f"CaptureProducer: source unchanged: {new_source_name}")
            return

        new_conf = subject.get_source_config_by_name(new_source_name)
        if new_conf:
            self.stop()
            # Instantiate the new source
            if self._source_instance:
                self._source_instance.release()
            self._source_instance = self._instantiate_source(new_conf)
            self._current_source_name = new_source_name
            logger.info(f"CaptureProducer: source changed to {new_source_name}")
            self.start()
        else:
            logger.warning(f"No LoadConfig found for source '{new_source_name}'")

