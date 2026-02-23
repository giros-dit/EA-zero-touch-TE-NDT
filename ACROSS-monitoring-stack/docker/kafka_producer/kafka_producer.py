#!/usr/bin/env python
from kafka import KafkaProducer
import requests
import json
import time
import os
import sys
import time

 # Check if minimum expected argument is provided: kafka_broker
if len(sys.argv) < 2:
    print("Uso: python3 kafka_producer.py <kafka_broker>")
    sys.exit(1)

 # Store input argument kafka_broker
kafka_broker = sys.argv[1]

 # Load test metrics files for each router
def load_test_metrics(directory_path="test_metrics"):
    test_metrics = {}
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        with open(file_path, "r") as file:
            try:
                file_data = json.load(file)
                router_name = filename.split(".")[0]
                test_metrics[router_name] = file_data
                print(f"Cargado: {router_name} desde {filename}")
            except json.JSONDecodeError:
                print(f"Error: El archivo {file} no es un JSON válido.")
    return test_metrics

test_metrics_data = load_test_metrics()

 # Load configuration parameters from config.json file
def load_config(file_path="config.json"):
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Error: El archivo de configuración no se encontró.")
    except json.JSONDecodeError:
        print("Error: El archivo de configuración no es un JSON válido.")
    return {}

config = load_config()

 # Get configuration parameters
experiment_id = config.get("experiment_id")
flag_original_metrics = config.get("flag_original_metrics")
flag_debug_params = config.get("flag_debug_params")
max_throughput = config.get("max_throughput_mbps")
polling_interval = config.get("polling_interval")
multiplier = config.get("multiplier")
routers = {}
test_metrics_iterator = {}

 # Get routers configuration
for router in config.get("routers", []):
    for router_name, router_config in router.items():
        routers[router_name] = router_config

 # Get all routers collector URLs
node_exporter_collector_urls = [router["collector_url"] for router in routers.values()]

 # Router interfaces and collector URLs mapping
router_interfaces = {
    router["collector_url"]: router["interfaces"] for router in routers.values()
}

 # Get all routers Kafka topics
kafka_topics = [router["topic"] for router in routers.values()]

 # Network metrics of interest to filter
network_metrics = [
    "node_network_receive_bytes_total",
    "node_network_receive_packets_total"
]

 # Configure Kafka Producer to publish node exporter metrics in Kafka input topics
producer = KafkaProducer(
    bootstrap_servers = [kafka_broker],
    value_serializer = lambda v: json.dumps(v).encode('utf-8'),
    acks = 'all'
)

