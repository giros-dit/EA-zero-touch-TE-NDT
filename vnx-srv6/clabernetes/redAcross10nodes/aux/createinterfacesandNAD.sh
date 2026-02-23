#!/bin/bash

# Verificar que al menos se pasen dos parámetros
if [ "$#" -lt 2 ]; then
  echo "Uso: $0 <namespace> <vlan1> [<vlan2> ... <vlanN>]"
  exit 1
fi

# Namespace en Kubernetes
NS="$1"
shift

# Lista de VLANs
VLANS=("$@")

# Crear definiciones de NetworkAttachment en Kubernetes
for VLAN in "${VLANS[@]}"; do
  cat <<EOF | kubectl create -f -
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

# Configurar Open vSwitch y VLANs en los servidores
for i in {1..3}; do
  ssh root@compute${i} "
    apt install -y openvswitch-switch
    ovs-vsctl add-br br-vlan
    ovs-vsctl add-port br-vlan vlannet
    ip link set br-vlan up
  "
  for VLAN in "${VLANS[@]}"; do
    ssh root@compute${i} "
      ip link add link br-vlan name br-vlan.${VLAN} type vlan id ${VLAN}
      ip link set br-vlan.${VLAN} up
    "
  done
done