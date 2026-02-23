#!/bin/bash
kubectl exec deploy/ru -- docker exec ru sh -c 'echo "101 tunel1" >> /etc/iproute2/rt_tables'
kubectl exec deploy/ru -- docker exec ru sh -c 'echo "102 tunel2" >> /etc/iproute2/rt_tables'
kubectl exec deploy/ru -- docker exec ru sh -c 'echo "103 tunel3" >> /etc/iproute2/rt_tables'
kubectl exec deploy/ru -- docker exec ru ip -6 rule add to fd00:0:2::2 lookup tunel1
kubectl exec deploy/ru -- docker exec ru ip -6 rule add to fd00:0:2::3 lookup tunel2
kubectl exec deploy/ru -- docker exec ru ip -6 rule add to fd00:0:2::4 lookup tunel3
kubectl exec -n across-tc32 deploy/rg1 -- docker exec rg1 ip -6 route add fd00:0:1::1 encap seg6 mode encap segs fcff:5::1 dev eth1
