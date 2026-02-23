#!/bin/bash

./delete.sh
cd ..
docker build -f docker/Dockerfile -t avillaseca01/networkstack .
docker push avillaseca01/networkstack
cd ./k8s
