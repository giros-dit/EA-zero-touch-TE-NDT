#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

for ((i=1; i<=8; i++))
do
    kubectl apply -f ./templates/jobs/flink-job-submitter-r4.yaml
    kubectl wait --for=condition=complete --timeout=600s "job/flink-job-submitter-test-r4"
    kubectl delete job/flink-job-submitter-test-r4
done