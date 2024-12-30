import logging
import threading

from config.config import ConfigManager
from model.fps_queue import FpsQueue
from observer.observer import Observer
from observer.subject import Subject
from utilities.classLoader import ClassLoader

logger = logging.getLogger(__name__)

class ResultConsumer(Observer):
    def __init__(self, queue: FpsQueue):
        self._queue = queue
        self._stop_event = threading.Event()
        self._thread = None
        self._sinks = []


    def start(self):
        if self._thread and self._thread.is_alive():
            logger.info("Consumer thread is already running")
            return

        logger.info("Starting Consumer thread")
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        logger.info("Stopping Consumer thread")
        self._stop_event.set()
        if self._thread:
            self._thread.join()
            self._thread = None

    def _run(self):
        logger.info("Consumer run method started")
        while not self._stop_event.is_set():
            print("consumer running")
            capture = self._queue.get()  # might be a BoxResult or something else
            for sink in self._sinks:
                sink.put(capture)
        logger.info("Consumer run method stopped")

    def _instantiate_sink(self, load_config):
        src_cls = ClassLoader.get_class_from_file(load_config.file_path, load_config.class_name)
        if not src_cls:
            logger.error(f"Failed to load class {load_config.class_name} from {load_config.file_path}")
            return None
        return src_cls(load_config.name)


    def update(self, subject: Subject) -> None:
        logger.info("Consumer received update from SettingsManager")

        if not isinstance(subject, ConfigManager):
            logger.error("not instance of SettingsManager")
            return

        new_sinks_setting = subject.get_setting("sinks")
        if not new_sinks_setting:
            logger.warning("No sinks found in settings")
            return
        
        if not isinstance(new_sinks_setting, list):
            new_sinks_setting = [new_sinks_setting]
    
        old_sink_names = {sink.get_name() for sink in self._sinks}
        new_sink_names = set(new_sinks_setting)
    
        to_remove = old_sink_names - new_sink_names
        to_add = new_sink_names - old_sink_names
        logger.info(f"Removing sinks: {to_remove}")
        logger.info(f"Adding sinks: {to_add}")

        for sink_obj in self._sinks:
            if sink_obj.get_name() in to_remove:
                sink_obj.release()  # free resources, stop threads, etc.
                sink_obj = None
    
        self._sinks = [s for s in self._sinks if s.get_name() not in to_remove]
    
        for sink_name in to_add:
            load_cfg = subject.get_sink_config_by_name(sink_name)
            if not load_cfg:
                logger.warning(f"No LoadConfig found for sink '{sink_name}'")
                continue
            
            new_sink_instance = self._instantiate_sink(load_cfg)
            self._sinks.append(new_sink_instance)

