sudo docker exec clab-srv6-r1 service frr start
sudo docker exec clab-srv6-r2 service frr start
sudo docker exec clab-srv6-r3 service frr start
sudo docker exec clab-srv6-r4 service frr start
sudo docker exec clab-srv6-r5 service frr start
sudo docker exec clab-srv6-r6 service frr start
sudo docker exec clab-srv6-r7 service frr start
sudo docker exec clab-srv6-r11 service frr start
sudo docker exec clab-srv6-r12 service frr start
sudo docker exec clab-srv6-r13 service frr start

#gNB1
sudo docker exec clab-srv6-gNB1 ip link add link eth1 name eth1.111 type vlan id 111
sudo docker exec clab-srv6-gNB1 ip link add link eth1 name eth1.112 type vlan id 112
sudo docker exec clab-srv6-gNB1 ip link add link eth1 name eth1.113 type vlan id 113
sudo docker exec clab-srv6-gNB1 ip -6 addr add fd00:0:2::1/127 dev eth1.111
sudo docker exec clab-srv6-gNB1 ip -6 addr add fd00:0:2::3/127 dev eth1.112
sudo docker exec clab-srv6-gNB1 ip -6 addr add fd00:0:2::5/127 dev eth1.113
sudo docker exec clab-srv6-gNB1 ip link set eth1.111 up
sudo docker exec clab-srv6-gNB1 ip link set eth1.112 up
sudo docker exec clab-srv6-gNB1 ip link set eth1.113 up
sudo docker exec clab-srv6-gNB1 ip -6 route add fd00:0:1::1/127 via fd00:0:2::
sudo docker exec clab-srv6-gNB1 ip -6 route add fd00:0:1::3/127 via fd00:0:2::2
sudo docker exec clab-srv6-gNB1 ip -6 route add fd00:0:1::5/127 via fd00:0:2::4

#gNB2
sudo docker exec clab-srv6-gNB2 ip link add link eth1 name eth1.121 type vlan id 121
sudo docker exec clab-srv6-gNB2 ip link add link eth1 name eth1.122 type vlan id 122
sudo docker exec clab-srv6-gNB2 ip link add link eth1 name eth1.123 type vlan id 123
sudo docker exec clab-srv6-gNB2 ip -6 addr add fd00:0:3::1/127 dev eth1.121
sudo docker exec clab-srv6-gNB2 ip -6 addr add fd00:0:3::3/127 dev eth1.122
sudo docker exec clab-srv6-gNB2 ip -6 addr add fd00:0:3::5/127 dev eth1.123
sudo docker exec clab-srv6-gNB2 ip link set eth1.121 up
sudo docker exec clab-srv6-gNB2 ip link set eth1.122 up
sudo docker exec clab-srv6-gNB2 ip link set eth1.123 up
sudo docker exec clab-srv6-gNB2 ip -6 route add fd00:0:1::7/127 via fd00:0:3::
sudo docker exec clab-srv6-gNB2 ip -6 route add fd00:0:1::9/127 via fd00:0:3::2
sudo docker exec clab-srv6-gNB2 ip -6 route add fd00:0:1::b/127 via fd00:0:3::4

#UPF
sudo docker exec clab-srv6-UPF ip link add link eth1 name eth1.111 type vlan id 111
sudo docker exec clab-srv6-UPF ip link add link eth1 name eth1.112 type vlan id 112
sudo docker exec clab-srv6-UPF ip link add link eth1 name eth1.113 type vlan id 113
sudo docker exec clab-srv6-UPF ip link add link eth1 name eth1.121 type vlan id 121
sudo docker exec clab-srv6-UPF ip link add link eth1 name eth1.122 type vlan id 122
sudo docker exec clab-srv6-UPF ip link add link eth1 name eth1.123 type vlan id 123
sudo docker exec clab-srv6-UPF ip -6 addr add fd00:0:1::1/127 dev eth1.111
sudo docker exec clab-srv6-UPF ip -6 addr add fd00:0:1::3/127 dev eth1.112
sudo docker exec clab-srv6-UPF ip -6 addr add fd00:0:1::5/127 dev eth1.113
sudo docker exec clab-srv6-UPF ip -6 addr add fd00:0:1::7/127 dev eth1.121
sudo docker exec clab-srv6-UPF ip -6 addr add fd00:0:1::9/127 dev eth1.122
sudo docker exec clab-srv6-UPF ip -6 addr add fd00:0:1::b/127 dev eth1.123
sudo docker exec clab-srv6-UPF ip link set eth1.111 up
sudo docker exec clab-srv6-UPF ip link set eth1.112 up
sudo docker exec clab-srv6-UPF ip link set eth1.113 up
sudo docker exec clab-srv6-UPF ip link set eth1.121 up
sudo docker exec clab-srv6-UPF ip link set eth1.122 up
sudo docker exec clab-srv6-UPF ip link set eth1.123 up
sudo docker exec clab-srv6-UPF ip -6 route add fd00:0:2::1/127 via fd00:0:1::
sudo docker exec clab-srv6-UPF ip -6 route add fd00:0:2::3/127 via fd00:0:1::2
sudo docker exec clab-srv6-UPF ip -6 route add fd00:0:2::5/127 via fd00:0:1::4
sudo docker exec clab-srv6-UPF ip -6 route add fd00:0:3::1/127 via fd00:0:1::6
sudo docker exec clab-srv6-UPF ip -6 route add fd00:0:3::3/127 via fd00:0:1::8
sudo docker exec clab-srv6-UPF ip -6 route add fd00:0:3::5/127 via fd00:0:1::a

