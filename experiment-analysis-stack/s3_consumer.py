#! /usr/local/bin/python

from kafka import KafkaConsumer
import json
import boto3
from botocore.exceptions import ClientError
import argparse
import os

# Parse arguments from environment variables first

# Default values from environment variables
default_topics = os.environ.get('KAFKA_TOPICS', '').split(',')  # Comma-separated topics
default_broker = os.environ.get('KAFKA_BROKER')
default_endpoint = os.environ.get('S3_ENDPOINT')
default_access_key = os.environ.get('S3_ACCESS_KEY')
default_secret_key = os.environ.get('S3_SECRET_KEY')
default_bucket = os.environ.get('S3_BUCKET')
default_verbose = os.environ.get('VERBOSE', 'false').lower() == 'true'

# Parse command line arguments, overriding environment variables
parser = argparse.ArgumentParser(description='Kafka Consumer')
parser.add_argument('-t', '--topics', type=str, nargs='+', default=default_topics,
                   help=f'Kafka topic names (default: {default_topics})')
parser.add_argument('-k', '--broker', type=str, default=default_broker,
                   help=f'Kafka broker address and port (default: {default_broker})')
parser.add_argument('-e', '--endpoint', type=str, default=default_endpoint,
                   help=f'S3 endpoint URL (default: {default_endpoint})')
parser.add_argument('-a', '--access_key', type=str, default=default_access_key,
                    help='S3 access key')
parser.add_argument('-s', '--secret_key', type=str, default=default_secret_key,
                    help='S3 secret key')
parser.add_argument('-b', '--bucket', type=str, default=default_bucket,
                    help=f'S3 bucket name (default: {default_bucket})')
parser.add_argument('-v', '--verbose', action='store_true', default=default_verbose,
                    help='Enable verbose output')
args = parser.parse_args()

# Filter out empty topics (could happen if env var is empty)
topics = [topic for topic in args.topics if topic]

if not topics:
    print("Error: At least one topic must be specified")
    exit(1)

# Print arguments for the user to check
print('Running with the following parameters:')
print(f'  Topics: {topics}')
print(f'  Broker: {args.broker}')
print(f'  S3 Endpoint: {args.endpoint}')
print(f'  Access Key: {args.access_key[:4]}{"*" * (len(args.access_key) - 4) if args.access_key else ""}')
print(f'  Secret Key: {"*" * 8}')  # Hide secret key completely
print(f'  Bucket: {args.bucket}')
print(f'  Verbose: {args.verbose}')
print('-' * 50)

# Create Kafka consumer instance with multiple topics
consumer = KafkaConsumer(
    *topics,  # Unpack the list of topics
    bootstrap_servers=args.broker,
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    #group_id='my_consumer_group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
)

# Initialize S3 client for Minio
s3 = boto3.client(
        's3',
        endpoint_url=args.endpoint,
        aws_access_key_id=args.access_key,
        aws_secret_access_key=args.secret_key,
        region_name='local'
    )

bucket_name = args.bucket

# Ensure the bucket exists; create it if it doesn't
try:
    s3.head_bucket(Bucket=bucket_name)
except ClientError:
    s3.create_bucket(Bucket=bucket_name)

# Continuously listen for messages
try:
    print(f"Starting consumer... Listening for messages on topics: {topics}")
    for message in consumer:
        if (args.verbose):
            print(f"Received message from topic: {message.topic}")
            print(f"Partition: {message.partition}, Offset: {message.offset}")
            print(f"Message: {message.value}")

        # Write current message to Minio S3
        topic_folder = message.topic
        timestamp = message.value.get("epoch_timestamp")
        if timestamp:
            file_key = f"{topic_folder}/{timestamp}.json"
            s3.put_object(
                Bucket=bucket_name,
                Key=file_key,
                Body=json.dumps(message.value).encode("utf-8")
            )
            if (args.verbose):
                print(f"Message written to s3://{bucket_name}/{file_key}")
        else:
            print("Skipped S3 write: 'epoch_timestamp' field missing in message.")

except KeyboardInterrupt:
    print("Stopping consumer...")
    consumer.close()