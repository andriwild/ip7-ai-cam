import threading
import logging

from ml.interface.operation import Operation
from model.result import BoxResult
from utilities.classLoader import ClassLoader
from model.resultWrapper import BoxWrapper
from observer.observer import Observer
from observer.subject import Subject
from config.config import ConfigManager


logger = logging.getLogger(__name__)

class Pipeline(Observer):
    def __init__(self, in_queue, out_queue):
        self.in_queue = in_queue
        self.out_queue = out_queue
        self._stop_event = threading.Event()
        self._thread = None
        self._steps: list[Operation] = []
        logger.info("Pipeline initialized")


    def _run(self):
        while not self._stop_event.is_set():
            print("pipeline running")
            frame = self.in_queue.get()
            if not frame:
                logger.warning("Received empty frame")
                continue
            #if self._steps:
            if False:
                result = self._steps[0].process(frame)
            else:
                result = BoxResult(frame_id=frame.frame_id, 
                                   frame=frame.frame, 
                                   boxes=BoxWrapper.dummy(None))

            self.out_queue.put(result)

    def start(self):
        if self._thread and self._thread.is_alive():
            logger.info("Pipeline thread is already running")
            return

        logger.info("Starting Pipeline thread")
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run)
        self._thread.start()

    def stop(self):
        logger.info("Stopping Pipeline thread")
        self._stop_event.set()
        if self._thread:
            self._thread.join()
            self._thread = None


    def _instantiate_step(self, load_config):
        src_cls = ClassLoader.get_class_from_file(load_config.file_path, load_config.class_name)
        if not src_cls:
            logger.error(f"Failed to load class {load_config.class_name} from {load_config.file_path}")
            return None
        return src_cls(load_config.name)


    def update(self, subject: Subject) -> None:
        logger.info("Pipeline received update from SettingsManager")

        if not isinstance(subject, ConfigManager):
            logger.error("not instance of SettingsManager")
            return

        new_steps_setting = subject.get_setting("steps")
        if not new_steps_setting:
            logger.warning("No steps found in settings")
            return
        
        if not isinstance(new_steps_setting, list):
            new_steps_setting = [new_steps_setting]
    
        old_step_names = {step.get_name() for step in self._steps}
        new_step_names = set(new_steps_setting)
    
        to_remove = old_step_names - new_step_names
        to_add = new_step_names - old_step_names

        logger.info(f"Removing steps: {to_remove}")
        logger.info(f"Adding steps: {to_add}")

        for step_obj in self._steps:
            if step_obj.get_name() in to_remove:
                self._steps.remove(step_obj)
    
        self._steps = [s for s in self._steps if s.get_name() not in to_remove]
    
        for step_name in to_add:
            load_cfg = subject.get_step_config_by_name(step_name)
            if not load_cfg:
                logger.warning(f"No LoadConfig found for step '{step_name}'")
                continue
            
            new_step_instance = self._instantiate_step(load_cfg)
            self._steps.append(new_step_instance)
