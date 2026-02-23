# B5Gemini ACROSS Experiment Stack

[![es](https://img.shields.io/badge/lang-es-blue)](./README.md)

This repository contains the requirements, instructions and scripts to execute experiments on the B5Gemini cluster.

## Table of Contents

1. [Scenario Description](#scenario-description)
    - [Architecture and software](#architecture-and-software)
    - [Network connections](#network-connections)
    - [Virtual scenario structure](#virtual-scenario-structure)

2. [Scenario deployment and experiment execution](#scenario-deployment-and-experiment-execution)
    - [*clabernetes* installation](#clabernetes-installation)
    - [Deployment modification for VlanNet connectivity](#deployment-modification-for-vlannet-connectivity)
    - [*Network emulation* deployment using containerlab topology in clabernetes](#network-emulation-deployment-using-containerlab-topology-in-clabernetes)
    - [*Monitoring stack* and Apache Kafka deployment](#monitoring-stack-and-apache-kafka-deployment)
    - [*ML Stack* deployment](#ml-stack-deployment)
    - [*Network control stack* deployment](#network-control-stack-deployment)
        - [NetworkInfo generator](#networkinfo-generator)
        - [Basic usage](#basic-usage)
        - [Customization for other topologies](#customization-for-other-topologies)
        - [Deployment on b5g](#deployment-on-b5g)
    - [*Experiment analysis stack* deployment](#experiment-analysis-stack-deployment)
        - [InfluxDB initial configuration](#influxdb-initial-configuration)
        - [MinIO initial configuration](#minio-initial-configuration)
        - [Complete deployment](#complete-deployment)
    - [Creation and execution of experiments using Ixia-c traffic generator](#creation-and-execution-of-experiments-using-ixia-c-traffic-generator)

## Scenario Description

For the purposes of the experiments contained in this repository, the B5Gemini cluster has one machine that acts as a controller and four others that act as compute nodes.

### Architecture and software

![B5Gemini Schema](./img/b5g.png)

> The cluster has an additional *compute4* node with the same configuration, but it is not shown in this diagram.

As indicated in the diagram, the [OpenStack](https://www.openstack.org/) virtualization platform and the [Kubernetes](https://kubernetes.io/es/) container orchestration platform are deployed on the cluster, on which the virtualized infrastructure for the experiments will run.

Additionally, the following components run on Kubernetes:

- [Calico CNI](https://github.com/projectcalico/calico)
- [Multus CNI](https://github.com/k8snetworkplumbingwg/multus-cni)
- [Ingress Nginx Controller](https://github.com/kubernetes/ingress-nginx)
- [MetalLB](https://metallb.io/)

### Network connections

![B5Gemini network schema](./img/b5g_net.png)
> The cluster has an additional *compute4* node with the same configuration, but it is not shown in this diagram.

Connectivity between nodes is established through a switch that handles traffic on various interfaces. The experiments contained here focus especially on the use of VLAN 30 network with virtual network bridges that allow establishing a second tagging for traffic segmentation.

### Virtual scenario structure

![Example complete virtual scenario for experiments](./img/scenario_lite_new.png)

The virtual scenario for experiments has various components that work together:

- **[Network emulation:](./vnx-srv6/)** Virtual [containerlab](https://containerlab.dev) network deployed using [clabernetes](https://containerlab.dev/manual/clabernetes/) on which to route traffic for experiments. Transport network routers report metrics to the *Monitoring stack* and establish their routes based on commands from the *Network control stack*. Connectivity between nodes is done using VLAN networks (over VlanNet) through *Multus* interfaces, which allows significantly reducing link latency.

- **[Monitoring stack:](./ACROSS-monitoring-stack/)** Collects and processes metrics from selected interfaces of transport network routers to make them available to the *ML Stack*.

- **ML stack:** Performs energy consumption calculation from metrics provided by the *Monitoring stack* for use in route creation by the *Network control stack*.

- **[Network control stack:](./vnx-srv6/NetworkControlStack/)** Performs route calculation based on data provided by the *ML stack*.

- **NDT Data Fabric:** Apache Kafka deployment where each component publishes processed data, using a *topic* per router and stage.

- **[Experiment analysis stack:](./experiment-analysis-stack/)** Consists of an [*InfluxDB*](https://www.influxdata.com/products/influxdb/) instance to store time series and visualize telemetry data in real time. Additionally, it has an instance of the [*MinIO*](https://min.io/) storage server where a replica of data is permanently stored in *S3*-compatible format. It is the only set of resources deployed on a "heavy" virtual machine in *OpenStack*.

## Scenario deployment and experiment execution

This section contains instructions for setting up the virtual scenario, assuming you already have a fully functional Kubernetes cluster with the necessary software described in the [Architecture and Software](#architecture-and-software) section.

### *clabernetes* installation

The [clabernetes quick start guide](https://containerlab.dev/manual/clabernetes/quickstart/) contains the necessary commands to install the tool in our Kubernetes cluster to handle the conversion of *Topology* objects that we deploy on it. Below is a summary of the commands needed for its setup:

```shell
alias helm='docker run --network host -ti --rm -v $(pwd):/apps -w /apps \
    -v ~/.kube:/root/.kube -v ~/.helm:/root/.helm \
    -v ~/.config/helm:/root/.config/helm \
    -v ~/.cache/helm:/root/.cache/helm \
    alpine/helm:3.12.3'
```

```shell
helm upgrade --install --create-namespace --namespace c9s \
    clabernetes oci://ghcr.io/srl-labs/clabernetes/clabernetes
```

### Deployment modification for VlanNet connectivity

To use the VlanNet network for communication between clabernetes nodes in our scenario, it is necessary to make available to the *pods* the *Multus* *NetworkAttachmentDefinition* objects that allow connection with interfaces of the Kubernetes *worker* node host.

An **example** of the command to define these objects is as follows:

```shell
NS=c9s-nodes3; cat <<EOF | kubectl create -f -
apiVersion: "k8s.cni.cncf.io/v1"
kind: NetworkAttachmentDefinition
metadata:
  name: net1000
  namespace: $NS
spec:
  config: '{
      "cniVersion": "0.3.0",
      "type": "macvlan",
      "master": "br-vlan.1000",
      "mode": "bridge",
      "ipam": {}
    }'
EOF
```

> If the name of this definition does not match the one established in the containerlab topology file **the pods will not start**.

### *Network emulation* deployment using containerlab topology in clabernetes

Deploying a containerlab topology in clabernetes is trivial using the `clabverter` tool. **This tool has been [modified](./clabernetes/clabverter/) for our scenario, so that the necessary patches are generated for using interfaces created through *Multus*.** To do this, simply indicate in the topology file a *link* element where one of the links is of *Multus* type `"multus:<interface name>"`.

> If the name of this interface does not match the one established in the definition of a *Multus* *NetworkAttachmentDefinition* object deployed in the *namespace* of our topology **the pods will not start**.

To be able to use clabverter directly from the command line without performing installations, we will run:

```shell
alias clabverter='sudo docker run --user $(id -u) \
    -v $(pwd):/clabernetes/work --rm \
    ghcr.io/giros-dit/clabernetes/clabverter'
```

> Since this is an image stored privately in the GitHub organization's container registry, authentication is necessary to access it. The procedure to generate an authentication token can be found [here](https://docs.github.com/es/packages/working-with-a-github-packages-registry/working-with-the-container-registry#autenticarse-en-el-container-registry).

To use clabverter, simply navigate to the directory where our topology is located and run:

```shell
clabverter --naming non-prefixed --outputDirectory ./converted
```

> Currently, this version of clabverter only works correctly if the `--naming non-prefixed` parameter is present.
> A complete list of options can be consulted by running `clabverter -h`.

This modified clabverter image will export the files:

- `_<topology name>-ns.yaml`: Creates the *namespace* where the topology will be deployed. Can be omitted if we work on an existing *namespace* that has been defined using the `--namespace` option of clabverter.

- `<topology name>.yaml`: File that deploys a *Topology* object on the indicated *namespace*. Clabernetes will automatically create the necessary resources (*deployments*, *services*...) to execute the topology.

- `deployment-patcher.sh`: Must be executed after deployment in the cluster to perform configuration of *Multus* interfaces.

- Additional files: Such as configuration files or licenses. These will be exported as Kubernetes [ConfigMaps](https://kubernetes.io/docs/concepts/configuration/configmap/) for use in the cluster.

> To be able to apply the patches, the [`yq`](https://mikefarah.gitbook.io/yq) tool is used through [its Docker image](https://hub.docker.com/r/mikefarah/yq). To avoid errors, it is recommended to run a `docker pull` with the tool's image before executing `deployment_patcher.sh`. The tests have been performed with version 4.44.5.

The experiments mainly use the topologies [redAcross6nodes](./vnx-srv6/clabernetes/redAcross6nodes/) and [redAcross10nodes](./vnx-srv6/clabernetes/redAcross10nodes/).

### *Monitoring stack* and Apache Kafka deployment

There are two deployment scripts for the telemetry system architecture that deploy:

- Apache Kafka broker
- Node Exporter Collector
- Kafka Producer microservice
- Flink Operator Cluster
- ML Stack

- [k8s-deploy-ml-models.sh](./ACROSS-monitoring-stack/Kubernetes/k8s-deploy-ml-models.sh):
Deploys **Monitoring Stack**, **NDT Data Fabric** and **Machine Learning Stack** with ML models.
- [k8s-deploy-ml-dummy.sh](./ACROSS-monitoring-stack/Kubernetes/k8s-deploy-ml-dummy.sh):
Deploys **Monitoring Stack**, **NDT Data Fabric** and **Machine Learning Stack** with ML dummy.

The execution of the [k8s-deploy-ml-models.sh](./ACROSS-monitoring-stack/Kubernetes/k8s-deploy-ml-models.sh) script requires two input parameters to define the router type and model type that the Machine Learning Stack will use.

```shell
./k8s-deploy.sh <router_type> <model_type>
```

- **<router_type>**: Router type to use, for example `rA`.
- **<model_type>**: Model type to use: `linear`, `MLP`, `polynomial`, `rf`.

Both router type <router_type>: `rA`, and model type <model_type>: `linear` are the default values used if no input parameters are specified.

The [k8s-deploy-ml-dummy.sh](./ACROSS-monitoring-stack/Kubernetes/k8s-deploy-ml-dummy.sh) script does not require any input parameters.

## Experiment

To define a new experiment to perform, it is necessary to configure the experiment definition parameters by editing the [config.json](./ACROSS-monitoring-stack/Kubernetes/config/config.json) file and restarting the Kafka Producer microservice responsible for reading these parameters:

- **Edit ConfigMap config-json**

 ```shell
kubectl edit configmap config-json
 ```

- **Restart Kafka Producer microservice**

 ```shell
kubectl rollout restart deployment kafka-producer
 ```

### *ML Stack* deployment

The *ML Stack* deployment is invoked from the general deployment script of the *Monitoring Stack* thanks to the input arguments <router_type> and <model_type> defined in [k8s-deploy.sh](./ACROSS-monitoring-stack/Kubernetes/k8s-deploy.sh). However, there is a complementary script [launch_ml_stack.sh](./ACROSS-monitoring-stack/Kubernetes/scripts/ml_models/launch_ml_stack.sh) that allows deploying the Machine Learning inference engine stack for all routers in the network scenario specified in the [config.json](./ACROSS-monitoring-stack/Kubernetes/config/config.json) configuration file.

```shell
./launch_ml_stack.sh <router_type> <model_type>
```

- **<router_type>**: Router type to use, for example `rA`.
- **<model_type>**: Model type to use: `linear`, `MLP`, `polynomial`, `rf`.

Both router type <router_type>: `rA`, and model type <model_type>: `linear` are the default values used if no input parameters are specified.

This script deploys as many ML models as routers in the network scenario, specified in the [config.json](./ACROSS-monitoring-stack/Kubernetes/config/config.json) configuration file, all with the same router type <router_type> and model type <model_type> specified as input arguments.

At the same time, there is a final script that allows deploying a single ML model for the router specified as input argument, so that over a stack of already deployed ML models, it allows changing the router type <router_type> or model type <model_type> for any of them, through the [launch_ml_model.sh](./ACROSS-monitoring-stack/Kubernetes/scripts/ml_models/launch_ml_model.sh) script.

```shell
./launch_ml_model.sh <router_id> <router_type> <model_type>
```

- **<router_id>**: Router ID to use, for example `r1`, `r2`, `r3`, `r4`, `r5`, `r6` or `r7`.
- **<router_type>**: Router type to use, for example `rA`.
- **<model_type>**: Model type to use: `linear`, `MLP`, `polynomial`, `rf`.

Both router type <router_type>: `rA`, and model type <model_type>: `linear` are the default values used if no input parameters are specified.

The three scripts [k8s-deploy.sh](./ACROSS-monitoring-stack/Kubernetes/k8s-deploy.sh), [launch_ml_stack.sh](./ACROSS-monitoring-stack/Kubernetes/scripts/ml_models/launch_ml_stack.sh) and [launch_ml_model.sh](./ACROSS-monitoring-stack/Kubernetes/scripts/ml_models/launch_ml_model.sh) use as default values the router type and model type `rA` and `linear`, respectively, if no input parameters are specified. In contrast, for the last script [launch_ml_model.sh](./ACROSS-monitoring-stack/Kubernetes/scripts/ml_models/launch_ml_model.sh) it is necessary to identify the router ID to use, for example: r1, r2, r3, r4, r5, r6 or r7.

To switch the ML Stack between ML models and dummy ML, you can use the [switch_ml_stack.sh](./ACROSS-monitoring-stack/Kubernetes/scripts/ml_models/switch_ml_stack.sh) script as follows:

```shell
./scripts/ml_models/switch_ml_stack.sh ml-model
```

This usage would switch from dummy ML Stack to ML models Stack with default values for router type (rA) and model type (linear).

```shell
./scripts/ml_models/switch_ml_stack.sh ml-model rA rf
```

This usage would switch from dummy ML Stack to ML models Stack with the specified router type and model type.

```shell
./scripts/ml_models/switch_ml_stack.sh dummy
```

This usage would switch from ML models Stack to dummy ML Stack.

### *Network control stack* deployment

First, you need to have a json file called networkinfo that describes the topology. To obtain this file, there is a program called `generate_networkfile.py`

#### NetworkInfo generator

Script that generates a JSON file with network information (connectivity graph and loopback addresses) from a Containerlab topology.

#### Basic usage

```bash
# Standard topology (nodes r1, r2... ru, rg, rc)
python3 networkinfo.py /path/to/topology.clab.yml

# Specify output file
python3 networkinfo.py /path/to/topology.clab.yml --output red.json
```

#### Customization for other topologies

If your nodes **do not start with "r"**, modify `--full_filter`:

```bash
# Nodes router1, router2...
python3 networkinfo.py /path/to/topology.clab.yml --full_filter "^(router.*)$"
```

If your border nodes **are not called ru/rg/rc**, modify `--final_filter`:

```bash
# Border: edge1, edge2, core
python3 networkinfo.py /path/to/topology.clab.yml --final_filter "^(edge\d+|core)$"
```

**Complete program documentation**
For more examples and detailed use cases, consult the [complete documentation](./vnx-srv6/blob/c72db89ff44b3050c68a8548313c43ff750f1b41/NetworkControlStack/readme_networkinfo.md).

#### Deployment on b5g

⚠️ Important: Once the networkinfo.json file is generated, you must copy it to the vnx-srv6 repository folder:

```bash
cp networkinfo.json /path/to/vnx-srv6/NetworkControlStack/k8s/
```

The Network Control Stack execution parameters can be configured in the networkstack.yaml file, which defines the Kubernetes deployment.

- ⚠️ `S3_BUCKET`: Modify the MinIO bucket value with the value associated with the experiment.
- `ENERGYAWARE`: if set to `"true"`, energy consumption inference is activated in route calculation.
- `DEBUG_COSTS`: if set to `"true"`, debug mode is enabled to see detailed information about route and cost calculation.

With the topology definition file, execute in the `k8s` folder

```bash
cd /path/to/vnx-srv6/NetworkControlStack/k8s/
./deploy.sh
```

To remove all containers and Network Control Stack resources, you can use the delete.sh script included in the same folder:

```bash
./delete.sh
```

### *Experiment analysis stack* deployment

The [*Experiment analysis stack*](./experiment-analysis-stack/) consists of a series of Docker containers that run the following services:

- [**InfluxDB:**](https://www.influxdata.com/products/influxdb/) Time series database and real-time graph visualization interface.

- [**Telegraf:**](https://github.com/influxdata/telegraf) Data collector for InfluxDB with various integrations (e.g. *Kafka*).

- [**MinIO:**](https://min.io/) Storage server compatible with [*Amazon S3*](https://aws.amazon.com/es/s3/) to make persistent copies of experiment data.

- [**S3 Consumer**](./experiment-analysis-stack/s3_consumer.py): *Python* script that acts as a *Kafka* consumer and saves captured messages to *MinIO* storage.

This *Docker Compose* deployment is the only component that needs to be deployed outside the cluster, on an OpenStack virtual machine. In our scenario, this machine has the following requirements:

- 4 vCPU
- 8GB RAM
- 40GB HDD
- 1 static IP address
- Ubuntu 22.04

Additionally, it is essential to have a [Docker](https://www.docker.com/) installation on this machine.

#### InfluxDB initial configuration

Prior to deploying the [docker-compose.yml](./experiment-analysis-stack/docker-compose.yml) file, it is necessary to initialize a temporary *InfluxDB* instance to establish the initial configuration and store it in a persistent directory:

```shell
docker run \
    -p 8086:8086
    -v "$PWD/influx-data:/var/lib/influxdb2" \
    -v "$PWD/influx-config:/etc/influxdb2" \
    -e DOCKER_INFLUXDB_INIT_MODE=setup \
    -e DOCKER_INFLUXDB_INIT_USERNAME=<USERNAME> \
    -e DOCKER_INFLUXDB_INIT_PASSWORD=<PASSWORD> \
    -e DOCKER_INFLUXDB_INIT_ORG=<ORG_NAME> \
    -e DOCKER_INFLUXDB_INIT_BUCKET=<BUCKET_NAME> \
    influxdb:2
```

> Complete information about using this image can be consulted on [*DockerHub*](https://hub.docker.com/_/influxdb).

Once started, it is necessary to access the web interface to create a new configuration for *telegraf*. After logging in, simply navigate to the "Sources" tab of the data loading option in the side menu.

![Influx home page](./img/influx_home.png)

On this new page, the "Kafka Consumer" plugin must be selected:

![Influx load source](./img/influx_load_source.png)

Then simply follow the steps indicated after clicking the "Use this plugin" button. The project configuration file for correctly capturing the fields of interest from the metrics can be consulted [here](./experiment-analysis-stack/telegraf.conf).

After clicking "Save and test", *InfluxDB* will return an access token and a configuration ID, necessary for *Telegraf* to load these settings:

![Influx save and test](./img/influx_save_and_test.png)

This instance can be deleted once the configuration is completed and stored, as it will persist in the directory mounted as a volume.

#### MinIO initial configuration

Prior to deploying the [docker-compose.yml](./experiment-analysis-stack/docker-compose.yml) file, it is necessary to initialize a temporary *MinIO* instance to establish the initial configuration and store it in a persistent directory:

```shell
docker run \
    -p 9001:9001
    -v "$PWD/minio-data:/data" \
    -e MINIO_ROOT_USER=<USERNAME>
    -e MINIO_ROOT_PASSWORD=<PASSWORD>\
    quay.io/minio/minio
```

Once the container is started, the *MinIO* interface will be available from `http://<ip_vm>:9001`. From it, it is possible to:

- Create a new data *bucket* to store experiment information. Available at `http://<ip_vm>:9001/buckets`.

- Create a new user with permissions to read and write to the *bucket*. Available at `http://<ip_vm>:9001/identity/users`.

- Create a new set of keys with permissions to read and write to the *bucket*. **This option is an alternative to creating a user** and allows greater permission granularity. Available at `http://<ip_vm>:9001/access-keys`.

This instance can be deleted once the configuration is completed and stored, as it will persist in the directory mounted as a volume.

#### Complete deployment

To perform the deployment using the [docker-compose.yml](./experiment-analysis-stack/docker-compose.yml) file, it is necessary to previously define a series of environment variables from the data of the other configured components:

```shell
KAFKA_BROKER=<kafka_broker_ip>:<kafka_broker_port>
KAFKA_TOPICS=<kafka_topics>

TELEGRAF_HOSTNAME=<telegraf_hostname>
INFLUX_URL=http://<influx_url>:<influx_port>
TELEGRAF_CONFIG_ID=<telegraf_config_id>
INFLUX_TOKEN=<influx_token>
INFLUX_ORG=<influx_org>
INFLUX_BUCKET=<influx_bucket>

MINIO_USER=<minio_user>
MINIO_PASS=<minio_pass>
S3_ENDPOINT=http://<s3_endpoint_ip>:<s3_endpoint_port>
S3_ACCESS_KEY=<s3_access_key>
S3_SECRET_KEY=<s3_secret_key>
S3_BUCKET=<s3_bucket>
```

> To facilitate the definition of these variables, it is recommended to add them to a small shell script.

After these definitions, simply start the containers:

```shell
docker compose up -d
```

### Creation and execution of experiments using Ixia-c traffic generator

In the [experiment-scripts](./experiment-scripts/) directory you will find the necessary files to launch experiments on the scenario.

For their correct operation, it is necessary to previamente install the dependencies defined in the [`requirements.txt`](./requirements.txt) file.

> The use of a Python virtual environment is recommended for installing dependencies and running experiments.

Experiments can be launched by executing the [`ixia_GUI.py`](./experiment-scripts/ixia_GUI.py) file as a Python script. From this file, configuration parameters are imported from one of the files in the [config](./experiment-scripts/config/) folder, which must be modified beforehand.

> Code sections where files are imported are marked by a series of `#` that allow their quick identification for modifications.

On the other hand, it is also necessary to import the flow definition function from one of the files within [flow_definitions](./experiment-scripts/flow_definitions/) and, optionally, a `variation_interval` function that defines an ordered sequence of flow startup and shutdown. Examples can be found in the files [fixed_packet_size_fixed_rate_mbps_continuous.py](./experiment-scripts/flow_definitions/fixed_packet_size_fixed_rate_mbps_continuous.py) and [fixed_packet_size_fixed_rate_mbps_interval.py](./experiment-scripts/flow_definitions/fixed_packet_size_fixed_rate_mbps_interval.py).

> The complete Ixia-c API documentation is available [here](https://redocly.github.io/redoc/?url=https://raw.githubusercontent.com/open-traffic-generator/models/v0.13.0/artifacts/openapi.yaml#tag/Configuration).

When running `ixia_GUI.py`, a graphical interface will be displayed with telemetry extracted from the flow generator and one or more buttons that allow starting or stopping flows.
