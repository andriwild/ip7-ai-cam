from observer.observer import Observer
from observer.observer import Observer
from api.server import WebServer
from config.configuration import Configuration
from observer.subject import Subject
import logging
import threading
from controller.controller import Controller

from sink.impl.console import Console
from sink.interface.sink import Sink

logger = logging.getLogger(__name__)


class CaptureConsumer(Observer):

    def __init__(self, controller: Controller, config: Configuration):
        self._controller = controller
        self._stop_event = threading.Event()
        self._sinks: list[Sink] = [Console(), WebServer(controller, config)]
        self._config = config
        self._thread = None
        logger.info("Consumer initialized")


    def _sink_from_name(self, sink_name: str) -> Sink | None:
        match sink_name: 
            case "console":
                logger.info(f"Sink {sink_name} created")
                return Console()
            case "webserver":
                logger.info(f"Sink {sink_name} created")
                return WebServer(self._controller, self._config)
            case _:
                logger.error(f"Sink {sink_name} not found")
                return None


    def update(self, subject: Subject) -> None:
        if not isinstance(subject, Configuration):
            logger.error("Expected subject to be an instance of Configuration")
            raise TypeError("Expected subject to be an instance of Configuration")

        updated_sink_names: list[str] = subject.get_sinks()
        logger.info(f"Sink configuration updated: {updated_sink_names}")

        # Create a set of currently active sink names
        current_sink_names = {type(sink).__name__.lower() for sink in self._sinks}
        updated_sink_names_set = set(updated_sink_names)

        # Determine sinks to add and remove
        sinks_to_add = updated_sink_names_set - current_sink_names
        sinks_to_remove = current_sink_names - updated_sink_names_set

        for name in sinks_to_add:
            new_sink = self._sink_from_name(name)
            if new_sink:
                self._sinks.append(new_sink)
                logger.info(f"Added sink: {name}")

        self._sinks = [sink for sink in self._sinks if type(sink).__name__.lower() not in sinks_to_remove]
        for name in sinks_to_remove:
            logger.info(f"Removed sink: {name}")


    def start(self):
        """Start the consumer thread if it is not already running."""
        if self._thread and self._thread.is_alive():
            logger.info("Consumer thread is already running")
            return

        logger.info("Starting Consumer thread")
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()


    def stop(self):
        """Stop the consumer thread."""
        logger.info("Stopping Consumer thread")
        self._stop_event.set()
        if self._thread:
            self._thread.join()
            self._thread = None


    def _run(self):
        """Run method that processes data and passes it to sinks."""
        logger.info("Consumer run method started")
        while not self._stop_event.is_set():
            capture = self._controller.get()
            for sink in self._sinks:
                sink.put(capture)
        logger.info("Consumer run method stopped")
