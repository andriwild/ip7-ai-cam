import argparse
import json
from kafka import KafkaConsumer

def main():
    parser = argparse.ArgumentParser(description="Console consumer for pipeline settings.")
    parser.add_argument("--bootstrap", default="localhost:29092", help="Kafka bootstrap server")
    parser.add_argument("--topic", default="pipeline-settings", help="Kafka topic for settings")
    parser.add_argument("--group-id", default="console-consumer-group")
    args = parser.parse_args()

    def deserializer(m):
        try:
            return json.loads(m.decode('utf-8'))
        except Exception as e:
            print(f"Error deserializing message: {m}")
            return {}

    consumer = KafkaConsumer(
        args.topic,
        bootstrap_servers=args.bootstrap,
        group_id=args.group_id,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        value_deserializer=deserializer
    )

    print(f"Listening on topic '{args.topic}'. Ctrl+C to exit.")
    try:
        for message in consumer:
            payload = message.value
            setting = payload.get("setting")
            value = payload.get("value")
            print(f"[consoleConsumer] Received setting '{setting}' = '{value}'")
    except KeyboardInterrupt:
        print("Exiting consumer.")

if __name__ == "__main__":
    main()
