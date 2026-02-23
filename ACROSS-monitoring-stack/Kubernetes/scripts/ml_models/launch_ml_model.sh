#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

DEFAULT_ROUTER_TYPE="rA"
DEFAULT_MODEL_TYPE="linear"

if [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "Uso: ./launch_ml_model.sh [ROUTER_ID] [ROUTER_TYPE] [MODEL_TYPE]"
    echo "Ejemplo: ./launch_ml_model.sh r1 rA linear"
    exit 0
fi

ROUTER_ID=$1

if [ -z "$ROUTER_ID" ]; then
  echo "Uso: $0 <router_id> <router_type> <model_type>"
  echo "Ejemplo: ./launch_ml_model.sh r1 rA linear"
  exit 1
fi

if [ -n "$2" ]; then
    ROUTER_TYPE="$2"
else
    ROUTER_TYPE="$DEFAULT_ROUTER_TYPE"
fi

if [ -n "$3" ]; then
    MODEL_TYPE="$3"
else
    MODEL_TYPE="$DEFAULT_MODEL_TYPE"
fi

TEMPLATE_FILE="../../templates/ml_models/ml_models_template.yaml"
DEPLOYMENT_FILE="../../templates/ml_models/ml_models_${ROUTER_ID}.yaml"

if [ ! -f "$TEMPLATE_FILE" ]; then
  echo "Error: No se encuentra el archivo $TEMPLATE_FILE"
  exit 1
fi

# Copiamos el archivo de template a un archivo de deployment
cp "$TEMPLATE_FILE" "$DEPLOYMENT_FILE"

# Actualizamos las variables en el YAML
sed -i "s/{{ROUTER_ID}}/$ROUTER_ID/g" "$DEPLOYMENT_FILE"

sed -i "s/{{ROUTER_TYPE}}/$ROUTER_TYPE/g" "$DEPLOYMENT_FILE"

sed -i "s/{{MODEL_TYPE}}/$MODEL_TYPE/g" "$DEPLOYMENT_FILE"

# Aplicamos el deployment actualizado
kubectl apply -f "$DEPLOYMENT_FILE"

echo "Actualizado $DEPLOYMENT_FILE con ROUTER_TYPE=$ROUTER_TYPE, MODEL_TYPE=$MODEL_TYPE y aplicado con kubectl apply"
