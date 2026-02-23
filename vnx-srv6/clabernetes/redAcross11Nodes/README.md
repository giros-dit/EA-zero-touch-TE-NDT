# Clabernets ACROSS - 11 Nodes Topology
Clabernetes scenario with 11 nodes for studying and analyzing SRv6 (Segment Routing over IPv6 dataplane).


### Before launching the scenarios
 
Install:
- Containerlab
- kubectl
- docker
- kind

---

### Kind installation (avoid if not necessary)
To launch it, run the next commands:


```
kind create cluster --name c9s --config - <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
  - role: worker
  - role: worker
containerdConfigPatches:
- |-
  [plugins."io.containerd.grpc.v1.cri".containerd]
    discard_unpacked_layers = false
EOF
```

```
alias helm='docker run --network host -ti --rm -v $(pwd):/apps -w /apps \
    -v ~/.kube:/root/.kube -v ~/.helm:/root/.helm \
    -v ~/.config/helm:/root/.config/helm \
    -v ~/.cache/helm:/root/.cache/helm \
    alpine/helm:3.12.3'
```
```
helm upgrade --install --create-namespace --namespace c9s clabernetes oci://ghcr.io/srl-labs/clabernetes/clabernetes
```

```
kubectl apply -f https://kube-vip.io/manifests/rbac.yaml
kubectl apply -f https://raw.githubusercontent.com/kube-vip/kube-vip-cloud-provider/main/manifest/kube-vip-cloud-controller.yaml
kubectl create configmap --namespace kube-system kubevip --from-literal range-global=172.18.1.10-172.18.1.250
```

### Launch scenario

```bash
alias clabverter='sudo docker run --user $(id -u) \
    -v $(pwd):/clabernetes/work --rm \
    ghcr.io/giros-dit/clabernetes/clabverter'
```

```bash
kubectl apply -f ./converted
```

```bash
./converted/deployment-patcher.sh
```
When all pods with their containers inside are up, run:

```bash
./routespatch.sh
```

### Enlaces Router-Router (Red Principal)

| **Router A**    | **Interface A** | **Router B**    | **Interface B** | **Router A IPv6**        | **Router B IPv6**          |
|-----------------|-----------------|-----------------|-----------------|--------------------------|----------------------------|
| **r1**          | eth1            | **r2**          | eth1            | `fcf0:0:1:2::0/127`      | `fcf0:0:1:2::1/127`        |
| **r1**          | eth2            | **r3**          | eth1            | `fcf0:0:1:3::0/127`      | `fcf0:0:1:3::1/127`        |
| **r1**          | eth3            | **r4**          | eth1            | `fcf0:0:1:4::0/127`      | `fcf0:0:1:4::1/127`        |
| **r1**          | eth4            | **r7**          | eth1            | `fcf0:0:1:7::0/127`      | `fcf0:0:1:7::1/127`        |
| **r2**          | eth2            | **r3**          | eth2            | `fcf0:0:2:3::0/127`      | `fcf0:0:2:3::1/127`        |
| **r2**          | eth3            | **r6**          | eth1            | `fcf0:0:2:6::0/127`      | `fcf0:0:2:6::1/127`        |
| **r3**          | eth3            | **r9**          | eth1            | `fcf0:0:3:9::0/127`      | `fcf0:0:3:9::1/127`        |
| **r4**          | eth2            | **r5**          | eth1            | `fcf0:0:4:5::0/127`      | `fcf0:0:4:5::1/127`        |
| **r5**          | eth2            | **r6**          | eth2            | `fcf0:0:5:6::0/127`      | `fcf0:0:5:6::1/127`        |
| **r5**          | eth3            | **rg**          | eth2            | `fcf0:0:5:11::0/127`     | `fcf0:0:5:11::1/127`       |
| **r6**          | eth3            | **rg**          | eth3            | `fcf0:0:6:11::0/127`     | `fcf0:0:6:11::1/127`       |
| **r7**          | eth2            | **r8**          | eth1            | `fcf0:0:7:8::0/127`      | `fcf0:0:7:8::1/127`        |
| **r8**          | eth2            | **r9**          | eth2            | `fcf0:0:8:9::0/127`      | `fcf0:0:8:9::1/127`        |
| **r8**          | eth3            | **ru**          | eth2            | `fcf0:0:8:13::0/127`     | `fcf0:0:8:13::1/127`       |
| **r9**          | eth3            | **ru**          | eth3            | `fcf0:0:9:13::0/127`     | `fcf0:0:9:13::1/127`       |

### Router IDs (Loopback)

| **Router**      | **Router ID**            |
|-----------------|--------------------------|
| **r1**          | `fcff:1::1/32`           |
| **r2**          | `fcff:2::1/32`           |
| **r3**          | `fcff:3::1/32`           |
| **r4**          | `fcff:4::1/32`           |
| **r5**          | `fcff:5::1/32`           |
| **r6**          | `fcff:6::1/32`           |
| **r7**          | `fcff:7::1/32`           |
| **r8**          | `fcff:8::1/32`           |
| **r9**          | `fcff:9::1/32`           |
| **rg**          | `fcff:11::1/32`          |
| **ru**          | `fcff:13::1/32`          |
| **rgnb**        | `fcff:14::1/32`          |
| **rupf**        | `fcff:16::1/32`          |

### Enlaces Router-Gateway (Conexiones de Acceso)

| **Router**      | **Interface** | **Gateway**     | **Interface** | **Router IPv6**          | **Gateway IPv6**         |
|-----------------|---------------|-----------------|---------------|--------------------------|--------------------------|
| **rg**          | eth1          | **rgnb**        | eth1          | `fd00:0:5::0/127`        | `fd00:0:5::1/127`        |
| **ru**          | eth1          | **rupf**        | eth1          | `fd00:0:4::0/127`        | `fd00:0:4::1/127`        |

### Segmentos de Red de Usuarios

| **Segmento**    | **Gateway**     | **Interface** | **Red IPv6**             |
|-----------------|-----------------|---------------|--------------------------|
| **gNB Network** | **rgnb**        | eth2          | `fd00:0:2::/64`          |
| **UPF Network** | **rupf**        | eth2          | `fd00:0:1::/64`          |

### Conexión con IXIA-C

| **Gateway**     | **Interface** | **IXIA-C**      | **Interface** |
|-----------------|---------------|-----------------|---------------|
| **rgnb**        | eth2          | **ixia-c**      | eth2          |
| **rupf**        | eth2          | **ixia-c**      | eth1          |

---


### Linux commands for create tunnels

To create the tunnels use the script:

```bash
./tunnelexample.sh
```
