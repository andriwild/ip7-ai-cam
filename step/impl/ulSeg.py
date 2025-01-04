from ultralytics import YOLO

from step.interface.operation import Operation
from model.frame import Frame
from model.result import Result
from model.result import MaskResult
from model.resultWrapper import MaskWrapper


class UlSeg(Operation):

    def __init__(self, name: str, model_path: str = "yolo11n-seg.onnx", confidence: float = 0.5):
        super().__init__(name)
        self._model = YOLO(model_path)
        self._confidence = confidence

    def process(self, frame: Frame) -> Result:
        results = self._model(frame.frame, verbose=False, conf=self._confidence)
        mask_wrapper = MaskWrapper.from_ultralytics(results[0])
        speed : dict[str, float | None] = results[0].speed
        return MaskResult(
            frame_id = frame.frame_id,
            frame = frame.frame,
            inference_time=speed["inference"],
            preprocess_time=speed["preprocess"],
            postprocess_time=speed["postprocess"],
            masks=mask_wrapper
        )
