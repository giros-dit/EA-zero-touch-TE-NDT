#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

 # For every router delete ML Dummy, Flink Job Submitter and Router deployments
ROUTERS=$(jq -r '.routers[] | keys[]' config/config.json)
for router in $ROUTERS; do
    kubectl delete -f "./templates/ml_models/ml_models_${router}.yaml"
    rm "./templates/ml_models/ml_models_${router}.yaml"
    kubectl delete -f "./templates/ml/ml-${router}.yaml"
    kubectl delete job flink-job-submitter-test-${router}
done

 # Delete Kubernetes deployments for Apache Flink Operator Cluster
kubectl delete -f ./templates/flink-cluster.yaml

 # Delete Kubernetes deployments for Kafka Producer microservice
kubectl delete -f ./templates/kafka-producer.yaml

 # Delete Kubernetes deployment for Kafka Broker
kubectl delete -f ./templates/kafka.yaml

 # Delete Kubernetes deployment for Zookeeper Server
kubectl delete -f ./templates/zookeeper.yaml

 # Delete Kubernetes deployment for Node Exporter Collector
kubectl delete -f ./templates/node-exporter-collector.yaml

 # Delete static configuration configmap config-json
kubectl delete configmap config-json
kubectl delete configmap test-metrics-configmap
kubectl delete configmap ml-config
kubectl delete configmap ml-inference
kubectl delete configmap ml-models-configmap
kubectl delete configmap ml-rA-config
kubectl delete configmap ml-rB-config