def scrape_metrics(node_exporter_collector_url):
    """Scrape metrics from node-exporter-collector endpoints."""
    try:
        response = requests.get(node_exporter_collector_url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error al realizar las peticiones a {node_exporter_collector_url}: {e}")
        return None

def filter_device(metric, interfaces):
    """Filter metrics based on network interfaces of interest."""
    filtered_devices = [
        value for value in metric.get('values', [])
        if any(label["name"] == "device" and label["value"] in interfaces 
            for label in value.get("labels", []))
    ]
    
    return{
        "name": metric["name"],
        "description": metric.get("description", ""),
        "type": metric.get("type", ""),
        "values": filtered_devices
    }

def filter_metrics(metrics, interfaces):
    """Filter metrics scraped from prometheus-node-exporter-collector."""
    if metrics:
        node_exporter = metrics.get('node_exporter')
        epoch_timestamp = metrics.get('epoch_timestamp')

         # Get router type and test metrics for the current router
        #router_type = next(
        #    (router["router_type"] for router in routers.values() if node_exporter.replace(":", "_") in router["collector_url"]))
        
        test_metrics = next(
            (router["test_metrics"] for router in routers.values() if node_exporter.replace(":", "_") in router["collector_url"]))

         # Filter metrics based on network metrics and interfaces of interest
        filtered_metrics = [
            filter_device(metric, interfaces) for metric in metrics.get('metrics', [])
            if metric['name'] in network_metrics
        ]

         # Create new JSON with target node-exporter, metrics timestamp, and filtered metrics
        return {
            'node_exporter': node_exporter,
            #'router_type': router_type,
            'epoch_timestamp': epoch_timestamp,
            'experiment_id': experiment_id,
            'interfaces': interfaces,
            'flag_debug_params': flag_debug_params,
            **({'debug_params': {
                'flag_original_metrics': flag_original_metrics,
                'max_throughput_mbps': max_throughput,
                'unit': 'bytes',
                'polling_interval': polling_interval,
                'test_metrics': test_metrics,
                'multiplier': multiplier,
                'metric_timestamp': epoch_timestamp,
                'collector_timestamp': f"{time.time()}"
            }} if flag_debug_params else {}),
            'metrics': filtered_metrics
        }
    else:
        return None

def test_metrics(router):
    """Generate test metrics for simulation purposes."""
    router_name = next((name for name, value in routers.items() if value["collector_url"] == router["collector_url"]))
    router_key = f"test_metrics_{router_name}"

     # Check if test metrics for the current router have been generated or get next period test metrics
    if router_name not in test_metrics_iterator:
        test_metrics_iterator[router_name] = 0
    else:
        test_metrics_iterator[router_name] += 1

    #print(f"Claves en test_metrics_data: {list(test_metrics_data.keys())}")

    periods = list(test_metrics_data[router_key].keys())

    if test_metrics_iterator[router_name] >= len(periods):
        test_metrics_iterator[router_name] = 0

    period = periods[test_metrics_iterator[router_name]]

    timestamp = f"{time.time()}"
    print(f"Timestamp: {timestamp}")

    return {
        'node_exporter': f"{router_name}:9100",
        #"router_type": router["router_type"],
        "epoch_timestamp": timestamp,
        "experiment_id": experiment_id,
        "interfaces": router_interfaces[router["collector_url"]],
        "flag_debug_params": flag_debug_params,
        **({"debug_params": {
            "flag_original_metrics": flag_original_metrics,
            "max_throughput_mbps": max_throughput,
            "unit": "bytes",
            "polling_interval": polling_interval,
            "test_metrics": router["test_metrics"],
            "multiplier": multiplier,
            "metric_timestamp": timestamp,
            "collector_timestamp": f"{time.time()}"
        }} if flag_debug_params else {}),
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
                        "value": test_metrics_data[router_key][period]["total_bytes"]
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
                        "value": test_metrics_data[router_key][period]["total_packets"]
                    }
                ]
            }
        ]
    }

def kafka_metrics(metrics, topic):
    """Publish scraped & filtered metrics into Kafka input topics."""
    try:
        producer.send(topic, metrics)
        producer.flush()
        #print("Métricas enviadas a Kafka con topic: {topic} correctamente")
    except Exception as e:
        print("Error al enviar las métricas a Kafka: {e}")
    
def main():
    """Main function that scrapes metrics from prometheus-node-exporter-collector and publishes them into Kafka input topics."""
    while True:
        #start_time = time.time()

        for i, router in enumerate(routers.values()):
             # Decide if metrics are scraped from node-exporter-collector or generated through test metrics
            if router["test_metrics"] == False:

                metrics = scrape_metrics(router["collector_url"])

                if metrics:

                    filtered_metrics = filter_metrics(metrics, router_interfaces[router["collector_url"]])

                    if filtered_metrics and filtered_metrics['metrics']:

                        kafka_metrics(filtered_metrics, kafka_topics[i])

            else:

                metrics = test_metrics(router)

                if metrics:

                    kafka_metrics(metrics, kafka_topics[i])

        #end_time = time.time()

        #print(f"Tiempo total de ejecución sin paralelización: {end_time - start_time} segundos.")
        
        time.sleep(polling_interval)

if __name__ == "__main__":
    main()
            
