#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

# Definir valor por defecto para ML models
DEFAULT_ROUTER_TYPE="rA"
DEFAULT_MODEL_TYPE="linear"

if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "Uso: ./deploy.sh [ROUTER_TYPE] [MODEL_TYPE]"
    echo "Ejemplo: ./deploy.sh rA linear"
    exit 0
fi

# Comprobar si se han pasado argumentos para ML models
if [ -z "$1" ]; then
    echo "No se ha especificado ningún tipo de router. Se usará el valor por defecto: $DEFAULT_ROUTER_TYPE"
    ROUTER_TYPE="$DEFAULT_ROUTER_TYPE"
else
    ROUTER_TYPE="$1"
    echo "Tipo de router especificado: $ROUTER_TYPE"
fi

if [ -z "$2" ]; then
    echo "No se ha especificado ningún tipo de modelo. Se usará el valor por defecto: $DEFAULT_MODEL_TYPE"
    MODEL_TYPE="$DEFAULT_MODEL_TYPE"
else
    MODEL_TYPE="$2"
    echo "Modelo especificado: $MODEL_TYPE"
fi

# Create ConfigMap from the configuration file config.json
kubectl create configmap config-json --from-file=config/config.json

# Create ConfigMap for test metrics files
TEST_FILES=""
for file in $SCRIPT_DIR/config/test_metrics/*; do
    TEST_FILES+=" --from-file=$file"
done
kubectl create configmap test-metrics-configmap $TEST_FILES

kubectl create configmap ml-rA-config --from-file=config/ml-config/ml-rA-config.txt
kubectl create configmap ml-rB-config --from-file=config/ml-config/ml-rB-config.txt

# Create ConfigMap for ML models URLs
kubectl apply -f templates/ml_models/ml_models_configmap.yaml

# Create ConfigMap for ML inference script
kubectl create configmap ml-inference --from-file=docker/ml_models/ml_inference/inference.py

# Install Cert-Manager and FlinKubernetes/scripts/flink-test.shk Operator
#kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.8.1/cert-manager.yaml
#kubectl wait --for=condition=available --timeout=600s deployment/cert-manager -n cert-manager
#kubectl wait --for=condition=available --timeout=600s deployment/cert-manager-webhook -n cert-manager
#kubectl wait --for=condition=available --timeout=600s deployment/cert-manager-cainjector -n cert-manager

#kubectl apply -f https://github.com/spotify/flink-on-k8s-operator/releases/download/v0.5.1-alpha.3/flink-operator.yaml
#kubectl wait --for=condition=available --timeout=600s deployment/flink-operator-controller-manager -n flink-operator-system

# Deployments for NDT Data Fabric and Node Exporter Collector
kubectl apply -f ./templates/node-exporter-collector.yaml
kubectl apply -f ./templates/zookeeper.yaml
kubectl apply -f ./templates/kafka.yaml
kubectl wait --for=condition=ready pod -l service=kafka-broker --timeout=600s

# Create Kafka topics
chmod +x ./scripts/kafka_broker/create-topics-kafka.sh
./scripts/kafka_broker/create-topics-kafka.sh

# Deploy Apache Flink Operator Cluster
kubectl apply -f ./templates/flink-cluster.yaml
kubectl wait --for=condition=ready --timeout=600s pod/flink-job-cluster-jobmanager-0
kubectl wait --for=condition=ready --timeout=600s pod/flink-job-cluster-taskmanager-0
kubectl wait --for=condition=ready --timeout=600s pod/flink-job-cluster-taskmanager-1

# Deploy Machine Learning Models for each router
chmod +x ./scripts/ml_models/launch_ml_stack.sh
chmod +x ./scripts/ml_models/launch_ml_model.sh
./scripts/ml_models/launch_ml_stack.sh "$ROUTER_TYPE" "$MODEL_TYPE"

# Deploy Flink Job submitters and Machine Learning Dummies for each router
ROUTERS=$(jq -r '.routers[] | keys[]' config/config.json)
for router in $ROUTERS; do
    kubectl apply -f "./templates/jobs/flink-job-submitter-${router}.yaml"
    kubectl wait --for=condition=complete --timeout=600s "job/flink-job-submitter-test-${router}"
    kubectl wait --for=condition=ready --timeout=600s "deployment/ml-models-${router}"
done

# Deploy Kafka producer microservice in order to start the telemetry system
kubectl apply -f ./templates/kafka-producer.yaml