__name__ = "B5G-ACROSS-TC32 -- Experiment data to CSV aggregator"
__version__ = "0.2.3"
__author__ = "David Martínez García <https://github.com/david-martinez-garcia>"
__credits__ = [
    "GIROS DIT-UPM <https://github.com/giros-dit>",
    "Luis Bellido Triana <https://github.com/lbellido>",
    "Pablo Fernández López <https://github.com/pablofl01>",
    "Mario Vicente Albertos <https://github.com/mariov22>",
    "Alejandro Villaseca Martínez <https://github.com/avillaseca01>",
    "Daniel González Sánchez <https://github.com/daniel-gonzalez-sanchez>",
    "Carlos Mariano Lentisco Sánchez <https://github.com/clentisco>"
]

## -- BEGIN IMPORT STATEMENTS -- ##

import boto3
import csv
from datetime import datetime
import json
import logging
import os
import re

## -- END IMPORT STATEMENTS -- ##

## -- BEGIN LOGGING CONFIGURATION -- ##

logger = logging.getLogger(__name__)
logging.basicConfig(
    format = '%(asctime)s %(levelname)-8s %(message)s',
    level = logging.DEBUG,
    datefmt = '%d-%m-%Y %H:%M:%S'
)

## -- END LOGGING CONFIGURATION -- ##

## -- BEGIN CONSTANTS DEFINITION -- ##

### --- S3 STORAGE CONFIGURATION --- ###

S3_ENDPOINT = os.environ.get("S3_ENDPOINT")
S3_ACCESS_KEY = os.environ.get("S3_ACCESS_KEY")
S3_SECRET_KEY = os.environ.get("S3_SECRET_KEY")

# Experiment data are saved in independent buckets.
# The name of the bucket will be the name/ID of the experiment.
S3_BUCKET = os.environ.get("S3_BUCKET")
S3_FLOWS_FILE_DATETIME_PREFIX = os.environ.get("S3_FLOWS_FILE_DATETIME_PREFIX")  # e.g., "flows_20251106"

### --- --- ###

### --- CSV HEADERS --- ###

POWER_CONSUMPTION_HEADERS = [
    "experiment_id",
    "router_id",
    "power_consumption_watts",
    "node_exporter_collector_timestamp",
    "kafka_producer_timestamp",
    "flink_aggregation_timestamp",
    "ml_timestamp",
    "telemetry_datetime"
]

EXPERIMENT_DURATION_HEADERS = [
    "experiment_begin_timestamp",
    "experiment_finish_timestamp"
]

### --- --- ###

## -- END CONSTANTS DEFINITION -- ##

## -- BEGIN MAIN CODE -- ##

logger.info("Script executed.")

logger.info("---")

# Initialize S3 client:
logger.info("Initializing S3 client...")
s3_client = boto3.client(
    "s3",
    endpoint_url = S3_ENDPOINT,
    aws_access_key_id = S3_ACCESS_KEY,
    aws_secret_access_key = S3_SECRET_KEY,
    region_name = "local" 
)
logger.info("Done.")

logger.info("---")

# Create output CSV file and write power consumption headers line:
logger.info("Creating output CSV file and writer object...")
csv_output_file = open(file = S3_BUCKET + ".csv", mode = "w", newline = "")
csv_writer = csv.writer(csv_output_file)
logger.info("Done.")

logger.info("---")

logger.info("Writing power consumption headers to CSV file...")
csv_writer.writerow(POWER_CONSUMPTION_HEADERS)
logger.info("Done.")

logger.info("---")

