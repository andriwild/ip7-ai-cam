
import argparse
import logging

from api.server import WebServer
from capture.impl.opencv import OpenCVCamera
from ml.impl.ulObjectDetection import UlObjectDetection
from pipeline.builder import PipelineBuilder
from pipeline.pipeline import Pipeline
from capture.impl.image import ImageGenerator
from sink.impl.console import Console


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main(host: str, port: int)-> None:
    pipeline: Pipeline = PipelineBuilder() \
    .add_source(OpenCVCamera()) \
    .add_source(ImageGenerator()) \
    .add_model(UlObjectDetection()) \
    .add_sink(Console()) \
    .add_sink(WebServer(host, port)) \
    .build()

    pipeline.start()



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip", type=str, default="0.0.0.0", help="ip address of the server")
    parser.add_argument("-o", "--port", type=int, default=8000, help="ephemeral port number of the server")
    args = vars(parser.parse_args())
    main(args["ip"], args["port"])

