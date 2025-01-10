from queue import Queue
import threading
import time
import logging

from sink.interface.sink import Sink
from source.interface.source import Source
from step.interface.operation import Operation
from model.model import Frame, Result
from model.detection import Detection

logger = logging.getLogger(__name__)


class Pipeline:
    def __init__(self, queue: Queue, instances):

        self._queue = queue
        self._source: Source|None = None 
        self._pipe: Operation|None = None 
        self._sinks: list[Sink] = []
        self._instances = instances

        self._stop_event = threading.Event()
        self._source_thread = None
        self._running = False
        
        logger.info("Pipeline initialized")


    def _run_source(self):
        while not self._stop_event.is_set():
            if self._source:
                frame: Frame = self._source.get_frame()
                self._queue.put(frame)
            else:
                time.sleep(0.2) # save CPU cycles


    def _run_pipeline(self):
        while self._running:
            frame: Frame = self._queue.get()
            det: list[Detection] = []

            if self._pipe:
                det = self._pipe.process(frame.frame)
            result = Result(frame)
            result.add_detection(det)

            if self._sinks:
                for sink in self._sinks:
                    sink.put(result)


    def run_forever(self):
        if self._source_thread and self._source_thread.is_alive():
            logger.info("Pipeline thread is already running")
            return

        logger.info("Starting Pipeline thread")
        self._stop_event.clear()
        self._running = True
        self._source_thread = threading.Thread(target=self._run_source)
        self._source_thread.start()
        self._run_pipeline()


    def stop(self):
        logger.info("Stopping Pipeline threads")
        self._stop_event.set()
        if self._source_thread:
            self._source_thread.join()


    def _restart_source_thread(self):
            self._stop_event.clear()
            self._source_thread = threading.Thread(target=self._run_source)
            self._source_thread.start()


    def set_source(self, source_name: str) -> bool:

        if self._source is not None and self._source.get_name() == source_name:
            logger.info(f"Update source for {source_name}: nothing to change")
            return True

        self._stop_event.set()

        if self._source:
            self._source.release()
        
        sources = self._instances.get("sources")
        instance = sources.get(source_name)

        if instance is not None:
            self._source = instance
            instance.init()
            self._restart_source_thread()
            logger.info(f"Update source to {source_name}")
            return True

        logger.warning(f"Could not update source to {source_name}")
        return False


    def set_pipe(self, pipe_name: str) -> bool:
        if self._pipe is not None and self._pipe.get_name() == pipe_name:
            logger.info(f"Update pipe to {pipe_name}: nothing to change")
            return True

        pipes = self._instances.get("pipes")
        new_pipe = pipes.get(pipe_name)
        if new_pipe is not None:
            self._pipe = new_pipe
            logger.info(f"Update pipe to {pipe_name}")
            return True

        logger.warning(f"Could not update pipe to {pipe_name}")
        return False


    def set_sinks(self, sink_names: list[str]) -> bool:
        current_sink_names = [sink.get_name() for sink in self._sinks] if self._sinks else []

        # remove sinks
        for sink in self._sinks:
            if sink.get_name() not in sink_names:
                sink.release()
                logger.info(f"remove sink {sink.get_name()}")
                sink.release()
                self._sinks.remove(sink)

        # add new sinks
        for sink_name in sink_names:
            if sink_name not in current_sink_names:
                sinks = self._instances.get("sinks")
                instance = sinks.get(sink_name)
                if instance is not None:
                    logger.info(f"add sink: {sink_name}")
                    instance.init()
                    self._sinks.append(instance)
        return True


    # def update(self, subject: Subject) -> None:
    #     logger.info("Pipeline received update")
    #     assert isinstance(subject, ConfigManager)

    #     new_config = subject.get_config()

    #     # Determine current names
    #     current_source_name = self._source.get_name() if self._source else None
    #     current_step_name = self._step.get_name() if self._step else None
    #     current_sink_names = [sink.get_name() for sink in self._sinks] if self._sinks else []

    #     # Get new names from config
    #     new_source_name = new_config['sources'][0]['name'] if new_config['sources'] else None
    #     new_step_name = new_config['steps'][0]['name'] if new_config['steps'] else None
    #     new_sink_names = [sink['name'] for sink in new_config['sinks']]

    #     print("Pipeline update:")
    #     print("old: ", current_source_name, current_step_name, current_sink_names)
    #     print("new: ", new_source_name, new_step_name, new_sink_names)

    #     # Identify changes
    #     if current_source_name != new_source_name:
    #         self._stop_event.set()
    #         if self._source:
    #             logger.info(f"Removing source: {current_source_name}")
    #             self._source.release()
    #             self._source = None
    #         if new_source_name:
    #             logger.info(f"Loading source: {new_source_name}")
    #             self._source = ClassLoader.instantiate_class(new_config['sources'][0])

    #     if current_step_name != new_step_name:
    #         if self._step:
    #             logger.info(f"Removing step: {current_step_name}")
    #             self._step = None
    #         if new_step_name:
    #             logger.info(f"Loading step: {new_step_name}")
    #             step_config = new_config['steps'][0]
    #             self._step = ClassLoader.instantiate_class(step_config)

    #     for sink in self._sinks:
    #         if sink.get_name() not in new_sink_names:
    #             logger.info(f"Removing sink: {sink.get_name()}")
    #             sink.release()
    #     self._sinks = [
    #         sink for sink in self._sinks if sink.get_name() in new_sink_names
    #     ]

    #     for sink_config in new_config['sinks']:
    #         if sink_config['name'] not in current_sink_names:
    #             logger.info(f"Loading sink: {sink_config['name']}")
    #             self._sinks.append(ClassLoader.instantiate_class(sink_config))



    #     self._stop_event = threading.Event()
    #     self._source_thread = threading.Thread(target=self._run_source)
    #     self._source_thread.start()
