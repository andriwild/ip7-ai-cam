from dataclasses import dataclass
import threading
import logging
from typing import Optional

from collections import defaultdict, deque
from ml.interface.operation import Operation
from model.frame import Frame
from utilities.classLoader import ClassLoader
from observer.observer import Observer
from observer.subject import Subject
from config.config import ConfigManager
from model.detection import Box, Mask, Keypoint
from dataclasses import dataclass, field
import numpy as np


logger = logging.getLogger(__name__)



@dataclass
class Prediction:
    infer_data: list[Box|Mask|Keypoint]
    model_name: str


@dataclass
class Result:
    frame: Frame
    predictions: list[Prediction] = field(default_factory=list) 

    def add_prediction(self, prediction: Prediction):
        self.predictions.append(prediction)



@dataclass
class Step:
    operation: Operation
    name: str
    task: Optional[str] = "detect"
    input_id: Optional[str] = "raw_image"
    output_id: Optional[str] = None

def sort_steps(steps):
    # Build a graph of dependencies
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    step_map = {step.output_id: step for step in steps if step.output_id}

    for step in steps:
        if step.input_id and step.output_id:
            graph[step.input_id].append(step.output_id)
            in_degree[step.output_id] += 1

    # Output graph for debugging
    print("Graph:")
    for key, value in graph.items():
        print(f"{key} -> {value}")

    # Check for root existence (raw_image)
    if "raw_image" not in {step.input_id for step in steps}:
        logger.error("Missing root step: 'raw_image'")
        exit(1)

    # Topological Sort (Kahn's Algorithm)
    queue = deque([node for node in graph if node == "raw_image"])
    sorted_steps = []

    while queue:
        current = queue.popleft()

        for neighbor in graph[current]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

            if neighbor in step_map:
                sorted_steps.append(step_map[neighbor])

    # Check if all steps with output_id are processed
    all_output_ids = {step.output_id for step in steps if step.output_id}
    processed_output_ids = {step.output_id for step in sorted_steps}

    if all_output_ids != processed_output_ids:
        logger.error("Not all steps with output_id are processed")
        exit(1)

    return sorted_steps


class Pipeline(Observer):
    def __init__(self, in_queue, out_queue):
        self.in_queue = in_queue
        self.out_queue = out_queue
        self._stop_event = threading.Event()
        self._thread = None
        self._steps: list[Step] = []
        logger.info("Pipeline initialized")



    def _preprocess(self, input: Prediction, frame: np.ndarray) -> list[np.ndarray]:
        cropped_images = []

        # Iterate over the infer_data to process only Box objects
        for item in input.infer_data:
            if isinstance(item, Box):  # Check if the item is a Box
                height, width = frame.shape[:2]
                x_center, y_center, w, h = item.xywhn

                # Convert normalized coordinates to pixel coordinates
                x1 = int((x_center - w / 2) * width)
                y1 = int((y_center - h / 2) * height)
                x2 = int((x_center + w / 2) * width)
                y2 = int((y_center + h / 2) * height)

                # Clip coordinates to image boundaries
                x1, y1 = max(0, x1), max(0, y1)
                x2, y2 = min(width, x2), min(height, y2)

                # Crop the image region
                cropped_image = frame[y1:y2, x1:x2]
                cropped_images.append(cropped_image)
        
        return cropped_images

    def _run(self):
        self._steps = sort_steps(self._steps)

        while not self._stop_event.is_set():
            frame = self.in_queue.get()
            result_map: dict[str, Prediction] = {}

            if not frame:
                logger.warning("Received empty frame")
                continue

            for step in self._steps:
                if step.input_id == "raw_image":
                    input = frame.frame
                else:
                    prev_det = result_map.get(step.input_id)
                    input = self._preprocess(prev_det, frame.frame) # TODO: e.g. cut out the detected object from the frame
                    if not input: 
                        logger.error(f"Missing input {step.input_id} for step {step.name}")
                        exit(1)

                detections = step.operation.process(input)

                p = Prediction(infer_data=detections, model_name=step.name)

                result_map[step.output_id] = p

            result = Result(frame)
            for key in result_map.keys():
                result.add_prediction(result_map[key])

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



    def _instantiate_step(self, path, name, params) -> Operation | None:
        src_cls = ClassLoader.get_class_from_file(path, name)
        if not src_cls:
            logger.error(f"Failed to load class {name} from {path}")
            return None
        return src_cls(name, params)


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
    
        old_step_names = {step.name for step in self._steps}
        new_step_names = set(new_steps_setting)
    
        to_remove = old_step_names - new_step_names
        to_add = new_step_names - old_step_names

        logger.info(f"Removing steps: {to_remove}")
        logger.info(f"Adding steps: {to_add}")

        for step_obj in self._steps:
            if step_obj.name in to_remove:
                self._steps.remove(step_obj)
    
        self._steps = [s for s in self._steps if s.name not in to_remove]
    
        for step_name in to_add:
            load_cfg = subject.get_step_config_by_name(step_name)
            if not load_cfg:
                logger.warning(f"No LoadConfig found for step '{step_name}'")
                continue
            
            new_step_instance = self._instantiate_step(load_cfg.file_path, load_cfg.class_name, load_cfg.parameters)
            if not new_step_instance:
                logger.warning(f"Failed to instantiate step '{step_name}'")
            else:
                self._steps.append(Step(new_step_instance, load_cfg.name, load_cfg.task, load_cfg.input_id, load_cfg.output_id))

