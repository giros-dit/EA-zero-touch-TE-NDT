#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

DEFAULT_ROUTER_TYPE="rA"
DEFAULT_MODEL_TYPE="linear"

if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "Uso: ./launch_ml_stack.sh [ROUTER_TYPE] [MODEL_TYPE]"
    echo "Ejemplo: ./launch_ml_stack.sh rA linear"
    exit 0
fi

if [ -n "$1" ]; then
    ROUTER_TYPE="$1"
else
    ROUTER_TYPE="$DEFAULT_ROUTER_TYPE"
fi

if [ -n "$2" ]; then
    MODEL_TYPE="$2"
else
    MODEL_TYPE="$DEFAULT_MODEL_TYPE"
fi

ROUTERS=$(jq -r '.routers[] | keys[]' ../../config/config.json)

for router in $ROUTERS; do
    echo "Generando deployment para router: $router con router_type: $ROUTER_TYPE y modelo: $MODEL_TYPE"
    ./launch_ml_model.sh "$router" "$ROUTER_TYPE" "$MODEL_TYPE"
done
