from kafka import KafkaConsumer
import json
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser(description='Kafka Consumer')
parser.add_argument('-t', '--topic', type=str, required=True,
                   help='Kafka topic name')
parser.add_argument('-b', '--broker', type=str, required=True,
                   help='Kafka broker address and port')
args = parser.parse_args()

# Create Kafka consumer instance

consumer = KafkaConsumer(
    args.topic,
    bootstrap_servers=args.broker,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    #group_id='my_consumer_group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
)

# Continuously listen for messages
try:
    print("Starting consumer... Waiting for messages")
    for message in consumer:
        print(f"Received message: {message.value}")
        print(f"Partition: {message.partition}, Offset: {message.offset}")

except KeyboardInterrupt:
    print("Stopping consumer...")
    consumer.close()