from kafka import KafkaConsumer
from kafka import KafkaProducer
import json
import random
import sys
from sympy import sympify, symbols
import time
import csv
import os
 
 # Check if minimum expected arguments are provided: input_topic, output_topic
if len(sys.argv) < 3:
    print("Uso: python3 ml.py <input_topic> <output_topic>")
    sys.exit(1)
 
 # Store input arguments input_topic & output_topic
input_topic = sys.argv[1]
output_topic = sys.argv[2]
 
 # Read energy consumption formulas from configuration text file
def load_formulas(filepath):
    formulas = {}
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue  # saltar comentarios y líneas vacías
            if '=' in line:
                key, expr = line.split('=', 1)
                formulas[key.strip()] = expr.strip().strip('"').strip("'")
    return formulas
 
formulas = load_formulas("ml-config.txt")
 
 # Create Kafka consumer instance
consumer = KafkaConsumer(
    input_topic,
    bootstrap_servers='kafka-service:9092',
    #bootstrap_servers='INSIDE://kafka-service:9092',
    auto_offset_reset='latest',
    enable_auto_commit=True,
    #group_id='my_consumer_group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8')),
)
 
 # Configure the Kafka producer
producer = KafkaProducer(
    bootstrap_servers='kafka-service:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)
 
#csv_file = "latency-test.csv"
 
#def init_csv():
#    try:
#        with open(csv_file, 'x', newline='') as file:
#            fieldnames = ["epoch_timestamp", "collector_timestamp", "process_timestamp", "ml_timestamp"]
#            writer = csv.DictWriter(file, fieldnames=fieldnames)
#            writer.writeheader()
#    except FileExistsError:
#        pass
 
#init_csv()
 
# Define a function to apply a formula from text file
def calculate_energy_consumption(formulas, val_x, val_y):
    sym_x, sym_y = symbols('x y')
    formula = formulas['energy_consumption']
    parsed_formula = sympify(formula)
    result = parsed_formula.subs({sym_x: val_x, sym_y: val_y})
    print("result", result)
    return [float(result)]
 
def calculate_dz_dx(formulas, val_x, val_y):
    sym_x, sym_y = symbols('x y')
    formula = formulas['dz/dx']
    parsed_formula = sympify(formula)
    result = parsed_formula.subs({sym_x: val_x, sym_y: val_y})
    return [float(result)]
 
def calculate_dz_dy(formulas):
    formula = formulas['dz/dy']
    parsed_formula = sympify(formula)
    return float(parsed_formula)
 
def ml_generator(message):
    """Generate output JSON format from input ML metrics."""
 
    #epoch_timestamp = float(message["epoch_timestamp"])
    #collector_timestamp = float(message["debug_params"]["collector_timestamp"])
    #process_timestamp_ms = message["debug_params"]["process_timestamp"]
    #process_timestamp = float(process_timestamp_ms) / 1000
    #ml_timestamp_raw = f"{time.time()}"
    #ml_timestamp = float(ml_timestamp_raw)
 
    #with open(csv_file, 'a', newline='') as file:      
    #    fieldnames = ["epoch_timestamp", "collector_timestamp", "process_timestamp", "ml_timestamp"]
    #    writer = csv.DictWriter(file, fieldnames=fieldnames)
    #    writer.writerow({"epoch_timestamp": epoch_timestamp, "collector_timestamp": collector_timestamp, "process_timestamp": process_timestamp, "ml_timestamp": ml_timestamp})
 
    for metric in message["input_ml_metrics"]:
        print("metric", metric)
        if metric["name"] == "node_network_router_capacity_occupation":
            occupation = float(metric["value"])
            print("occupation: ", occupation)
        if metric["name"] == "node_network_average_received_packet_length":
            packet_length = metric["value"]
            print("packet_length: ", packet_length)
   
     # Simulate power consumption variation based on node occupation and router type
    #if (message["router_type"] == "A"):
    #    ml_pc_dbw = 0.2
    #    ml_pc_w = 700 + (occupation * ml_pc_dbw)
    #else:
    #    ml_pc_dbw = 0.5
    #    ml_pc_w = 500 + (occupation * ml_pc_dbw)
 
    #ml_pc_dpl = 0
 
    energy_consumption = calculate_energy_consumption(formulas, occupation, packet_length)
    print("energy_consumption: ", energy_consumption)
    dz_dx = calculate_dz_dx(formulas, occupation, packet_length)
    dz_dy = calculate_dz_dy(formulas)
 
    message["debug_params"]["ml_timestamp"] = f"{time.time()}"
 
    message["output_ml_metrics"] = [
        {
            "name": "node_network_power_consumption_wats",
            "type": "power_consumption_wats",
            "value": energy_consumption,
        },{
            "name": "node_network_power_consumption_variation_rate_occupation",
            "type": "power_consumption_variation_rate",
            "value": dz_dx,
        },{
            "name": "node_network_power_consumption_variation_rate_packet_length",
            "type": "power_consumption_variation_rate",
            "value": dz_dy,
        }
    ]
 
    return message
 
def main():
    """Main function that listens for messages in input Kafka topic and sends messages to output Kafka topic."""
    try:
         # Continuously listen for messages
        print("Starting consumer... Waiting for messages")
        for message in consumer:
            print(f"Received message: {message.value}")
            #print(f"Partition: {message.partition}, Offset: {message.offset}")
 
            ml_data = ml_generator(message.value)
           
             # Send message to Kafka topic
            producer.send(output_topic, ml_data)
            producer.flush()
            #print(f"Sent: {ml_data}")
 
    except KeyboardInterrupt:
        print("Stopping consumer...")
        consumer.close()
 
if __name__ == "__main__":
    main()
 