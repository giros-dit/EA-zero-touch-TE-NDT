#!/usr/bin/env bash
set -euo pipefail
 
if [ $# -ne 1 ]; then
    echo "Uso: $0 <nombre_del_pod>"
    exit 1
fi
 
POD="$1"
 
 
# 1. Listar interfaces eth* dentro del contenedor Docker
IFS=$'\n' read -r -d '' -a IFACES < <(
    kubectl exec deploy/"$POD" -- docker exec "$POD" ip -o link show \
    | awk -F': ' '/^.* eth[0-9]+/ {gsub(/@.*/, "", $2); print $2}' \
    && printf '\0'
)
 
if [ ${#IFACES[@]} -eq 0 ]; then
    echo "No se encontraron interfaces eth* en el contenedor $POD."
    exit 0
fi
 
# 2. Subir cada interfaz
for IF in "${IFACES[@]}"; do
    echo "Subiendo interfaz '$IF' en contenedor '$POD'..."
    kubectl exec deploy/"$POD" -- docker exec "$POD" ip link set "$IF" up
done