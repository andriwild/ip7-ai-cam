import threading
import logging
from typing import Optional

from collections import defaultdict, deque
from step.interface.operation import Operation
from model.frame import Frame
from utilities.classLoader import ClassLoader
from model.observer.observer import Observer
from model.observer.subject import Subject
from model.config import ConfigManager
from model.detection import Box, Mask, Keypoint
from dataclasses import dataclass, field
import numpy as np


logger = logging.getLogger(__name__)


@dataclass
class Prediction:
    infer_data: list[Box|Mask|Keypoint]
    model_name: str
    annotate: bool


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
    annotate: bool
    input_id: str = "raw_image"
    output_id: Optional[str] = None

# TODO: also validate that the graph
def sort_steps(steps):
    if len(steps) == 0:
        return steps

    # Build a graph of dependencies
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    step_map = {step.output_id: step for step in steps if step.output_id}

    for step in steps:
        if step.input_id and step.output_id:
            graph[step.input_id].append(step.output_id)
            in_degree[step.output_id] += 1

    # Output graph for debugging
    if logger.isEnabledFor(logging.INFO):
        graph_str = "Graph:\n"
        graph_str += "-" * 50 + "\n"
        for key, value in graph.items():
            graph_str += f"\t{key} -> {value}\n"
        graph_str += "-" * 50 + "\n"
        logger.info(graph_str)

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



    def _preprocess(self, boxes: list[Box], frame: np.ndarray) -> list[np.ndarray]:
        cropped_images = []

        for item in boxes: 
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



    def _predict_from_original_frame(self, input, step) -> Prediction:
        detections = step.operation.process(input)
        p = Prediction(
            infer_data=detections, 
            model_name=step.name, 
            annotate=step.annotate)
        return p

    def _predict_from_previous_prediction(self, frame: np.ndarray, step: Step, prediction) -> Prediction:
        results = []
        height, width = frame.shape[:2]
        boxes = prediction.infer_data
        cropped_images = self._preprocess(boxes, frame)

        for i, crop in enumerate(cropped_images):
            crop_h, crop_w = crop.shape[:2]
            detections: list[Box] = step.operation.process(crop)
            x1_item = (boxes[i].xywhn[0] - boxes[i].xywhn[2] / 2) * width
            y1_item = (boxes[i].xywhn[1] - boxes[i].xywhn[3] / 2) * height

            for det in detections:
                cx_crop = det.xywhn[0] * crop_w
                cy_crop = det.xywhn[1] * crop_h
                w_crop = det.xywhn[2] * crop_w
                h_crop = det.xywhn[3] * crop_h

                cx_orig = x1_item + cx_crop# + w_crop / 2
                cy_orig = y1_item + cy_crop# + h_crop / 2
                w_orig = w_crop
                h_orig = h_crop

                cx_norm = cx_orig / width
                cy_norm = cy_orig / height
                w_norm = w_orig / width
                h_norm = h_orig / height

                results.append(
                    Box(
                        xywhn=(cx_norm, cy_norm, w_norm, h_norm),
                        conf=det.conf,
                        label=str(det.label)
                    )
                )

        return Prediction(
            infer_data=results,
            model_name=step.name,
            annotate=step.annotate
        )


    def _run_all_steps(self, frame: np.ndarray) -> dict[str, Prediction]:
        result_map: dict[str, Prediction] = {}

        for step in self._steps:
           if step.input_id == "raw_image":
               p = self._predict_from_original_frame(frame, step)
           else:
               prev_prediction = result_map.get(step.input_id)
               p = self._predict_from_previous_prediction(frame, step, prev_prediction)

           if step.output_id:
               result_map[step.output_id] = p

        return result_map


    def _run(self):
        self._steps = sort_steps(self._steps)

        while not self._stop_event.is_set():
            frame: Frame = self.in_queue.get()
            result = Result(frame)
            if self._steps:
                result_map = self._run_all_steps(frame.frame)
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
            exit(1)
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
                input_id = load_cfg.parameters.get("input_id", "raw_image")
                output_id = load_cfg.parameters.get("output_id")
                annotate =  load_cfg.parameters.get("annotate", False)
                self._steps.append(Step(new_step_instance, load_cfg.name, annotate, input_id, output_id))

