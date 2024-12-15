from ultralytics import YOLO

from controller.interfaces.operation import Operation


class UltralyticsInference(Operation):

    def __init__(self):
        self._model = YOLO("resources/ml_models/yolo11n.onnx")
        self._confidence = 0.5

    def process(self, frame):
        results = self._model(frame, verbose=False, conf=self._confidence)
        frame = results[0].plot()
        return frame
