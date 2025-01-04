import json
import logging
import threading

from kafka import KafkaConsumer
from kafka import KafkaProducer

from model.config import ConfigManager

logger = logging.getLogger(__name__)


def run_settings_consumer(settings_manager: ConfigManager,
                          topic="pipeline-settings",
                          bootstrap_servers="localhost:29092",
                          group_id="pipeline-consumer-group"):

    def deserializer(m):
        try:
            return json.loads(m.decode('utf-8'))
        except Exception as e:
            logger.error(f"Error deserializing message: {m}")
            return m.decode('utf-8')

    consumer = KafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id=group_id,
        auto_offset_reset='latest',
        enable_auto_commit=True,
        value_deserializer=deserializer
    )

    for msg in consumer:
        payload = msg.value
        setting = payload.get("setting")
        value = payload.get("value")
        if setting:
            logger.info(f"[settings_consumer] Received setting '{setting}' = '{value}'")
            settings_manager.update_setting(setting, value)

def start_settings_consumer_in_thread(settings_manager: ConfigManager):
    thread = threading.Thread(
        target=run_settings_consumer, 
        args=(settings_manager,),
        daemon=True
    )
    thread.start()
    return thread


def get_kafka_producer(bootstrap_servers='localhost:29092'):
    return KafkaProducer(
        bootstrap_servers=bootstrap_servers,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )
