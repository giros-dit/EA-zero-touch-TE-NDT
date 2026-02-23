#!/bin/bash
kubectl exec deploy/rg -- docker exec rg ip -6 route add fd00:0:1::/64 encap seg6 mode encap segs fcff:13::1 dev eth1
kubectl exec deploy/rc -- docker exec rc ip -6 route add fd00:0:1::/64 encap seg6 mode encap segs fcff:13::1 dev eth1