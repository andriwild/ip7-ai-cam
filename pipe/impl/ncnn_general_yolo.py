from model.detection import Box
from model.model import Frame
from utilities.formatConverter import convert_xywh_to_xywhn
import multiprocessing
from pipe.base.operation import Operation
import logging
from ncnn.model_zoo import get_model
import multiprocessing

logger = logging.getLogger(__name__)

class NCNNGeneral(Operation):
    def __init__(self, name: str, params):
        super().__init__(name)

        cores = multiprocessing.cpu_count()
        self.net = get_model(
            params.get("model"),
            target_size=640,
            prob_threshold=params.get("confidence_threshold", 0.5),
            nms_threshold=params.get("nms_threshold", 0.5),
            num_threads=params.get("num_threads", cores),
            use_gpu=params.get("use_gpu", False),
        )

    def process(self, frame: Frame) -> list[Box]:
        r = self.net(frame.image)
        boxes = []
        for obj in r:
            re = obj.rect
            result = convert_xywh_to_xywhn((re.x, re.y, re.w, re.h), frame.image.shape[1], frame.image.shape[0])
            boxes.append(Box(result, obj.prob, obj.label))

        return boxes

