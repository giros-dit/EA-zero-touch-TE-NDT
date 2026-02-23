# Clabernets ACROSS
Claberntes scenarios for studying and analyzing SRv6 (Segment Routing over IPv6 dataplane).


### Before launching the scenarios
 
Install:
- Containerlab
- kubectl
- docker
- kind

---

### Kind installation (avoid if not necessary)
Too launch it, run the next commands:


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
When al pods with their container inside are up run

```bash
./routespatch.sh
```

### Enlaces Router-Router (Red Principal)

| **Router A**    | **Interface A** | **Router B**    | **Interface B** | **Router A IPv6**        | **Router B IPv6**          |
|-----------------|-----------------|-----------------|-----------------|--------------------------|----------------------------|
| **r1**          | eth1            | **rg**          | eth2            | `fcf0:0:1:11::0/127`     | `fcf0:0:1:11::1/127`       |
| **r1**          | eth2            | **r4**          | eth2            | `fcf0:0:1:4::0/127`      | `fcf0:0:1:4::1/127`        |
| **r1**          | eth3            | **r2**          | eth1            | `fcf0:0:1:2::0/127`      | `fcf0:0:1:2::1/127`        |
| **r2**          | eth2            | **r5**          | eth1            | `fcf0:0:2:5::0/127`      | `fcf0:0:2:5::1/127`        |
| **r2**          | eth3            | **r3**          | eth3            | `fcf0:0:2:3::0/127`      | `fcf0:0:2:3::1/127`        |
| **r2**          | eth4            | **rc**          | eth2            | `fcf0:0:2:12::0/127`     | `fcf0:0:2:12::1/127`       |
| **r3**          | eth1            | **ru**          | eth2            | `fcf0:0:3:13::0/127`     | `fcf0:0:3:13::1/127`       |
| **r3**          | eth2            | **r7**          | eth2            | `fcf0:0:3:7::0/127`      | `fcf0:0:3:7::1/127`        |
| **r3**          | eth4            | **rc**          | eth3            | `fcf0:0:3:12::0/127`     | `fcf0:0:3:12::1/127`       |
| **r4**          | eth1            | **rg**          | eth3            | `fcf0:0:4:11::0/127`     | `fcf0:0:4:11::1/127`       |
| **r4**          | eth3            | **r6**          | eth1            | `fcf0:0:4:6::0/127`      | `fcf0:0:4:6::1/127`        |
| **r5**          | eth2            | **r6**          | eth2            | `fcf0:0:5:6::0/127`      | `fcf0:0:5:6::1/127`        |
| **r6**          | eth3            | **r7**          | eth3            | `fcf0:0:6:7::0/127`      | `fcf0:0:6:7::1/127`        |
| **r7**          | eth1            | **ru**          | eth3            | `fcf0:0:7:13::0/127`     | `fcf0:0:7:13::1/127`       |

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
| **rg**          | `fcff:11::1/32`          |
| **rc**          | `fcff:12::1/32`          |
| **ru**          | `fcff:13::1/32`          |
| **rgnb**        | `fcff:14::1/32`          |
| **rcpd**        | `fcff:15::1/32`          |
| **rupf**        | `fcff:16::1/32`          |

### Enlaces Router-Gateway (Conexiones de Acceso)

| **Router**      | **Interface** | **Gateway**     | **Interface** | **Router IPv6**          | **Gateway IPv6**         |
|-----------------|---------------|-----------------|---------------|--------------------------|--------------------------|
| **rg**          | eth1          | **rgnb**        | eth2          | `fd00:0:5::0/127`        | `fd00:0:5::1/127`        |
| **rc**          | eth1          | **rcpd**        | eth2          | `fd00:0:6::0/127`        | `fd00:0:6::1/127`        |
| **ru**          | eth1          | **rupf**        | eth2          | `fd00:0:4::0/127`        | `fd00:0:4::1/127`        |

### Segmentos de Red de Usuarios

| **Segmento**    | **Gateway**     | **Interface** | **Red IPv6**             |
|-----------------|-----------------|---------------|--------------------------|
| **gNB Network** | **rgnb**        | eth1          | `fd00:0:2::/64`          |
| **CPD Network** | **rcpd**        | eth1          | `fd00:0:3::/64`          |
| **UPF Network** | **rupf**        | eth1          | `fd00:0:1::/64`          |

### Hosts Conectados

| **Host**        | **Red**         | **IPv6 Address**         | **Gateway**              |
|-----------------|-----------------|--------------------------|--------------------------|
| **hgnb-h1**     | gNB Network     | `fd00:0:2::2/64`         | `fd00:0:2::1`            |
| **hgnb-h2**     | gNB Network     | `fd00:0:2::3/64`         | `fd00:0:2::1`            |
| **hgnb-h3**     | gNB Network     | `fd00:0:2::4/64`         | `fd00:0:2::1`            |
| **hgnb-h4**     | gNB Network     | `fd00:0:2::5/64`         | `fd00:0:2::1`            |
| **hgnb-h5**     | gNB Network     | `fd00:0:2::6/64`         | `fd00:0:2::1`            |
| **hgnb-h6**     | gNB Network     | `fd00:0:2::7/64`         | `fd00:0:2::1`            |
| **hgnb-h7**     | gNB Network     | `fd00:0:2::8/64`         | `fd00:0:2::1`            |
| **hgnb-h8**     | gNB Network     | `fd00:0:2::9/64`         | `fd00:0:2::1`            |
| **hgnb-h9**     | gNB Network     | `fd00:0:2::a/64`         | `fd00:0:2::1`            |
| **hcpd-h1**     | CPD Network     | `fd00:0:3::2/64`         | `fd00:0:3::1`            |
| **hcpd-h2**     | CPD Network     | `fd00:0:3::3/64`         | `fd00:0:3::1`            |
| **hcpd-h3**     | CPD Network     | `fd00:0:3::4/64`         | `fd00:0:3::1`            |
| **hupf-h1**     | UPF Network     | `fd00:0:1::2/64`         | `fd00:0:1::1`            |

---


### Linux commands for create tunnels

to create the 2 tunnels use the script 

```bash
./tunnelexample.sh
```
