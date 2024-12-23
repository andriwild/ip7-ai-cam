
import threading
from queue import Queue
import logging

from capture.frameProducer import CaptureProducer
from model.result import BoxResult
from model.resultWrapper import BoxWrapper
from sink.captureConsumer import CaptureConsumer

# Configure logging
logger = logging.getLogger(__name__)

class Pipeline:
    def __init__(self, sources, models, sinks, queue_size=10):
        """
        Initialize the Pipeline.
        :param sources: List of source objects.
        :param models: List of model objects with an `infer` method.
        :param sinks: List of sink objects.
        :param queue_size: Size of the internal queue.
        :param active_source: The source object that acts as the active source.
        """
        self.sources = sources
        self.models = models
        self.sinks = sinks
        self.in_queue = Queue(maxsize=queue_size)
        self.out_queue = Queue(maxsize=queue_size)
        self.running = False
        self.producer = CaptureProducer(self.in_queue, sources)
        self.consumer = CaptureConsumer(self.out_queue, sinks)

    def start(self):
        logger.info("Starting pipeline.")
        logger.info(self)

        self.running = True

        self.producer.start()
        self.consumer.start()

        # Start the model threads
        def transform():
            while self.running:
                frame = self.in_queue.get()
                result = self.models[0].process(frame)
                #result = BoxResult(frame_id=frame.frame_id, frame=frame.frame, boxes=BoxWrapper.dummy(None))
                self.out_queue.put(result)

        threading.Thread(target=transform).start()

        
    def stop(self):
        """
        Stop the pipeline and all its components.
        """
        self.running = False
        logger.info("Stopping pipeline...")


    def __str__(self) -> str:
        """
        Create a string representation of the pipeline.
        :return: String with details about sources, model, sinks, and configuration.
        """
        sources_names = [source.get_name() for source in self.sources]
        sinks_names = [sink.get_name() for sink in self.sinks]
        model_names = [model.get_name() for model in self.models]

        return (
            f"\nPipeline:\n"
            f"  Sources: {', '.join(sources_names)}\n"
            f"  Model: {', '.join(model_names)}\n"
            f"  Sinks: {', '.join(sinks_names)}\n" 
            f"  Input Queue Size: {self.in_queue.maxsize}\n"
            f"  Output Queue Size: {self.out_queue.maxsize}\n"
            f"  Running: {'Yes' if self.running else 'No'}")
