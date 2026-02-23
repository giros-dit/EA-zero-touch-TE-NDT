#!/bin/bash

# JSON config file
SCRIPT_DIR=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)
CONFIG_FILE="$SCRIPT_DIR/../../config/config.json"

# Router names from JSON config file
ROUTERS=$(jq -r '.routers[] | keys[]' $CONFIG_FILE)

KAFKA_POD=statefulset/kafka-broker
# Define for each router TD_rn, TP_rn & ML_rn
for ROUTER in $ROUTERS; do
    TD_TOPIC="TD_${ROUTER}"
    TP_TOPIC="TP_${ROUTER}"
    ML_TOPIC="ML_${ROUTER}"

    echo "Creating Kafka topics: $TD_TOPIC, $TP_TOPIC, $ML_TOPIC"

    for TOPIC in $TD_TOPIC $TP_TOPIC $ML_TOPIC; do
        kubectl exec -it "$KAFKA_POD" -- kafka-topics.sh --create --topic "$TOPIC" --bootstrap-server INSIDE://kafka-service:9092
    done

done

echo "✅ All Kafka topics correctly created."
