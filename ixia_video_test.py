import time
import snappi
import urllib3
import keyboard

urllib3.disable_warnings()

src_mac= "02:00:00:00:01:aa"
#dst_mac= "02:00:00:00:02:aa"

dst_mac = "02:00:00:00:02:aa"  # Add the missing mac address

src_ip= "fd00:0:1::3"
dst_ips =  [f"fd00:0:2::b{str(i)}" for i in range(2, 9)]

# Create a new API handle to make API calls against OTG
# with HTTP as default transport protocol
#api = snappi.api(location="https://172.20.20.5:8443")
#api = snappi.api(location="https://138.4.21.11:31114")
api = snappi.api(location="https://138.4.21.11:31121")


# Create a new traffic configuration that will be set on OTG
cfg = api.config()

# Add tx and rx ports to the configuration
ptx = cfg.ports.add(name="ptx", location="eth1")
prx = cfg.ports.add(name="prx", location="eth2")

# Limit link speed to 100 Mbps full-duplex
# link100 = cfg.layer1.add(name="link100", port_names=["ptx", "prx"])
# link100.speed = "speed_100_fd_mbps"

# Add two devices to the configuration
# and set their MAC addresses
r1 = cfg.devices.add(name="r1")
r2 = cfg.devices.add(name="r2")

r1Eth = r1.ethernets.add(name="r1Eth")
r1Eth.mac = src_mac

r2Eth = r2.ethernets.add(name="r2Eth")
r2Eth.mac = "02:00:00:00:01:ff"

# Set connection of each device to the corresponding test port
r1Eth.connection.port_name = ptx.name
r2Eth.connection.port_name = prx.name

# Add IPv6 addresses to each device
r1Ip = r1Eth.ipv6_addresses.add(name="r1Ip", address=src_ip, gateway="fd00:0:1::1", prefix=64)
r2Ip = r2Eth.ipv6_addresses.add(name="r2Ip", address="fd00:0:2::b1", gateway="fd00:0:2::1", prefix=64)


#########################################################################
# Initial definition of flow

name = "video_flow"
packet_size = 1000

#########################################################################

def define_flow(name, tx_device, rx_device, packet_size, rate_mbps, dst_ip):
    # Configure a flow and set previously created test port as one of endpoints
    flow = cfg.flows.add(name=name)

    flow.tx_rx.device.tx_names = [tx_device.name]
    flow.tx_rx.device.rx_names = [rx_device.name]

    # and enable tracking flow metrics
    flow.metrics.enable = True
    flow.metrics.timestamps = True
    flow.metrics.latency.enable = True
    flow.metrics.latency.mode = "cut_through"

    # and fixed byte size of all packets in the flow
    flow.size.fixed = packet_size

    flow.rate.mbps = rate_mbps

    # Configure protocol headers for all packets in the flow
    eth, ip, udp = flow.packet.ethernet().ipv6().udp()

    eth.src.value = src_mac
    eth.dst.value = dst_mac

    ip.src.value = src_ip
    ip.dst.value = dst_ip

    udp.src_port.value = 1234
    udp.dst_port.value = 1234

#########################################################################


define_flow(f"flow_{dst_ips[0]}", r1Ip, r2Ip, packet_size, 20, dst_ips[0])
define_flow(f"flow_{dst_ips[1]}", r1Ip, r2Ip, packet_size, 20, dst_ips[1])
define_flow(f"flow_{dst_ips[2]}", r1Ip, r2Ip, packet_size, 50, dst_ips[2])
define_flow(f"flow_{dst_ips[3]}", r1Ip, r2Ip, packet_size, 20, dst_ips[3])
define_flow(f"flow_{dst_ips[4]}", r1Ip, r2Ip, packet_size, 45, dst_ips[4])
define_flow(f"flow_{dst_ips[5]}", r1Ip, r2Ip, packet_size, 20, dst_ips[5])
define_flow(f"flow_{dst_ips[6]}", r1Ip, r2Ip, packet_size, 17, dst_ips[6])


# Push traffic configuration constructed so far to OTG
api.set_config(cfg)

# Start transmitting the packets from configured flow
cs = api.control_state()

def metrics_ok():
    # Fetch metrics for configured flow
    mr = api.metrics_request()
    mr.flow.flow_names = []
    m = api.get_metrics(mr).flow_metrics

    # Clear screen before printing new metrics
    print('\n' * 2)
    print("=" * 120)
    print("Current Traffic Metrics")
    print("=" * 120)
    
    # Create headers for each flow
    headers = ['Metric'] + dst_ips
    
    # Define metrics to display with units
    metrics = [
        ('transmit', 'State'),
        ('bytes_tx', 'Bytes Tx (B)'),
        ('bytes_rx', 'Bytes Rx (B)'),
        ('frames_tx', 'Frames Tx'),
        ('frames_rx', 'Frames Rx'),
        ('frames_tx_rate', 'Tx Rate (fps)'),
        ('frames_rx_rate', 'Rx Rate (fps)'),
        ('latency.maximum_ns', 'Latency Max (ns)'),
        ('latency.minimum_ns', 'Latency Min (ns)'),
        ('latency.average_ns', 'Latency Avg (ns)')
    ]
    
    # Calculate column width based on content
    col_width = 20
    
    # Print headers with separator
    print('-' * (col_width * (len(headers) + 1)))
    print('|' + '|'.join(f'{h:^{col_width}}' for h in headers) + '|')
    print('-' * (col_width * (len(headers) + 1)))
    
    # Print each metric row
    for attr, label in metrics:
        row = [label]
        for flow in m:
            # Handle nested attributes (latency)
            value = flow
            for part in attr.split('.'):
                value = getattr(value, part)
            # Format numbers with commas for better readability
            if isinstance(value, (int, float)):
                value = f"{value:,}"
            row.append(str(value))
        print('|' + '|'.join(f'{v:^{col_width}}' for v in row) + '|')
    
    print('-' * (col_width * (len(headers) + 1)))
    print('\n')
    return m[0].transmit == m[0].STOPPED

# Add flow state tracking
flow_states = {i+1: False for i in range(7)}  # Keys 1-7, False means stopped

# Replace the try-except block with this new one
try:
    print("\nPress keys 1-7 to toggle flows. Press Ctrl+C to exit.\n")
    while True:
        for key in range(1, 8):
            if keyboard.is_pressed(str(key)):
                flow_name = f"flow_{dst_ips[key-1]}"
                flow_states[key] = not flow_states[key]
                
                cs.traffic.flow_transmit.flow_names = [flow_name]
                cs.traffic.flow_transmit.state = (cs.traffic.flow_transmit.START 
                    if flow_states[key] else cs.traffic.flow_transmit.STOP)
                api.set_control_state(cs)
                
                print(f"\nFlow {key} {'started' if flow_states[key] else 'stopped'}")
                time.sleep(0.3)  # Debounce
                
        metrics_ok()
        time.sleep(0.1)

except KeyboardInterrupt:
    cs.traffic.flow_transmit.flow_names = []
    cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.STOP
    api.set_control_state(cs)
    print("\nStopping all traffic...")
    time.sleep(5)
