from pipeline.pipeline import Pipeline
import logging

logger = logging.getLogger(__name__)

class PipelineBuilder:
    def __init__(self):
        self._sources = []
        self._models = []
        self._sinks = []
        self._queue_size = 10
        self._active_source = None

    def add_source(self, source):
        """
        Add a source to the pipeline.
        """
        self._sources.append(source)
        logger.debug(f"Added source: {source.get_name()}")
        return self

    def set_active_source(self, source):
        """
        Set the active source for the pipeline.
        """
        self._active_source = source
        logger.debug(f"Set active source: {source.get_name()}")
        return self

    def add_model(self, model):
        """
        Add a model to the pipeline.
        """
        self._models.append(model)
        logger.debug(f"Added model: {model.get_name()}")
        return self

    def add_sink(self, sink):
        """
        Add a sink to the pipeline.
        """
        self._sinks.append(sink)
        logger.debug(f"Added sink: {sink.get_name()}")
        return self

    def set_queue_size(self, size):
        """
        Set the queue size for the pipeline.
        """
        self._queue_size = size
        logger.debug(f"Set queue size: {size}")
        return self

    def build(self) -> Pipeline:
        """
        Build and return the pipeline.
        """
        if not self._sources:
            raise ValueError("At least one source must be provided!")
        if not self._sinks:
            raise ValueError("At least one sink must be defined!")

        logger.info("Building pipeline.")
        return Pipeline(
            sources=self._sources,
            models=self._models,
            sinks=self._sinks,
            queue_size=self._queue_size,
        )
