import argparse
import logging
from queue import Queue
import importlib
import yaml

from pipeline.configServer import PipelineConfigurator
from pipeline.pipeline import Pipeline
from utilities.classLoader import ClassLoader

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def is_library_available(library_name):
    try:
        importlib.import_module(library_name)
        return True
    except ImportError:
        return False

    
def main(config_file: str, host: str, port: int)-> None:
    logger.info(f"Initialize Pipeline with config {config_file}")

    config = yaml.safe_load(open(config_file))
    instances = ClassLoader.instances_from_config(config)

    initial_sinks  = list(instances["sinks"].values())[0]
    initial_pipe   = list(instances["pipes"].values())[0]
    initial_source = list(instances["sources"].values())[0]

    queue  = Queue(maxsize=1)
    pipeline = Pipeline(queue, instances, initial_source, initial_pipe, [initial_sinks])
    PipelineConfigurator(pipeline, config, host, port)

    logger.info("Start pipline")
    pipeline.run_forever() # doesn't return


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    default_config = "config.yml"

    if is_library_available("picamera2"):
        default_config = "pi_config.yml"

    parser.add_argument("-c", "--config", type=str, default=default_config, help="config file to load configuration")
    parser.add_argument("-p", "--port", type=int, default=8001, help="port of the config server")
    parser.add_argument("-o", "--host", type=str, default="0.0.0.0", help="host of the config server")
    args = vars(parser.parse_args())
    main(args["config"], args["host"], args["port"])
