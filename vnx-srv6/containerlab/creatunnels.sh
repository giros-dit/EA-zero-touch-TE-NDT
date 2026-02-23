sudo docker exec clab-srv6-r1 ip -6 route add fd00:0:2::/127 encap seg6 mode encap segs fcff:2::1,fcff:3::1 dev eth3.111
sudo docker exec clab-srv6-r1 ip -6 route add fd00:0:2::3/127 encap seg6 mode encap segs fcff:4::1,fcff:3::1 dev eth3.112

sudo docker exec clab-srv6-r3 ip -6 route add fd00:0:1::/127 encap seg6 mode encap segs fcff:2::1,fcff:1::1 dev eth3.111
sudo docker exec clab-srv6-r3 ip -6 route add fd00:0:1::3/127 encap seg6 mode encap segs fcff:4::1,fcff:1::1 dev eth3.112