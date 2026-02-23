import time
import snappi
import urllib3

urllib3.disable_warnings()

# MAC address of Ixia tx port
src_mac= "02:00:00:00:01:aa"

# MAC address of first hop incoming interface
dst_mac= "02:00:00:00:02:aa"

# IPv6 source address
src_ip= "fd00:0:1::2"

# List of destination IPv6 addresses
# Last hop must be configured to route this subnet through Ixia's rx port
# fd00:0:2::b0/124
dst_ips =  [f"fd00:0:2::b{str(i)}" for i in range(2, 3)]

# Create a new API handle to make API calls against OTG
# with HTTP as default transport protocol
api = snappi.api(location="https://172.20.20.5:8443")

# Create a new traffic configuration that will be set on OTG
cfg = api.config()

# Add tx and rx ports to the configuration
ptx = cfg.ports.add(name="ptx", location="eth1")
prx = cfg.ports.add(name="prx", location="eth2")

# Limit link speed to 100 Mbps full-duplex
link100 = cfg.layer1.add(name="link100", port_names=["ptx", "prx"])
link100.speed = "speed_100_fd_mbps"

# Add two devices to the configuration
# and set their MAC addresses
r1 = cfg.devices.add(name="r1")
r2 = cfg.devices.add(name="r2")

r1Eth = r1.ethernets.add(name="r1Eth")
r1Eth.mac = src_mac

# Ixia rx port MAC address is set statically as it does not affect the test
r2Eth = r2.ethernets.add(name="r2Eth")
r2Eth.mac = "02:00:00:00:01:ff"

# Set connection of each device to the corresponding test port
r1Eth.connection.port_name = ptx.name
r2Eth.connection.port_name = prx.name

# Add IPv6 addresses to each device
r1Ip = r1Eth.ipv6_addresses.add(name="r1Ip", address=src_ip, gateway="fd00:0:1::1", prefix=64)
r2Ip = r2Eth.ipv6_addresses.add(name="r2Ip", address="fd00:0:2::b0", gateway="fd00:0:2::1", prefix=64)


#########################################################################
# Initial definition of flow

name = "real_traffic_simple"
variation_interval = 30


weighted_packet_sizes = [{"size": 62, "weight": 40}, {"size": 1300, "weight": 5}, {"size": 1500, "weight": 25}, {"size":619, "weight": 30}]

# Add a uniform distribution of packet sizes
# U(min, Max) = U(62, 1300)
min_size = 62
max_size = 1300

# Total weight of the uniform distribution in the overall packet sizes
normal_distribution_total_weight = 0.3

num_sizes = max_size - min_size + 1
weight_per_size = (1 / num_sizes) * normal_distribution_total_weight * 100

packets = [{"size": size, "weight": weight_per_size} for size in range(min_size, max_size + 1)]

weighted_packet_sizes.extend(packets)

simultaenous_flows = [7,6,5,4,3,4,5,6,7,8,8,8,8,8,8,8,8,9,9,9,10,10,9,8]

#########################################################################

def define_flow(name, tx_device, rx_device, weighted_packet_sizes, rate_mbps, dst_ip):
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
    #flow.size.weight_pairs.custom.add(weighted_packet_sizes)

    for size_weight in weighted_packet_sizes:
        flow.size.weight_pairs.custom.add(size=size_weight["size"], weight=size_weight["weight"])

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

# Define a flow for each destination IP address
for dst_ip in dst_ips:
    define_flow(f"flow_{dst_ip}", r1Ip, r2Ip, weighted_packet_sizes, 10, dst_ip)

# Push traffic configuration constructed so far to OTG
api.set_config(cfg)

# Assign control state api method to variable
cs = api.control_state()

# Get the first value from simultaneous_flows array
initial_flows_count = simultaenous_flows[0]

# Select only the first N flows from the configuration
flow_names = [flow.name for flow in cfg.flows[:initial_flows_count]]

# Set these flows to be transmitted
cs.traffic.flow_transmit.flow_names = flow_names

print(f"Starting {initial_flows_count} flows: {flow_names}")

# Set flows to start transmitting
cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.START

# Storage experiment start time 
start_time = time.time()
flow_list_index = 0

# Send updated control state to OTG
api.set_control_state(cs)

# Check flows are transmitting and print metrics
def metrics_ok():
    # Fetch metrics for configured flow
    mr = api.metrics_request()
    mr.flow.flow_names = []
    m = api.get_metrics(mr).flow_metrics # type: ignore

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

# Keep printing metrics until experiment is stopped or all flows are stopped
try:
    while not metrics_ok():
        current_time = time.time()
        # Check if a variation interval has passed
        if current_time - start_time >= variation_interval * (flow_list_index + 1):

            # Check if we have more flow configurations to apply
            if flow_list_index+1 >= len(simultaenous_flows):
                print("No more flow configurations to apply, stopping traffic.")
                
                cs.traffic.flow_transmit.flow_names = []
                cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.STOP
                api.set_control_state(cs)
                print("Experiment finished, stopping all traffic...")
                time.sleep(5)
                exit()

            # Get currently running flows
            current_flows = simultaenous_flows[flow_list_index]

            # Move to next flow configuration
            flow_list_index = flow_list_index + 1
            new_flow_count = simultaenous_flows[flow_list_index]

            # Get which flows to start/stop based on new count
            flow_difference = new_flow_count - current_flows

            # Set flows to start or stop based on the difference
            starting_flows = []
            stopping_flows = []

            if flow_difference > 0:
                for i in range(current_flows + 1, new_flow_count + 1):
                    starting_flows.append(cfg.flows[i-1].name)

            elif flow_difference < 0:
                for i in range(new_flow_count + 1, current_flows + 1):
                    stopping_flows.append(cfg.flows[i-1].name)

            else:
                print(f"Time {current_time - start_time:.1f}s: No change in flow count ({new_flow_count})")
                continue
            
            # Get currently running flows
            current_flows = set(cs.traffic.flow_transmit.flow_names)
            
            # Stop flows that are no longer needed
            if len(stopping_flows) > 0:
                cs.traffic.flow_transmit.flow_names = stopping_flows
                cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.STOP
                api.set_control_state(cs)

            # Start new flows
            if len(starting_flows) > 0:
                cs.traffic.flow_transmit.flow_names = starting_flows
                cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.START
                api.set_control_state(cs)
            
            print(f"Time {current_time - start_time:.1f}s: Updated to {new_flow_count} flows: 1 to {new_flow_count}")

        time.sleep(1)

except KeyboardInterrupt:
    cs.traffic.flow_transmit.flow_names = []
    cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.STOP
    api.set_control_state(cs)
    print("Stopping traffic...")
    time.sleep(5)
