# based on: https://pyimagesearch.com/2020/09/02/opencv-stream-video-to-web-browser-html-page/
# onnx runtime info: https://onnxruntime.ai/docs/tutorials/iot-edge/rasp-pi-cv.html


# TODO: was kann ein ultralytics model alles verarbeiten? Schnittstelle für model outputs (bounding boxen, ...)

import argparse
import logging

from annotator.keypointAnnotator import KeypointAnnotator
from annotator.maskAnnotator import MaskAnnotator
from capture.captureProducer import CaptureProducer
from config.configuration import Configuration
from controller.controller import Controller
from annotator.textAnnotator import TextAnnotator
from annotator.boxAnnotator import BoxAnnotator
from ml.modelCoordinator import ModelCoordinator
from sink.captureConsumer import CaptureConsumer


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main(host: str, port: int)-> None:
    model_coordinator = ModelCoordinator()

    controller = Controller()
    controller.add_operations([
        TextAnnotator(),
        model_coordinator,
        BoxAnnotator(),
        KeypointAnnotator(),
        MaskAnnotator()
    ])

    config = Configuration(host, port)

    capture_consumer = CaptureConsumer(controller, config)
    capture_consumer.start()

    capture_provider = CaptureProducer(controller)
    capture_provider.start()

    config.attach(capture_provider)
    config.attach(model_coordinator)
    config.attach(capture_consumer)

    input() # TODO: prevent from stopping properly


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip", type=str, default="0.0.0.0", help="ip address of the server")
    parser.add_argument("-o", "--port", type=int, default=8000, help="ephemeral port number of the server")
    args = vars(parser.parse_args())

    main(args["ip"], args["port"])

