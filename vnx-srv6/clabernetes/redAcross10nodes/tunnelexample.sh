#!/bin/bash
kubectl exec -n across-tc32 deploy/ru -- docker exec ru ip -6 route add fd00:0:2::2 encap seg6 mode encap segs fcff:3::1,fcff:2::1,fcff:1::1,fcff:11::1 dev eth1
kubectl exec -n across-tc32 deploy/ru -- docker exec ru ip -6 route add fd00:0:2::3 encap seg6 mode encap segs fcff:7::1,fcff:6::1,fcff:4::1,fcff:11::1 dev eth1
kubectl exec -n across-tc32 deploy/ru -- docker exec ru ip -6 route add fd00:0:3::2 encap seg6 mode encap segs fcff:7::1,fcff:6::1,fcff:5::1,fcff:2::1,fcff:12::1 dev eth1