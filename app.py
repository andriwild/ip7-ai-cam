import argparse         # For handling command-line arguments
import logging          # For logging messages (info, debug, etc.)
from queue import Queue # For creating a thread-safe queue
import yaml             # To load configuration files written in YAML

# Import custom modules:
# - PipelineConfigurator: Likely manages a configuration server for the pipeline.
# - Pipeline: Handles the main data processing pipeline.
# - ClassLoader: Dynamically loads classes/instances based on configuration.
# - is_library_available: Checks if a Python library is installed.
from pipeline.configServer import PipelineConfigurator
from pipeline.pipeline import Pipeline
from utilities.classLoader import ClassLoader
from utilities.helper import is_library_available


# Configure the logging system:
# This sets the logging level to INFO and specifies the format of log messages.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create a logger specific to this module.
logger = logging.getLogger(__name__)
    
def main(config_file: str, host: str, port: int, queue_size: int)-> None:
    """
    Main function to initialize and run the data pipeline.

    Parameters:
    - config_file (str): Path to the YAML configuration file.
    - host (str): Host address for the configuration server.
    - port (int): Port number for the configuration server.
    - queue_size (int): Maximum number of items (e.g., frames) the queue can hold.
    """
    logger.info(f"Initialize Pipeline with config {config_file}")
    
    # Load configuration data from the provided YAML file.
    config = yaml.safe_load(open(config_file))

    # Dynamically instantiate classes for different pipeline components using the configuration.
    # 'instances' is expected to be a dictionary with keys such as 'sources', 'pipes', and 'sinks'.
    instances = ClassLoader.instances_from_config(config)

    # Select the first available instance from each category.
    initial_sinks  = list(instances["sinks"].values())[0]
    initial_pipe   = list(instances["pipes"].values())[0]
    initial_source = list(instances["sources"].values())[0]
    logger.debug("Initialize Pipeline with: ", initial_source, initial_pipe, initial_sinks)

    # Create a queue to manage the flow of images.
    # Exchange the queue for own purposes (e.g. Hard Disk).
    queue  = Queue(maxsize=queue_size)
    logger.debug(f"Initialized Queue with size {queue_size}")

    # The pipeline handles how data is moved and processed between the source, processing operation, and sinks.
    pipeline = Pipeline(queue, instances, initial_source, initial_pipe, [initial_sinks])
    
    # Configure the pipeline further by using the configuration server.
    PipelineConfigurator(pipeline, config, host, port)

    logger.info("Start pipline")
    pipeline.run_forever() # doesn't return


# Entry point of the application.
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    default_config = "config.yml"

    if is_library_available("picamera2"):
        default_config = "pi_config.yml"

    parser.add_argument("-c", "--config", type=str, default=default_config, help="config file to load configuration")
    parser.add_argument("-p", "--port", type=int, default=8001, help="port of the config server")
    parser.add_argument("-q", "--queue_size", type=int, default=1, help="the size of the frame queue")
    parser.add_argument("-o", "--host", type=str, default="0.0.0.0", help="host of the config server")
    parser.add_argument('-v', '--verbose', action='store_true', help='make me talkative!')
    args = vars(parser.parse_args())

    if args["verbose"]:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Verbose mode on")

    main(args["config"], args["host"], args["port"], args["queue_size"])
