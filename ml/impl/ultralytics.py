from ultralytics import YOLO

from controller.interfaces.operation import Operation


class UltralyticsInference(Operation):

    def __init__(self, path: str, model_name: str = "yolo11n.onnx"):
        self._model = YOLO(f"{path}/{model_name}")
        self._confidence = 0.5

    def process(self, frame):
        results = self._model(frame, verbose=False, conf=self._confidence)
        frame = results[0].plot()
        return frame
