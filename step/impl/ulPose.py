from ultralytics import YOLO

from step.interface.operation import Operation
import torch
import numpy as np
from model.frame import Frame
from model.resultWrapper import KeypointWrapper
from model.detection import Detection, Keypoint


class UlPose(Operation):

    def __init__(self, name: str, params):
        super().__init__(name)
        self._model_path = params.get("model_path", "./resources/ml_models/yolo11n-pose.onnx")
        self._model = YOLO(self._model_path)
        self._confidence = params.get("confidence_threshold", 0.5)

    def process(self, frame: np.ndarray) -> list[Detection]:
        result = self._model(frame, verbose=False, conf=self._confidence)
        # keypoint_wrapper = KeypointWrapper.from_ultralytics(results[0])
        #speed : dict[str, float | None] = results[0].speed

        keypoints = result[0].keypoints
        if keypoints is None:
            keypoints = []

        # return KeypointResult(
        #     frame_id = frame.frame_id,
        #     frame = frame.frame,
        #     inference_time=speed["inference"],
        #     preprocess_time=speed["preprocess"],
        #     postprocess_time=speed["postprocess"],
        #     keypoint=keypoint_wrapper
        # )
        return [Keypoint(keypoints=keypoints)]

        
