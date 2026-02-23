__name__ = "Prometheus Node Exporter Collector"
__version__ = "1.0.1"
__author__ = "David Martínez García"
__credits__ = ["GIROS DIT-UPM", "Luis Bellido Triana", "Daniel González Sánchez", "David Martínez García"]

## -- BEGIN IMPORT STATEMENTS -- ##

from fastapi import FastAPI, HTTPException, Request, status
import logging
import requests
import time

## -- END IMPORT STATEMENTS -- ##

## -- BEGIN LOGGING CONFIGURATION -- ## 

logger = logging.getLogger(__name__)
logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S')

## -- END LOGGING CONFIGURATION -- ##

## -- BEGIN CONSTANTS DECLARATION -- ##

### Prometheus and OpenMetrics suffixes:
### https://prometheus.io/docs/instrumenting/exposition_formats/#text-based-format
### https://github.com/OpenObservability/OpenMetrics/blob/main/specification/OpenMetrics.md#suffixes
SUFFIXES = [
    "sum",
    "count",
    "bucket",
    "total",
    "created",
    "gcount",
    "gsum",
    "info"
]

## -- END CONSTANTS DECLARATION -- ##

## -- BEGIN DEFINITION OF AUXILIARY FUNCTIONS -- ##

def query_node_exporter_metrics(node_exporter_host: str, node_exporter_port: str) -> str:
    """
    It sends an HTTP GET request to retrieve metrics from the Node Exporter which endpoint
    is passed as parameter.
    A text-based format is returned:
    - https://prometheus.io/docs/instrumenting/exposition_formats/#text-based-format
    """
    
    logger.info("Sending HTTP GET request to retrieve metrics from Prometheus Node Exporter at "
                + node_exporter_host + ":" + node_exporter_port + "...")

    # Build HTTP GET request:
    response = requests.get(
        url="http://" + node_exporter_host + ":" + node_exporter_port + "/metrics",
        headers={
            "accept": "text/plain"
        }
    )
    # Evaluate response:
    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(status_code=response.status_code, detail=response.text)
    else:
        logger.info("Response is 200 OK - returning content...")
        return response.text

def parse_metrics(data: str, node_exporter_host: str, node_exporter_port: str) -> dict:
    """
    It parses the text-based format for the metrics and returns a JSON dictionary.
    The parsing is done line by line.
    """
    
    logger.info("Parsing metrics and generating JSON object...")

    dict = {}
    dict["node_exporter"] = node_exporter_host + ":" + node_exporter_port
    dict["epoch_timestamp"] = str(time.time())
    metrics = []
    metric = {}
    metric["name"] = ""
    metric["description"] = ""
    metric["type"] = ""
    metric["values"] = []

    suffixes_list = []
    suffixes_dict = {}

    first_metric = True

    for line in data.splitlines():
        line = line.strip()
        if line.startswith("# HELP"): # Description of the metric:
            if first_metric == False:
                # New metric found -- every metric starts with a HELP line.
                # Therefore, it can be considered as new metric indicator.
                # The prior metric dict is appended and emptied for the next metric.
                if len(suffixes_list) > 0:
                    suffixes_dict["suffixes"] = suffixes_list
                    metric["values"].append(suffixes_dict)
                metrics.append(metric)
                metric = {}
                metric["name"] = ""
                metric["description"] = ""
                metric["type"] = ""
                metric["values"] = []
                suffixes_list = []
                suffixes_dict = {}
            first_metric = False
            splitted_line = line.split(" ")
            # splitted_line[0] is the "#" character.
            # splitted_line[1] is the "HELP" keyword.
            # splitted_line[2] is the name of the metric.
            # splitted_line[3:] is the description of the metric (splitted word by word).
            metric["name"] = splitted_line[2]
            metric["description"] = " ".join(map(str, splitted_line[3:]))
        elif line.startswith("# TYPE"): # Data type of the metric:
            splitted_line = line.split(" ")
            # splitted_line[0] is the "#" character.
            # splitted_line[1] is the "TYPE" keyword.
            # splitted_line[2] is the name of the metric.
            # splitted_line[3] is the data type of the metric.
            metric["type"] = splitted_line[3]
        else: # Value of the metric:
            # The split function is applied from right to left (rsplit) because there may be labels with
            # values that contain whitespaces. Splitting the line this way ensures that those whitespaces
            # are correctly processed.
            splitted_line = line.rsplit(" ", maxsplit=1)
            # splitted_line[0] is the name of the metric (with labels between {} and suffixes after the "_" character)
            # splitted_line[1] is the value of the metric
            if "{" in splitted_line[0]: # Look for labels:
                ''' 
                Labels are enclosed in {} and represented as a comma-separated list of key-values (e.g., {key1="value1",key2="value2"})
                with a key-value occurence being a particular metric label.
                Note: For each label (i.e., one key-value occurrence), the label value could be a string with different words separated 
                by punctuation characters (e.g., {key1="value1.1,value1.2,value1.3"}).
                '''
                labels = "".join(splitted_line[0].split("{")[1].split("}")[0]).split('",')
                labels_list = []
                labels_dict = {}
                for label in labels:
                    label = label.replace("'", "").replace("\"", "").split("=")
                    # label[0] is the name of the label
                    # label[1] is the value of the label
                    label_dict = {}
                    label_dict["name"] = label[0]
                    label_dict["value"] = label[1]
                    labels_list.append(label_dict)
                labels_dict["labels"] = labels_list
                labels_dict["value"] = splitted_line[1]
                metric["values"].append(labels_dict)
            else: # Look for other values:
                if any(suffix in splitted_line[0] for suffix in SUFFIXES): # Look for suffixes:
                    suffix_dict = {}
                    suffix_dict["name"] = splitted_line[0].split("_")[-1]
                    suffix_dict["value"] = splitted_line[1]
                    suffixes_list.append(suffix_dict)
                else: # Look for standard values:
                    value = {}
                    value["value"] = splitted_line[1]
                    metric["values"].append(value)

    # Last metric is appended to the list:
    metrics.append(metric)

    dict["metrics"] = metrics

    logger.info("Done")

    return dict

## -- END DEFINITION OF AUXILIARY FUNCTIONS -- ##

## -- BEGIN MAIN CODE -- ##

app = FastAPI(
    title=__name__ + " - REST API",
    version=__version__
)

@app.get(path="/metrics/{node_exporter_host}_{node_exporter_port}.json")
async def get_metrics(request: Request, node_exporter_host: str, node_exporter_port: str) -> dict:
    """
    FastAPI request handler function: HTTP GET /metrics/{node_exporter_host}_{node_exporter_port}.json
    """

    logger.info("Received HTTP GET request from "
                + request.client.host + ":" + str(request.client.port)
                + " to /metrics/" + node_exporter_host + "_" + node_exporter_port + ".json")
    
    # Send an HTTP GET request to the Node Exporter:
    data = query_node_exporter_metrics(node_exporter_host, node_exporter_port)

    # Parse Node Exporter metrics and generate output JSON dictionary:
    metrics_json = parse_metrics(data, node_exporter_host, node_exporter_port)

    logger.info("Returning metrics in JSON format...")

    # Return output JSON dictionary:
    return metrics_json

## -- END MAIN CODE -- ##
