from kafka import KafkaProducer
import json
import time
import random

# Configure the Kafka producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Topic name
TOPIC_NAME = 'test_topic'

def generate_example_data():
    return {
        "id": random.randint(1, 1000),
        "timestamp": time.time(),
        "message": f"Example message {random.randint(1, 100)}",
        "value": random.uniform(0, 100)
    }

def generate_example_data_with_format():
    current_timestamp = f"{time.time()}"
    return {
        "node_exporter": "r1-service:9100",
        "epoch_timestamp": current_timestamp,
        "experiment_id": "1",
        "debug_params": {
            "flag_original_metrics": "true",
            "max_throughput(Mbps)": 100,
            "interfaces": ["eth0", "lo"],
            "unit": "bytes",
            "polling_interval": 1
        },
        "metrics": [
            {
                "name": "node_network_receive_bytes_total",
                "description": "Network device statistic receive_bytes.",
                "type": "counter",
                "values": [
                    {
                        "labels": [
                            {
                                "name": "device",
                                "value": "eth0"
                            }
                        ],
                        "value": "42002"
                    },
                    {
                        "labels": [
                            {
                                "name": "device",
                                "value": "lo"
                            }
                        ],
                        "value": "0"
                        }
                ]
            },
            {
                "name": "node_network_receive_packets_total",
                "description": "Network device statistic receive_packets.",
                "type": "counter",
                "values": [
                    {
                        "labels": [
                            {
                                "name": "device",
                                "value": "eth0"
                            }
                        ],
                        "value": "495"
                    },
                    {
                        "labels": [
                            {
                                "name": "device",
                                "value": "lo"
                            }
                        ],
                        "value": "0"
                    }
                ]
            }
        ],
        "ml_metrics": [
            {
                "name": "node_network_receive_bytes_total_rate",
                "description": "Calculated rate metric for node_network_receive_bytes_total",
                "type": "rate",
                "value": random.uniform(500,700),
                "labels": {
                    "name": "device",
                    "value": ["eth0", "lo"]
                }
            },
            {
                "name": "node_network_receive_packets_total_rate",
                "description": "Calculated rate metric for node_network_receive_packets_total",
                "type": "rate",
                "value": random.uniform(0,10),
                "labels": {
                    "name": "device",
                    "value": ["eth0", "lo"]
                }
            },
            {
                "name": "node_network_average_received_packet_size",
                "description": "Average size of received packets",
                "type": "size",
                "value": random.uniform(0,100),
                "labels": {
                    "name": "device",
                    "value": ["eth0", "lo"]
                }
            },
            {
                "name": "node_network_router_capacity_occupation",
                "description": "Router capacity occupation",
                "type": "percentage",
                "value": random.uniform(0,0.96),
                "labels": {
                    "name": "device",
                    "value": ["eth0", "lo"]
                }
            }
        ]
    }
    

def main():
    try:
        while True:
            # Generate example data
            data = generate_example_data_with_format()
            
            # Send message to Kafka topic
            producer.send(TOPIC_NAME, data)
            print(f"Sent: {data}")
            
            # Wait random time between 1 and 5 seconds
            sleep_time = random.uniform(1, 5)
            #sleep_time = 5

            time.sleep(sleep_time)
            
    except KeyboardInterrupt:
        print("\nStopping producer...")
    finally:
        producer.close()

if __name__ == "__main__":
    main()