#r1
sudo docker exec clab-srv6-r1 sysctl -p
sudo docker exec clab-srv6-r1 vtysh -c 'configure terminal' -f /etc/frr/zebra.conf
sudo docker exec clab-srv6-r1 vtysh -c 'configure terminal' -f /etc/frr/isisd.conf
sudo docker exec clab-srv6-r1 sysctl -w net.ipv6.conf.eth1.seg6_enabled=1
sudo docker exec clab-srv6-r1 sysctl -w net.ipv6.conf.eth2.seg6_enabled=1
sudo docker exec clab-srv6-r1 sysctl -w net.ipv6.conf.eth3.seg6_enabled=1

#r2
sudo docker exec clab-srv6-r2 sysctl -p
sudo docker exec clab-srv6-r2 vtysh -c 'configure terminal' -f /etc/frr/zebra.conf
sudo docker exec clab-srv6-r2 vtysh -c 'configure terminal' -f /etc/frr/isisd.conf
sudo docker exec clab-srv6-r2 sysctl -w net.ipv6.conf.eth1.seg6_enabled=1
sudo docker exec clab-srv6-r2 sysctl -w net.ipv6.conf.eth2.seg6_enabled=1
sudo docker exec clab-srv6-r2 sysctl -w net.ipv6.conf.eth3.seg6_enabled=1
sudo docker exec clab-srv6-r2 sysctl -w net.ipv6.conf.eth4.seg6_enabled=1

#r3
sudo docker exec clab-srv6-r3 sysctl -p
sudo docker exec clab-srv6-r3 vtysh -c 'configure terminal' -f /etc/frr/zebra.conf
sudo docker exec clab-srv6-r3 vtysh -c 'configure terminal' -f /etc/frr/isisd.conf
sudo docker exec clab-srv6-r3 sysctl -w net.ipv6.conf.eth1.seg6_enabled=1
sudo docker exec clab-srv6-r3 sysctl -w net.ipv6.conf.eth2.seg6_enabled=1
sudo docker exec clab-srv6-r3 sysctl -w net.ipv6.conf.eth3.seg6_enabled=1
sudo docker exec clab-srv6-r3 sysctl -w net.ipv6.conf.eth4.seg6_enabled=1

#r4
sudo docker exec clab-srv6-r4 sysctl -p
sudo docker exec clab-srv6-r4 vtysh -c 'configure terminal' -f /etc/frr/zebra.conf
sudo docker exec clab-srv6-r4 vtysh -c 'configure terminal' -f /etc/frr/isisd.conf
sudo docker exec clab-srv6-r4 sysctl -w net.ipv6.conf.eth1.seg6_enabled=1
sudo docker exec clab-srv6-r4 sysctl -w net.ipv6.conf.eth2.seg6_enabled=1
sudo docker exec clab-srv6-r4 sysctl -w net.ipv6.conf.eth3.seg6_enabled=1

#r5
sudo docker exec clab-srv6-r5 sysctl -p
sudo docker exec clab-srv6-r5 vtysh -c 'configure terminal' -f /etc/frr/zebra.conf
sudo docker exec clab-srv6-r5 vtysh -c 'configure terminal' -f /etc/frr/isisd.conf
sudo docker exec clab-srv6-r5 sysctl -w net.ipv6.conf.eth1.seg6_enabled=1
sudo docker exec clab-srv6-r5 sysctl -w net.ipv6.conf.eth2.seg6_enabled=1

#r6
sudo docker exec clab-srv6-r6 sysctl -p
sudo docker exec clab-srv6-r6 vtysh -c 'configure terminal' -f /etc/frr/zebra.conf
sudo docker exec clab-srv6-r6 vtysh -c 'configure terminal' -f /etc/frr/isisd.conf
sudo docker exec clab-srv6-r6 sysctl -w net.ipv6.conf.eth1.seg6_enabled=1
sudo docker exec clab-srv6-r6 sysctl -w net.ipv6.conf.eth2.seg6_enabled=1
sudo docker exec clab-srv6-r6 sysctl -w net.ipv6.conf.eth3.seg6_enabled=1

#r7
sudo docker exec clab-srv6-r7 sysctl -p
sudo docker exec clab-srv6-r7 vtysh -c 'configure terminal' -f /etc/frr/zebra.conf
sudo docker exec clab-srv6-r7 vtysh -c 'configure terminal' -f /etc/frr/isisd.conf
sudo docker exec clab-srv6-r7 sysctl -w net.ipv6.conf.eth1.seg6_enabled=1
sudo docker exec clab-srv6-r7 sysctl -w net.ipv6.conf.eth2.seg6_enabled=1
sudo docker exec clab-srv6-r7 sysctl -w net.ipv6.conf.eth3.seg6_enabled=1

