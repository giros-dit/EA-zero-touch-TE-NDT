#!/bin/bash
kubectl exec deploy/rg -- docker exec rg ip -6 route add fd00:0:1::/64 encap seg6 mode encap segs fcff:13::1 dev eth1
kubectl exec deploy/rg -- docker exec rg ip -6 route add fd00:0:4::0/127 encap seg6 mode encap segs fcff:13::1 dev eth1
kubectl exec deploy/rgnb -- docker exec rgnb ip -6 route add fd00:0:2::/64 via fd00:0:2::b1 dev eth2 metric 10
