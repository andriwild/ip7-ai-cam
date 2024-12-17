import logging
from observer.subject import Subject
from observer.observer import Observer

logger = logging.getLogger(__name__)

class Configuration(Subject):

    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._source = "static"
        self._models = []
        self._observers = []
        self._sinks = ["console", "webserver"]
        logger.info("Configuration initialized with default source 'static'")


    def get_port(self):
        return self._port


    def get_host(self):
        return self._host


    # Observer pattern methods
    def attach(self, observer: Observer) -> None:
        self._observers.append(observer)
        logger.info(f"Observer {observer} attached")


    def detach(self, observer: Observer) -> None:
        self._observers.remove(observer)
        logger.info(f"Observer {observer} detached")


    def notify(self) -> None:
        logger.info("Notifying observers")
        for observer in self._observers:
            observer.update(self)


    # source property
    def get_source(self) -> str:
        logger.debug(f"Getting source: {self._source}")
        return self._source


    def set_source(self, source_name):
        logger.info(f"Setting source to {source_name}")
        self._source = source_name
        self.notify()


    # model property
    def get_models(self) -> list[str]:
        logger.debug(f"Getting models: {self._models}")
        return self._models


    def set_models(self, models: list[str]):
        logger.info(f"Setting models to {models}")
        self._models = models
        self.notify()


    # sink property
    def get_sinks(self) -> list[str]:
        logger.debug(f"Getting sinks: {self._sinks}")
        return self._sinks


    def set_sinks(self, sinks: list[str]):
        logger.info(f"Setting sinks to {sinks}")
        self._sinks = sinks
        self.notify()

