from snappi import Config, Flow, Device

BUTTON_VARIANT = "individual"

def define_flow(
    cfg: Config, 
    name: str, 
    tx_device: Device, 
    rx_device: Device, 
    packet_size: int, 
    rate_mbps: float, 
    src_ip: str, 
    dst_ip: str, 
    src_mac: str, 
    dst_mac: str
) -> Flow:
    """
    Configure a network flow with fixed packet size and transmission rate.
    
    Creates and configures a bidirectional network flow between two devices with specified
    packet characteristics, rate limiting, and protocol headers.
    
    Args:
        cfg: Configuration object containing flow definitions
        name (str): Name identifier for the flow
        tx_device: Transmitting device object
        rx_device: Receiving device object  
        packet_size (int): Fixed size in bytes for all packets in the flow
        rate_mbps (float): Transmission rate in megabits per second
        src_ip (str): Source IPv6 address
        dst_ip (str): Destination IPv6 address
        src_mac (str): Source MAC address
        dst_mac (str): Destination MAC address
    
    Returns:
        None
        
    Note:
        - Enables flow metrics including timestamps and cut-through latency measurement
        - Uses UDP protocol with fixed source and destination ports
        - Configures Ethernet/IPv6/UDP packet headers
    """
    
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

    return flow