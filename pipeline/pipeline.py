from queue import Queue
import threading
import time
import logging

from sink.base.sink import Sink
from source.base.source import Source
from pipe.base.operation import Operation
from model.model import Frame, Result
from model.detection import Detection

logger = logging.getLogger(__name__)


class Pipeline:
    """
    Pipeline class to manage the flow of frames through the pipeline and 
    executes the operations on the frames. The pipeline is started by calling
    the `run_forever` method. The pipeline can be stopped by calling the `stop`
    method. After processing the frames, the results are sent to the sinks.
    """
    def __init__(
            self, 
            queue: Queue, 
            instances: dict[str, object],
            source: Source, 
            pipe: Operation, 
            sinks: list[Sink] = []):
        self._queue = queue
        self._source: Source = source
        self._pipe: Operation = pipe
        self._sinks: list[Sink] = sinks
        self._instances = instances
        self._stop_event = threading.Event()
        self._source_thread = None
        self._running = False
        
        logger.info("Pipeline initialized")

    
    
    def _start_source_loop(self):
        """"
        Start the source loop to get frames from the source and put them into the queue.
        """
        while not self._stop_event.is_set():
            if self._source:
                frame: Frame = self._source.get_frame()
                self._queue.put(frame)
            else:
                time.sleep(0.2) # save CPU cycles


    def _start_pipeline(self):
        """
        Run the pipeline by getting frames from the queue and processing them
        with the pipe. The results are sent to the sinks.
        """
        while self._running:
            frame: Frame = self._queue.get()
            det: list[Detection] = []

            if self._pipe:
                det = self._pipe.process(frame)
            result = Result(frame)
            result.add_detection(det)

            if self._sinks:
                for sink in self._sinks:
                    sink.put(result)


    def run_forever(self):
        """
        Start the pipeline thread and run the pipeline.
        """
        if self._source_thread and self._source_thread.is_alive():
            logger.info("Pipeline thread is already running")
            return

        logger.info("Starting Pipeline thread")
        self._stop_event.clear()
        self._running = True
        self._source_thread = threading.Thread(target=self._start_source_loop)
        self._source_thread.start()
        self._start_pipeline()


    def stop(self):
        """
        Stop the source thread.
        """
        logger.info("Stopping Pipeline threads")
        self._stop_event.set()
        if self._source_thread:
            self._source_thread.join()
            self._running = False


    def _restart_source_thread(self):
            self._stop_event.clear()
            self._source_thread = threading.Thread(target=self._start_source_loop)
            self._source_thread.start()


    def set_source(self, source_name: str) -> bool:
        """
        Set the source for the pipeline. 
        If the source is already set, it will be replaced.
        """
        if self._source is not None and self._source.get_name() == source_name:
            logger.info(f"Update source for {source_name}: nothing to change")
            return True

        self._stop_event.set()

        if self._source:
            self._source.release()
        
        available_sources = self._instances.get("sources")
        instance = available_sources.get(source_name)

        if instance is not None:
            self._source = instance
            instance.init()
            self._restart_source_thread()
            logger.info(f"Update source to {source_name}")
            return True

        logger.warning(f"Could not update source to {source_name}")
        return False


    def set_pipe(self, pipe_name: str) -> bool:
        """
        Set the pipe for the pipeline. 
        If the pipe is already set, it will be replaced.
        """
        if self._pipe is not None and self._pipe.get_name() == pipe_name:
            logger.info(f"Update pipe to {pipe_name}: nothing to change")
            return True

        available_pipes = self._instances.get("pipes")
        new_pipe = available_pipes.get(pipe_name)
        if new_pipe is not None:
            self._pipe = new_pipe
            logger.info(f"Update pipe to {pipe_name}")
            return True

        logger.warning(f"Could not update pipe to {pipe_name}")
        return False


    def set_sinks(self, sink_names: list[str]) -> bool:
        """
        Set the sinks for the pipeline.
        Multiple sinks can be set at once.
        """
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
                available_sinks = self._instances.get("sinks")
                instance = available_sinks.get(sink_name)
                if instance is not None:
                    logger.info(f"add sink: {sink_name}")
                    instance.init()
                    self._sinks.append(instance)
        return True

