import argparse
import logging
import yaml
from queue import Queue

from config.configServer import PipelineConfigurator
from pipeline.pipeline import Pipeline
from utilities.classLoader import ClassLoader

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
    
def main(config_file: str, host: str, port: int)-> None:
    logger.info(f"Initialize Pipeline with config {config_file}")

    config = yaml.safe_load(open(config_file))
    instances = ClassLoader.instances_from_config(config)

    queue  = Queue(maxsize=1)
    pipeline = Pipeline(queue, instances)
    PipelineConfigurator(pipeline, config, host, port)

    logger.info("Start pipline")
    pipeline.run_forever() # doesn't return



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str, default="config.yml", help="config file to load configuration")
    parser.add_argument("-p", "--port", type=int, default=8001, help="port of the config server")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="host of the config server")
    args = vars(parser.parse_args())
    main(args["config"], args["host"], args["port"])
