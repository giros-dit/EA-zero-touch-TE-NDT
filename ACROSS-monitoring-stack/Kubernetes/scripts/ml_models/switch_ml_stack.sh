#!/bin/bash

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
cd $SCRIPT_DIR

# Valores por defecto
DEFAULT_ROUTER_TYPE="rA"
DEFAULT_MODEL_TYPE="linear"

# Mostrar ayuda
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "Uso: ./switch_ml_stack.sh <ml-model|dummy> [ROUTER_TYPE] [MODEL_TYPE]"
    echo "Ejemplo ML model: ./switch_ml_stack.sh ml-model rA linear"
    echo "Ejemplo Dummy: ./switch_ml_stack.sh dummy"
    exit 0
fi

# Comprobar parámetro principal
if [ -z "$1" ]; then
    echo "Error: Debes especificar el modo de despliegue: 'ml-model' o 'dummy'."
    exit 1
fi

MODE="$1"
ROUTERS=$(jq -r '.routers[] | keys[]' ../../config/config.json)

# Cambiar de dummy a ml-model
if [ "$MODE" == "ml-model" ]; then
    echo "Cambiando de ML Stack dummy a ML Stack ML models..."

    # Eliminar dummies existentes
    for router in $ROUTERS; do
        echo "Eliminando dummy para router $router..."
        kubectl delete -f "../../templates/ml/ml-${router}.yaml" 2>/dev/null
    done

    # Determinar router y modelo
    ROUTER_TYPE="${2:-$DEFAULT_ROUTER_TYPE}"
    MODEL_TYPE="${3:-$DEFAULT_MODEL_TYPE}"
    echo "Desplegando ML Stack con tipo de router: $ROUTER_TYPE, modelo: $MODEL_TYPE"

    # Llamar al script de despliegue ML
    ./launch_ml_stack.sh "$ROUTER_TYPE" "$MODEL_TYPE"

# Cambiar de ml-model a dummy
elif [ "$MODE" == "dummy" ]; then
    echo "Cambiando de ML  Stack ML models a ML Stack dummy..."

    # Eliminar ML models existentes
    for router in $ROUTERS; do
        echo "Eliminando ML model para router $router..."
        kubectl delete -f "../../templates/ml_models/ml_models_${router}.yaml" 2>/dev/null
        rm -f "../../templates/ml_models/ml_models_${router}.yaml"
    done

    # Desplegar dummies
    for router in $ROUTERS; do
        echo "Desplegando dummy para router $router..."
        kubectl apply -f "../../templates/ml/ml-${router}.yaml"
    done

else
    echo "Error: Modo desconocido '$MODE'. Usa 'ml-model' o 'dummy'."
    exit 1
fi
