from model.capture import Capture
from sink.interface.sink import Sink


class Console(Sink):

    def put(self, capture: Capture) -> None:
        boxes = capture.get_boxes()
        n = 0
        if boxes:
            n = len(boxes)
        print(f"Boxes: {n}")
