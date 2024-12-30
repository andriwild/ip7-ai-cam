from kafka import KafkaProducer, KafkaConsumer
from kafka.admin import KafkaAdminClient, NewTopic
import json
import threading
import time

# Konfiguration
BROKER = "localhost:9092"
TOPIC = "example-topic"

# Broker Setup
def setup_broker():
    admin_client = KafkaAdminClient(bootstrap_servers=BROKER)
    try:
        admin_client.create_topics([NewTopic(name=TOPIC, num_partitions=1, replication_factor=1)])
        print(f"Topic '{TOPIC}' created.")
    except Exception as e:
        print(f"Topic '{TOPIC}' already exists or error occurred: {e}")

# Producer
def producer():
    producer = KafkaProducer(
        bootstrap_servers=BROKER,
        value_serializer=lambda v: json.dumps(v).encode("utf-8")
    )
    for i in range(5):
        message = {"id": i, "value": f"Message {i}"}
        producer.send(TOPIC, message)
        print(f"Produced: {message}")
        time.sleep(1)  # Simuliere Verzögerung
    producer.close()

# Consumer
def consumer():
    consumer = KafkaConsumer(
        TOPIC,
        bootstrap_servers=BROKER,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")),
        group_id="example-group"
    )
    for message in consumer:
        print(f"Consumed: {message.value}")

# Main-Thread, um Producer und Consumer zu starten
if __name__ == "__main__":
    # Broker Setup
    setup_broker()
    
    # Threads für Producer und Consumer
    consumer_thread = threading.Thread(target=consumer, daemon=True)
    producer_thread = threading.Thread(target=producer, daemon=True)
    
    consumer_thread.start()
    producer_thread.start()

    producer_thread.join()
    consumer_thread.join()
