kubectl exec -n c9s-srv6 -it $(kubectl get pods -n c9s-srv6 --no-headers | awk '/^r1-/ && $3=="Running" {print $1}') -- docker exec r1 ip -6 route add fd00:0:2::/127 encap seg6 mode encap segs fcff:2::1,fcff:3::1 dev eth3.111
kubectl exec -n c9s-srv6 -it $(kubectl get pods -n c9s-srv6 --no-headers | awk '/^r3-/ && $3=="Running" {print $1}') -- docker exec r3 ip -6 route add fd00:0:1::/127 encap seg6 mode encap segs fcff:2::1,fcff:1::1 dev eth3.111

kubectl exec -n c9s-srv6 -it $(kubectl get pods -n c9s-srv6 --no-headers | awk '/^r1-/ && $3=="Running" {print $1}') -- docker exec r1 ip -6 route add fd00:0:2::3/127 encap seg6 mode encap segs fcff:4::1,fcff:3::1 dev eth3.112
kubectl exec -n c9s-srv6 -it $(kubectl get pods -n c9s-srv6 --no-headers | awk '/^r3-/ && $3=="Running" {print $1}') -- docker exec r3 ip -6 route add fd00:0:1::3/127 encap seg6 mode encap segs fcff:4::1,fcff:1::1 dev eth3.112
