#!/bin/bash
kubectl exec deploy/rgnb -- docker exec rgnb ip -6 neigh replace fd00:0:1::b1 dev eth2 lladdr 02:00:00:00:01:ff nud permanent