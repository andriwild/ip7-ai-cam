import argparse
import logging

from config.config import ConfigManager
from kafkaUtil.helper import start_settings_consumer_in_thread
from model.fps_queue import FpsQueue
from pipeline.pipeline import Pipeline
from pipeline.resultConsumer import ResultConsumer
from pipeline.frameproducer import FrameProducer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main(config_file: str)-> None:
    in_queue = FpsQueue(maxsize=10)
    out_queue = FpsQueue(maxsize=10)

    producer = FrameProducer(queue=in_queue)
    consumer = ResultConsumer(queue=out_queue)
    pipeline = Pipeline(in_queue, out_queue)

    settings = ConfigManager()

    start_settings_consumer_in_thread(settings)

    settings.attach(producer)
    settings.attach(pipeline)
    settings.attach(consumer)

    settings.load_config(config_file)

    producer.start()
    consumer.start()
    pipeline.start()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", type=str, default="config.yml", help="config file to load configuration")
    args = vars(parser.parse_args())
    main(args["config"])
