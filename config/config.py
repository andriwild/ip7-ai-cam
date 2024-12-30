import logging
import threading
from typing import Any, Dict, List

import yaml

from model.loadConfig import LoadConfig
from model.singleton import SingletonMeta
from observer.observer import Observer
from observer.subject import Subject

logger = logging.getLogger(__name__)

class ConfigManager(Subject, metaclass=SingletonMeta):
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._config = None
        self._settings: Dict[str, Any] = {
            "source": None,
            "steps": None,
            "sinks": None,
        }
        self._observers: List[Observer] = []
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


    def update_setting(self, key: str, value: Any) -> None:
        logger.info(f"Updating setting {key} to {value}")
        self._settings[key] = value
        self.notify()


    def get_setting(self, key: str) -> Any:
        with self._lock:
            return self._settings.get(key, None)


    def load_config(self, file: str):
        logger.info(f"Loading settings from {file}")
        self._config = yaml.safe_load(open(file))

        sinks =  [sink["name"] for sink in self._config.get("sinks", [])]
        steps =  [step["name"] for step in self._config.get("steps", [])]
        source =  self._config.get("sources", [])[0]["name"]

        self.update_setting("sinks", sinks)
        self.update_setting("steps", steps)
        self.update_setting("source", source)


    def get_source_config_by_name(self, name: str):
        sources = [LoadConfig(**source) for source in self._config["sources"]]
        for source in sources:
            if source.name == name:
                return source
        return None


    def get_sink_config_by_name(self, name: str):
        sinks = [LoadConfig(**sink) for sink in self._config["sinks"]]
        for sink in sinks:
            if sink.name == name:
                return sink
        return None


    def get_step_config_by_name(self, name: str):
        steps = [LoadConfig(**step) for step in self._config["steps"]]
        for step in steps:
            if step.name == name:
                return step
        return None


    def get_config(self):
        return self._config
    

    def get_sources(self)-> List[LoadConfig]:
        if not self._config:
            return []
        return [LoadConfig(**source) for source in self._config["sources"]]


    def get_sinks(self)-> List[LoadConfig]:
        if not self._config:
            return []
        return [LoadConfig(**sink) for sink in self._config["sinks"]]

