import argparse
import logging
import yaml
from queue import Queue
from pprint import pprint

from model.configServer import ConfigServer
from model.config import ConfigManager
from step.impl.bridge import Bridge
from pipeline.pipeline import Pipeline
from sink.impl.console import Console
from sink.interface.sink import Sink
from source.impl.opencv import OpenCVCamera
from source.interface.source import Source
from step.interface.operation import Operation

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def load_config(file_path: str):
    logger.info(f"Loading settings from {file_path}")
    config = yaml.safe_load(open(file_path))

    settings = {
        "sinks": config.get("sinks"),
        "steps": config.get("steps"),
        "sources": config.get("sources"),
    }
    return settings


def main(config_file: str)-> None:
    logger.info(f"Start Edge ML Pipeline")
    config = load_config(config_file)
    pprint(config)


    manager = ConfigManager(config)
    ConfigServer(manager, config, "0.0.0.0", 8001)

    queue  = Queue(maxsize=10)
    pipeline = Pipeline(queue=queue)

    manager.attach(pipeline)
    pipeline.run_forever()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str, default="config.yml", help="config file to load configuration")
    args = vars(parser.parse_args())
    main(args["config"])
