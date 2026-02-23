#!/bin/bash

docker run -p 8086:8086 \
  -v "/root/influxdb-data:/var/lib/influxdb2" \
  -v "/root/influxdb-config:/etc/influxdb2" \
  -e DOCKER_INFLUXDB_INIT_MODE=setup \
  -e DOCKER_INFLUXDB_INIT_USERNAME=$INFLUX_USER \
  -e DOCKER_INFLUXDB_INIT_PASSWORD=$INFLUX_PASS \
  -e DOCKER_INFLUXDB_INIT_ORG=$INFLUX_ORG \
  -e DOCKER_INFLUXDB_INIT_BUCKET=$INFLUX_BUCKET \
  influxdb:2.7
