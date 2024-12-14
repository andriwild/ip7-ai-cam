# based on: https://pyimagesearch.com/2020/09/02/opencv-stream-video-to-web-browser-html-page/
# onnx runtime info: https://onnxruntime.ai/docs/tutorials/iot-edge/rasp-pi-cv.html



# TODO: was kann ein ultralytics model alles verarbeiten? Schnittstelle für model outputs (bounding boxen, ...)
import argparse
import logging

from ultralytics import YOLO

from api.server import WebServer
from camera_adapter.frameProvider import FrameProvider
from configuration import Configuration
from controller import Controller

model = YOLO("resources/ml_models/yolo11n.onnx")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


def main(host: str, port: int)-> None:
    controller = Controller()

    config = Configuration()

    frame_provider = FrameProvider(controller)
    frame_provider.start()

    config.attach(frame_provider)

    server = WebServer(controller, config)
    server.run(host, port)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip", type=str, default="0.0.0.0", help="ip address of the server")
    parser.add_argument("-o", "--port", type=int, default=8000, help="ephemeral port number of the server")
    args = vars(parser.parse_args())

    main(args["ip"], args["port"])