#r11
sudo docker exec clab-srv6-r11 sysctl -p
sudo docker exec clab-srv6-r11 vtysh -c 'configure terminal' -f /etc/frr/zebra.conf
sudo docker exec clab-srv6-r11 vtysh -c 'configure terminal' -f /etc/frr/isisd.conf
sudo docker exec clab-srv6-r11 sysctl -w net.ipv6.conf.eth1.seg6_enabled=1
sudo docker exec clab-srv6-r11 sysctl -w net.ipv6.conf.eth2.seg6_enabled=1
sudo docker exec clab-srv6-r11 ip link add link eth3 name eth3.111 type vlan id 111
sudo docker exec clab-srv6-r11 ip link add link eth3 name eth3.112 type vlan id 112
sudo docker exec clab-srv6-r11 ip link add link eth3 name eth3.113 type vlan id 113
sudo docker exec clab-srv6-r11 ip -6 addr add fd00:0:2::/127 dev eth3.111
sudo docker exec clab-srv6-r11 ip -6 addr add fd00:0:2::2/127 dev eth3.112
sudo docker exec clab-srv6-r11 ip -6 addr add fd00:0:2::4/127 dev eth3.113
sudo docker exec clab-srv6-r11 ip link set eth3.111 up
sudo docker exec clab-srv6-r11 ip link set eth3.112 up
sudo docker exec clab-srv6-r11 ip link set eth3.113 up

#r12
sudo docker exec clab-srv6-r12 sysctl -p
sudo docker exec clab-srv6-r12 vtysh -c 'configure terminal' -f /etc/frr/zebra.conf
sudo docker exec clab-srv6-r12 vtysh -c 'configure terminal' -f /etc/frr/isisd.conf
sudo docker exec clab-srv6-r12 sysctl -w net.ipv6.conf.eth1.seg6_enabled=1
sudo docker exec clab-srv6-r12 sysctl -w net.ipv6.conf.eth2.seg6_enabled=1
sudo docker exec clab-srv6-r12 ip link add link eth3 name eth3.121 type vlan id 121
sudo docker exec clab-srv6-r12 ip link add link eth3 name eth3.122 type vlan id 122
sudo docker exec clab-srv6-r12 ip link add link eth3 name eth3.123 type vlan id 123
sudo docker exec clab-srv6-r12 ip -6 addr add fd00:0:3::/127 dev eth3.121
sudo docker exec clab-srv6-r12 ip -6 addr add fd00:0:3::2/127 dev eth3.122
sudo docker exec clab-srv6-r12 ip -6 addr add fd00:0:3::4/127 dev eth3.123
sudo docker exec clab-srv6-r12 ip link set eth3.121 up
sudo docker exec clab-srv6-r12 ip link set eth3.122 up
sudo docker exec clab-srv6-r12 ip link set eth3.123 up

#r13
sudo docker exec clab-srv6-r13 sysctl -p
sudo docker exec clab-srv6-r13 vtysh -c 'configure terminal' -f /etc/frr/zebra.conf
sudo docker exec clab-srv6-r13 vtysh -c 'configure terminal' -f /etc/frr/isisd.conf
sudo docker exec clab-srv6-r13 sysctl -w net.ipv6.conf.eth1.seg6_enabled=1
sudo docker exec clab-srv6-r13 sysctl -w net.ipv6.conf.eth2.seg6_enabled=1
sudo docker exec clab-srv6-r13 ip link add link eth3 name eth3.111 type vlan id 111
sudo docker exec clab-srv6-r13 ip link add link eth3 name eth3.112 type vlan id 112
sudo docker exec clab-srv6-r13 ip link add link eth3 name eth3.113 type vlan id 113
sudo docker exec clab-srv6-r13 ip link add link eth3 name eth3.121 type vlan id 121
sudo docker exec clab-srv6-r13 ip link add link eth3 name eth3.122 type vlan id 122
sudo docker exec clab-srv6-r13 ip link add link eth3 name eth3.123 type vlan id 123
sudo docker exec clab-srv6-r13 ip -6 addr add fd00:0:1::/127 dev eth3.111
sudo docker exec clab-srv6-r13 ip -6 addr add fd00:0:1::2/127 dev eth3.112
sudo docker exec clab-srv6-r13 ip -6 addr add fd00:0:1::4/127 dev eth3.113
sudo docker exec clab-srv6-r13 ip -6 addr add fd00:0:1::6/127 dev eth3.121
sudo docker exec clab-srv6-r13 ip -6 addr add fd00:0:1::8/127 dev eth3.122
sudo docker exec clab-srv6-r13 ip -6 addr add fd00:0:1::a/127 dev eth3.123
sudo docker exec clab-srv6-r13 ip link set eth3.111 up
sudo docker exec clab-srv6-r13 ip link set eth3.112 up
sudo docker exec clab-srv6-r13 ip link set eth3.113 up
sudo docker exec clab-srv6-r13 ip link set eth3.121 up
sudo docker exec clab-srv6-r13 ip link set eth3.122 up
sudo docker exec clab-srv6-r13 ip link set eth3.123 up