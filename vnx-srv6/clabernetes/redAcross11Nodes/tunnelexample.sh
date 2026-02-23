#!/bin/bash
#kubectl exec -n across-tc32 deploy/ru -- docker exec ru ip -6 route add fd00:0:2::1 encap seg6 mode encap segs fcff:9::1,fcff:3::1,fcff:2::1,fcff:6::1,fcff:11::1 dev eth3

kubectl exec -n across-tc32 deploy/ru -- docker exec ru ip -6 route add fd00:0:2::b2 encap seg6 mode encap segs fcff:9::1,fcff:3::1,fcff:2::1,fcff:6::1,fcff:11::1 dev eth3
kubectl exec -n across-tc32 deploy/ru -- docker exec ru ip -6 route add fd00:0:2::b3 encap seg6 mode encap segs fcff:9::1,fcff:3::1,fcff:2::1,fcff:6::1,fcff:11::1 dev eth3
