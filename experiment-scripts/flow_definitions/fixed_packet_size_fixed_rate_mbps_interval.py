from snappi import Config, Flow, Device
import time
import threading
import requests
import urllib.parse
import logging

# Import monitor function for debugging
from minio_flow_uploader import monitor_s3_files, log_current_stack

# Create logger for this module
logger = logging.getLogger(__name__)

BUTTON_VARIANT = "grouped"

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
        - Uses UDP protocol with fixed source and destination ports (1234)
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

def variation_function(api, cfg, NCS_API_LOCATION, variation_interval: int, simultaneous_flows: list):
    """
    Handle flow start/stop variations based on time intervals and flow counts.
    This function manages the transmission of network flows by starting and stopping them
    according to a predefined schedule. It uses the Snappi API to control the state of the
    traffic flows defined in the configuration object.
    Runs in a separate thread to avoid blocking the GUI.
    
    Args:
        api: Snappi API object for control state operations
        cfg: Configuration object containing flow definitions
        variation_interval (int): Time interval in seconds between flow changes
        simultaneous_flows (list): Array of flow counts per interval
    
    Returns:
        tuple: (variation_thread, stop_event) for controlling the thread
    """
    # Create a stop event to control the thread
    stop_event = threading.Event()
    
    def variation_worker():
        # Get control state
        cs = api.control_state()
        
        # Storage experiment start time 
        start_time = time.time()
        
        # Start with the first target from simultaneous_flows (don't assume 0)
        current_active_flows = simultaneous_flows[0] if simultaneous_flows else 0
        
        logger.info(f"Starting variation with {current_active_flows} initial active flows")
        
        # Start initial flows if needed
        if current_active_flows > 0:
            initial_flows = [cfg.flows[i].name for i in range(min(current_active_flows, len(cfg.flows)))]
            
            # Start traffic flows (don't send API requests - flows already exist)
            cs.traffic.flow_transmit.flow_names = initial_flows
            cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.START
            api.set_control_state(cs)
            
            logger.info(f"Started initial {current_active_flows} flows: {initial_flows}")
        
        # Main variation loop - starts from interval 1 (skip the initial setup)
        for interval_index, target_flows in enumerate(simultaneous_flows[1:], 1):
            # Wait for the next interval
            while time.time() - start_time < variation_interval * interval_index:
                if stop_event.wait(1):
                    return
            
            # Only process if there's actually a change
            if target_flows == current_active_flows:
                logger.info(f"Time {time.time() - start_time:.1f}s - Interval {interval_index + 1}: No change needed, keeping {current_active_flows} flows")
                continue
            
            # Determine flows to start and stop
            flows_to_start = []
            flows_to_stop = []
            
            if target_flows > current_active_flows:
                # Need to start more flows - only start the additional ones
                flows_to_start = [cfg.flows[i].name for i in range(current_active_flows, min(target_flows, len(cfg.flows)))]
                
                # Send POST requests for new flows
                for flow_name in flows_to_start:
                    send_api_request(flow_name, 'POST')
                
                # Start traffic for new flows
                cs.traffic.flow_transmit.flow_names = flows_to_start
                cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.START
                api.set_control_state(cs)
                
            elif target_flows < current_active_flows:
                # Need to stop some flows - only stop the excess ones
                flows_to_stop = [cfg.flows[i].name for i in range(target_flows, current_active_flows)]
                
                # Stop traffic flows first
                cs.traffic.flow_transmit.flow_names = flows_to_stop
                cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.STOP
                api.set_control_state(cs)
                
                # Send DELETE requests for stopped flows
                for flow_name in flows_to_stop:
                    send_api_request(flow_name, 'DELETE')
            
            # Update current active flows count
            current_active_flows = target_flows
            
            # Print current state
            elapsed_time = time.time() - start_time
            active_flow_names = [cfg.flows[i].name for i in range(min(current_active_flows, len(cfg.flows)))]
            logger.info(f"Time {elapsed_time:.1f}s - Interval {interval_index + 1}: {current_active_flows} active flows: {active_flow_names}")
        
        # Stop all remaining flows at the end
        logger.info("Experiment finished, stopping all remaining traffic...")
        if current_active_flows > 0:
            remaining_flows = [cfg.flows[i].name for i in range(min(current_active_flows, len(cfg.flows)))]
            
            # Stop traffic first
            cs.traffic.flow_transmit.flow_names = []
            cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.STOP
            api.set_control_state(cs)
            
            # Then send DELETE requests
            for flow_name in remaining_flows:
                send_api_request(flow_name, 'DELETE')
        
        logger.info("Variation thread completed")

    def send_api_request(flow_name, method):
        dst_ip = flow_name.split('_')[-1]
        encoded_ip = urllib.parse.quote(dst_ip, safe='')
        url = f"{NCS_API_LOCATION}/flows/{encoded_ip}"
        
        logger.debug(f"========== BEFORE {method} {dst_ip} ==========")
        log_current_stack(f"About to {method} {dst_ip}")
        monitor_s3_files()
        
        try:
            response = requests.delete(url) if method == 'DELETE' else requests.post(url)
            
            try:
                response_data = response.json()
                message = response_data.get('error' if response.status_code >= 400 else 'message', 'Unknown')
            except:
                message = 'No response data'
            
            logger.info(f"{method} request for flow {flow_name} (IP: {dst_ip}), status: {response.status_code}, response: {message}")
            
            logger.debug(f"========== AFTER {method} {dst_ip} ==========")
            monitor_s3_files()
            
        except Exception as e:
            logger.error(f"Error sending {method} request for flow {flow_name}: {e}")

    
    variation_thread = threading.Thread(target=variation_worker, daemon=True)
    variation_thread.start()
    
    return variation_thread, stop_event