# Get JSON files from S3 storage. These files contain the desired router metrics and flows
# information that are to be aggregated in the output CSV file.
# Help: https://stackoverflow.com/questions/36205481/read-file-content-from-s3-bucket-with-boto3
try:
    # logger.info("Trying to retrieve JSON files from S3 storage...")
    logger.info("Building paginator and regex to retrieve JSON files from S3 storage...")
    # Metrics files are under folders named ML_rX, being "X" the number of the router.
    # The prefix specifies that keys must start with the string "ML_r".
    # If we want to filter to specific routers, we can use a regular expression.
    #pattern = re.compile(r'^ML_r\d+/')
    pattern = re.compile(r'^ML_r[a-zA-Z0-9]+/')
    # A paginator is used since the number of files to retrieve is very large.
    paginator = s3_client.get_paginator("list_objects_v2")
    
    logger.info("Done.")

    logger.info("---")

    keys = []
    for page in paginator.paginate(Bucket = S3_BUCKET, Prefix = "flows"):
        for object in page.get("Contents"):
            key = object.get("Key")
            if key.startswith("flows/" + S3_FLOWS_FILE_DATETIME_PREFIX):
                keys.append(key)
        
    
    first_flows_file = keys[0]
    last_flows_file = keys[-1]
    
    first_flows_file_regex = re.search(r'flows_(\d{8}_\d{6})\.json$', first_flows_file)
    if first_flows_file_regex:
        first_flows_file_match = first_flows_file_regex.group(1)
        first_flows_file_datetime = datetime.strptime(first_flows_file_match, "%Y%m%d_%H%M%S")

        logger.info("First flows file timestamp:" + first_flows_file_match)
        logger.info("First flows file datetime:" + str(first_flows_file_datetime))
    
    last_flows_file_regex = re.search(r'flows_(\d{8}_\d{6})\.json$', last_flows_file)
    if last_flows_file_regex:
        last_flows_file_match = last_flows_file_regex.group(1)
        last_flows_file_datetime = datetime.strptime(last_flows_file_match, "%Y%m%d_%H%M%S")

        logger.info("Last flows file timestamp:" + last_flows_file_match)
        logger.info("Last flows file datetime:" + str(last_flows_file_datetime))

    logger.info("Trying to retrieve metrics files...")
    logger.info("---")
    for page in paginator.paginate(Bucket = S3_BUCKET, Prefix = "ML_r"):
        for object in page.get("Contents"):
            key = object.get("Key")
            logger.info("File retrieved: " + key)
            file_regex = re.search(r'^ML_r[a-zA-Z0-9]+/([0-9]+\.[0-9]+)\.json$', key)
            if file_regex:
                unix_str = file_regex.group(1)
            file_datetime = datetime.fromtimestamp(float(unix_str))
            
            if first_flows_file_datetime < file_datetime < last_flows_file_datetime:
                logger.info(f"File {key} with datetime {file_datetime} is INSIDE the time window")
                if pattern.match(key):
                    logger.info("File key/name matches regular expression.")
                    logger.info("Trying to retrieve data from JSON file...")
                    data = s3_client.get_object(Bucket = S3_BUCKET, Key = key)
                    metrics_content = json.loads(data["Body"].read().decode("utf-8").strip())
                    logger.info("Done.")

                # For every retrieved JSON file, parse it to get metrics and write them to output CSV file.
                logger.info("Trying to parse JSON data and retrieve desired metrics...")
                experiment_id = metrics_content["experiment_id"]
                router_id = metrics_content["node_exporter"].split(":")[0]
                logger.info("Router id: " + router_id)
                node_exporter_collector_timestamp = metrics_content["debug_params"]["metric_timestamp"]
                kafka_producer_timestamp = metrics_content["debug_params"]["collector_timestamp"]
                flink_aggregation_timestamp = metrics_content["debug_params"]["process_timestamp"]
                ml_timestamp = metrics_content["debug_params"]["ml_timestamp"]
                metric_epoch_timestamp = metrics_content["epoch_timestamp"]
                telemetry_datetime = datetime.fromtimestamp(float(metric_epoch_timestamp)).strftime('%d-%m-%YT%H:%M:%S')
                for output_ml_metric in metrics_content["output_ml_metrics"]:
                    if output_ml_metric["name"] == "node_network_power_consumption_wats":
                        power_consumption_watts = output_ml_metric["value"][0]
                csv_metrics = [
                    experiment_id,
                    router_id,
                    power_consumption_watts,
                    node_exporter_collector_timestamp,
                    kafka_producer_timestamp,
                    flink_aggregation_timestamp,
                    ml_timestamp,
                    telemetry_datetime
                ]
                logger.info("Done.")

                logger.info("Trying to write metrics to output CSV file...")
                csv_writer.writerow(csv_metrics)
                logger.info("Done.")

                logger.info("---")
            else:
                logger.info(f"File {key} with datetime {file_datetime} is OUTSIDE the time window")

    logger.info("Done.")

    logger.info("---")

    # An empty line is written to output CSV file.
    csv_writer.writerow([])

    # Experiment duration headers are written to output CSV file.
    logger.info("Writing experiment duration headers to CSV file...")
    csv_writer.writerow(EXPERIMENT_DURATION_HEADERS)
    logger.info("Done.")

    logger.info("---")

    logger.info("Trying to retrieve flows files...")
    logger.info("---")
    flows_files_timestamps = []
    for page in paginator.paginate(Bucket = S3_BUCKET, Prefix = "flows"):
        for object in page.get("Contents"):
            key = object.get("Key")
            timestamp_iso = object.get("LastModified") # In ISO format.
            # Timestamp is converted to UNIX epoch format.
            timestamp_epoch = str(datetime.fromisoformat(str(timestamp_iso)).timestamp())
            logger.info("File retrieved: " + key)
            logger.info("File timestamp (ISO): " + str(timestamp_iso))
            logger.info("File timestamp (epoch): " + timestamp_epoch)
            logger.info("Saving flows file timestamp to temporary list...")
            flows_files_timestamps.append(timestamp_epoch)
            logger.info("Done.")

            logger.info("---")

    logger.info("Done.")

    logger.info("---")

    logger.info("Sorting flows timestamps to extract experiment duration...")
    # List is sorted in ascending order: from the lowest to the highest timestamp.
    flows_files_timestamps.sort()
    # flows_files_timestamps[0] should be the timestamp of the file "flows_initial.json", which is skipped.
    begin_timestamp = flows_files_timestamps[1]
    finish_timestamp = flows_files_timestamps[-1]
    experiment_duration = [begin_timestamp, finish_timestamp]
    logger.info("Done.")

    logger.info("---")

    logger.info("Writing experiment duration to output CSV file...")
    csv_writer.writerow(experiment_duration)
    logger.info("Done.")

    logger.info("---")

    # Finally, the output CSV file is closed:
    logger.info("Closing output CSV file...")
    csv_output_file.close()
    logger.info("Done.")
    
    logger.info("---")
except Exception as e:
    logger.exception(f"Exception while retrieving data from S3 storage: {e}")

logger.info("All done.")

## -- END MAIN CODE -- ##
