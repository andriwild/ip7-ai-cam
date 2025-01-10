import logging
import threading

from model.observer.observer import Observer
from model.observer.subject import Subject

logger = logging.getLogger(__name__)

class ConfigManager(Subject):
    def __init__(self, config: dict) -> None:
        self._lock = threading.Lock()
        self._config = config
        self._observers: list[Observer] = []
        logger.info("ConfigManager initialized")


    def attach(self, observer: Observer) -> None:
        with self._lock:
            if observer not in self._observers:
                self._observers.append(observer)


    def detach(self, observer: Observer) -> None:
        with self._lock:
            if observer in self._observers:
                self._observers.remove(observer)


    def notify(self) -> None:
        logger.info("Notifying observers")
        for observer in self._observers:
            observer.update(self)


    def update_setting(self, config) -> None:
        logger.info(f"Updating setting")
        self._config = config
        self.notify()


    def get_config(self):
        return self._config
    
