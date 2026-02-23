#!/bin/bash

# Namespace en Kubernetes
NS="across-tc32"

# Verificar si el namespace existe; si no, crearlo
if ! kubectl get namespace "$NS" &>/dev/null; then
  echo "Namespace $NS no existe. Creándolo..."
  kubectl create namespace "$NS"
fi

# Lista de VLANs
VLANS=(1001 1002 1003 1004 1005 1006 1007 1008 1009 1010 1011 1012 1013 1014 2001 2002 2003)

# Iterar sobre cada VLAN y crear la definición
for VLAN in "${VLANS[@]}"; do
  echo "Creando definición para VLAN ${VLAN} en el namespace ${NS}..."
  cat <<EOF | kubectl apply -f -
apiVersion: "k8s.cni.cncf.io/v1"
kind: NetworkAttachmentDefinition
metadata:
  name: net${VLAN}
  namespace: $NS
spec:
  config: '{
      "cniVersion": "0.3.0",
      "type": "macvlan",
      "master": "br-vlan.${VLAN}",
      "mode": "bridge",
      "ipam": {}
    }'
EOF
done
