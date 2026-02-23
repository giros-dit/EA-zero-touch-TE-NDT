import time
import snappi
import urllib3
import json

urllib3.disable_warnings()

src_mac= "02:00:00:00:01:aa"
dst_mac= "02:00:00:00:02:aa"

# Create a new API handle to make API calls against OTG
# with HTTP as default transport protocol
api = snappi.api(location="https://172.20.20.5:8443")

# Create a new traffic configuration that will be set on OTG
cfg = api.config()

# Add a test port to the configuration
ptx = cfg.ports.add(name="ptx", location="eth1")
prx = cfg.ports.add(name="prx", location="eth2")

link100 = cfg.layer1.add(name="link100", port_names=["ptx", "prx"])
link100.speed = "speed_100_fd_mbps"


r1 = cfg.devices.add(name="r1")
r2 = cfg.devices.add(name="r2")

r1Eth = r1.ethernets.add(name="r1Eth")
r1Eth.mac = src_mac

r2Eth = r2.ethernets.add(name="r2Eth")
r2Eth.mac = dst_mac

r1Eth.connection.port_name = ptx.name
r2Eth.connection.port_name = prx.name

r1Ip = r1Eth.ipv4_addresses.add(name="r1Ip", address="1.1.1.1", gateway="1.1.1.2", prefix=24)
r2Ip = r2Eth.ipv4_addresses.add(name="r2Ip", address="2.2.2.1", gateway="2.2.2.2", prefix=24)

#########################################################################
# Initial definition of flow

name = "stepped_pyramid"
variation_interval = 5*1
#variation_interval = 15
packet_size = 1500
rate_percentages = [10,20,30,40,50,60,70,80,90,100,90,80,70,60,50,40,30,20,10]

#########################################################################

# Configure a flow and set previously created test port as one of endpoints
flow = cfg.flows.add(name=name)

flow.tx_rx.device.tx_names = [r1Ip.name]
flow.tx_rx.device.rx_names = [r2Ip.name]

# and enable tracking flow metrics
flow.metrics.enable = True
flow.metrics.timestamps = True
flow.metrics.latency.enable = True
flow.metrics.latency.mode = "cut_through"

# Configure number of packets to transmit for previously configured flow
flow.duration.fixed_seconds.seconds = variation_interval * rate_percentages.__len__()

# and fixed byte size of all packets in the flow
flow.size.fixed = packet_size

flow.rate.percentage = rate_percentages[0]

# Configure protocol headers for all packets in the flow
#eth, ip, udp = flow.packet.ethernet().ipv6().udp()
eth, ip, tcp = flow.packet.ethernet().ipv4().tcp()

eth.src.value = src_mac
#eth.dst.value = dst_mac

ip.src.value = "10.10.10.1"
ip.dst.value = "20.20.20.1"

# ip.src.value = "192.168.1.1"
# ip.dst.value = "192.168.1.6"

#ip.src.value = "fd00:0:1::1"
#ip.dst.value = "fd00:0:2::2"

tcp.src_port.value = 1234
tcp.dst_port.value = 1234

#########################################################################

# Push traffic configuration constructed so far to OTG
api.set_config(cfg)

# Start transmitting the packets from configured flow
cs = api.control_state()
cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.START

start_time = time.time()
percentage_index = 0

api.set_control_state(cs)

def metrics_ok():
    # Fetch metrics for configured flow
    mr = api.metrics_request()
    mr.flow.flow_names = [flow.name]
    m = api.get_metrics(mr).flow_metrics[0] # type: ignore
    print("FLOW METRICS", m, sep="\n")
    return m.transmit == m.STOPPED

# Keep polling until either expectation is met or deadline exceeds
try:
    while not metrics_ok():
        current_time = time.time()
        if current_time - start_time >= variation_interval * (percentage_index + 1):
            if percentage_index < len(rate_percentages) - 1:
                percentage_index = percentage_index + 1
                
                flow = api.get_config().flows[0] # type: ignore
                flow.rate.percentage = rate_percentages[percentage_index]
                
                # Create a config update object specifically for updating flow rate
                config_update = api.config_update()

                flow_updated_config = config_update.flows
                flow_updated_config.flows.append(flow)
                flow_updated_config.property_names = ["rate"]
                
                # Send the update
                api.update_config(config_update)

        time.sleep(1)

except KeyboardInterrupt:
    cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.STOP
    api.set_control_state(cs)
    print("Stopping traffic...")
    time.sleep(5)