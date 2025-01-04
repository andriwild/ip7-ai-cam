import argparse
import json
from kafka import KafkaProducer

def main():
    parser = argparse.ArgumentParser(description="REPL to set pipeline settings.")
    parser.add_argument("--bootstrap", default="localhost:29092", help="Kafka bootstrap server")
    parser.add_argument("--topic", default="pipeline-settings", help="Kafka topic for settings")
    args = parser.parse_args()

    producer = KafkaProducer(
        bootstrap_servers=args.bootstrap,
        value_serializer=lambda v: json.dumps(v).encode('utf-8')
    )

    print("Enter settings in the form <key>=<value>. E.g. 'source=Camera1'")
    print("Type 'q' to quit.")

    while True:
        user_input = input("> ").strip()
        if user_input.lower() == "q":
            print("Exiting REPL.")
            break

        # Parse input of form key=value
        if "=" in user_input:
            key, value = user_input.split("=", 1)
            key, value = key.strip(), value.strip()
            # Send to Kafka
            msg = {"setting": key, "value": value}
            producer.send(args.topic, msg)
            producer.flush()
            print(f"[consoleProducer] Sent: {msg}")
        else:
            print("Invalid input. Use 'key=value' or 'q' to quit.")

if __name__ == "__main__":
    main()
