from snappi import Config, Flow, Device
import time
import threading
import requests
import urllib.parse
import logging

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
        Flow: The configured flow object
        
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

def variation_function(api, cfg, NCS_API_LOCATION, rate_min: int, rate_max: int, rate_step: int, 
                      flow_duration: int, ncs_to_flow_delay: float,
                      src_ip: str = None, dst_ip: str = None, 
                      src_mac: str = None, dst_mac: str = None, packet_size: int = None):
    """
    Execute sequential rate tests on a single flow with different transmission rates.
    
    This function tests network flow performance by sequentially transmitting traffic at different
    rates from rate_min to rate_max in rate_step increments. Each test runs for flow_duration
    seconds and the results are evaluated for packet/byte loss.
    
    IMPORTANT: For this test, the flow is deleted and recreated before each test iteration
    to reset metrics to 0, ensuring clean measurements for each rate.
    
    Args:
        api: Snappi API object for control state operations
        cfg: Configuration object containing a single flow definition
        NCS_API_LOCATION (str): URL of the Network Control Stack API
        rate_min (int): Minimum transmission rate in Mbps
        rate_max (int): Maximum transmission rate in Mbps
        rate_step (int): Step increment between rates in Mbps
        flow_duration (int): Duration to run each flow test in seconds
        ncs_to_flow_delay (float): Delay in seconds after NCS API POST before starting traffic
        src_ip (str): Source IPv6 address for flow recreation
        dst_ip (str): Destination IPv6 address for flow recreation
        src_mac (str): Source MAC address for flow recreation
        dst_mac (str): Destination MAC address for flow recreation
        packet_size (int): Packet size in bytes for flow recreation
    
    Returns:
        tuple: (variation_thread, stop_event) for controlling the thread
    """
    # Create a stop event to control the thread
    stop_event = threading.Event()
    
    def variation_worker():
        # Get control state
        cs = api.control_state()
        
        # Storage for test results
        test_results = []
        
        # Get the single flow and store its configuration parameters
        if len(cfg.flows) != 1:
            logger.error(f"Sequential rate test requires exactly 1 flow, found {len(cfg.flows)}")
            return
        
        # Store original flow configuration before starting tests
        original_flow = cfg.flows[0]
        flow_name = original_flow.name
        flow_dst_ip = flow_name.replace('flow_', '')
        original_packet_size = original_flow.size.fixed
        
        # Get device names from the original flow
        tx_device_names = original_flow.tx_rx.device.tx_names
        rx_device_names = original_flow.tx_rx.device.rx_names
        
        # Use provided parameters or defaults from original flow
        use_packet_size = packet_size if packet_size is not None else original_packet_size
        use_src_ip = src_ip if src_ip is not None else "fd00:0:1::3"
        use_dst_ip = dst_ip if dst_ip is not None else flow_dst_ip
        use_src_mac = src_mac if src_mac is not None else "02:00:00:00:01:aa"
        use_dst_mac = dst_mac if dst_mac is not None else "02:00:00:00:02:aa"
        
        logger.info(f"Starting sequential rate test from {rate_min} to {rate_max} Mbps (step: {rate_step} Mbps)")
        logger.info(f"Flow duration: {flow_duration}s, NCS delay: {ncs_to_flow_delay}s")
        logger.info(f"Note: Flow will be recreated before each test to reset metrics to 0")
        
        # Iterate through all rate values
        for rate_mbps in range(rate_min, rate_max + 1, rate_step):
            if stop_event.is_set():
                logger.info("Sequential rate test stopped by user")
                break
            
            logger.info(f"\n{'='*60}")
            logger.info(f"Testing rate: {rate_mbps} Mbps")
            logger.info(f"{'='*60}")
            
            # RECREATE THE FLOW to reset metrics to 0
            logger.info(f"Recreating flow to reset metrics...")
            
            # Remove all existing flows
            cfg.flows.clear()
            
            # Recreate the flow with the same configuration but new rate
            flow = cfg.flows.add(name=flow_name)
            flow.tx_rx.device.tx_names = tx_device_names
            flow.tx_rx.device.rx_names = rx_device_names
            flow.metrics.enable = True
            flow.metrics.timestamps = True
            flow.metrics.latency.enable = True
            flow.metrics.latency.mode = "cut_through"
            flow.size.fixed = use_packet_size
            flow.rate.mbps = rate_mbps
            
            # Configure protocol headers for the recreated flow
            eth, ip, udp = flow.packet.ethernet().ipv6().udp()
            eth.src.value = use_src_mac
            eth.dst.value = use_dst_mac
            ip.src.value = use_src_ip
            ip.dst.value = use_dst_ip
            udp.src_port.value = 1234
            udp.dst_port.value = 1234
            
            # Push the updated configuration to reset the flow
            api.set_config(cfg)
            logger.info(f"Flow recreated successfully with rate {rate_mbps} Mbps, metrics reset to 0")
            
            # Send POST request to NCS API
            encoded_ip = urllib.parse.quote(use_dst_ip, safe='')
            url = f"{NCS_API_LOCATION}/flows/{encoded_ip}"
            
            try:
                logger.info(f"Sending POST request to NCS API for flow {flow_name} (IP: {use_dst_ip})")
                response = requests.post(url)
                
                try:
                    response_data = response.json()
                    message = response_data.get('error' if response.status_code >= 400 else 'message', 'Unknown')
                except:
                    message = 'No response data'
                
                logger.info(f"NCS API response - status: {response.status_code}, message: {message}")
                
            except Exception as e:
                logger.error(f"Error sending POST request to NCS API: {e}")
            
            # Wait NCS_TO_FLOW_DELAY before starting traffic
            logger.info(f"Waiting {ncs_to_flow_delay}s before starting traffic...")
            if stop_event.wait(ncs_to_flow_delay):
                logger.info("Test stopped during NCS delay")
                break
            
            # Get initial metrics
            mr_initial = api.metrics_request()
            mr_initial.flow.flow_names = [flow_name]
            metrics_initial = api.get_metrics(mr_initial).flow_metrics[0]
            
            initial_bytes_tx = metrics_initial.bytes_tx
            initial_bytes_rx = metrics_initial.bytes_rx
            initial_frames_tx = metrics_initial.frames_tx
            initial_frames_rx = metrics_initial.frames_rx
            
            # Start traffic
            logger.info(f"Starting traffic at {rate_mbps} Mbps...")
            cs.traffic.flow_transmit.flow_names = [flow_name]
            cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.START
            api.set_control_state(cs)
            
            # Wait for flow_duration
            logger.info(f"Running traffic for {flow_duration}s...")
            if stop_event.wait(flow_duration):
                logger.info("Test stopped during traffic transmission")
                # Stop traffic before breaking
                cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.STOP
                api.set_control_state(cs)
                break
            
            # Stop traffic
            logger.info("Stopping traffic...")
            cs.traffic.flow_transmit.state = cs.traffic.flow_transmit.STOP
            api.set_control_state(cs)
            
            # Wait for metrics to stabilize after stopping traffic
            # This is critical to ensure all packets are properly counted
            stabilization_delay = 3  # seconds
            logger.info(f"Waiting {stabilization_delay}s for metrics to stabilize...")
            time.sleep(stabilization_delay)
            
            # Get final metrics
            mr_final = api.metrics_request()
            mr_final.flow.flow_names = [flow_name]
            metrics_final = api.get_metrics(mr_final).flow_metrics[0]
            
            final_bytes_tx = metrics_final.bytes_tx
            final_bytes_rx = metrics_final.bytes_rx
            final_frames_tx = metrics_final.frames_tx
            final_frames_rx = metrics_final.frames_rx
            
            # Calculate differences
            bytes_tx = final_bytes_tx - initial_bytes_tx
            bytes_rx = final_bytes_rx - initial_bytes_rx
            frames_tx = final_frames_tx - initial_frames_tx
            frames_rx = final_frames_rx - initial_frames_rx
            
            # Determine if test passed (no packet or byte loss)
            test_passed = (bytes_tx == bytes_rx) and (frames_tx == frames_rx)
            result_status = "OK" if test_passed else "NOTOK"
            
            # Log results
            logger.info(f"\nResults for {rate_mbps} Mbps:")
            logger.info(f"  Bytes:  TX={bytes_tx}, RX={bytes_rx}, Loss={bytes_tx - bytes_rx}")
            logger.info(f"  Frames: TX={frames_tx}, RX={frames_rx}, Loss={frames_tx - frames_rx}")
            logger.info(f"  Status: {result_status}")
            
            # Store result
            test_results.append({
                'rate_mbps': rate_mbps,
                'bytes_tx': bytes_tx,
                'bytes_rx': bytes_rx,
                'frames_tx': frames_tx,
                'frames_rx': frames_rx,
                'status': result_status
            })
            
            # Send DELETE request to NCS API
            try:
                logger.info(f"Sending DELETE request to NCS API for flow {flow_name} (IP: {use_dst_ip})")
                response = requests.delete(url)
                
                try:
                    response_data = response.json()
                    message = response_data.get('error' if response.status_code >= 400 else 'message', 'Unknown')
                except:
                    message = 'No response data'
                
                logger.info(f"NCS API response - status: {response.status_code}, message: {message}")
                
            except Exception as e:
                logger.error(f"Error sending DELETE request to NCS API: {e}")
        
        # Print summary of all tests
        logger.info(f"\n{'='*60}")
        logger.info("SEQUENTIAL RATE TEST SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"{'Rate (Mbps)':<12} {'Bytes TX':<12} {'Bytes RX':<12} {'Frames TX':<12} {'Frames RX':<12} {'Status':<8}")
        logger.info(f"{'-'*60}")
        
        for result in test_results:
            logger.info(f"{result['rate_mbps']:<12} {result['bytes_tx']:<12} {result['bytes_rx']:<12} "
                       f"{result['frames_tx']:<12} {result['frames_rx']:<12} {result['status']:<8}")
        
        logger.info(f"{'='*60}")
        
        # Count OK vs NOTOK
        ok_count = sum(1 for r in test_results if r['status'] == 'OK')
        notok_count = len(test_results) - ok_count
        
        logger.info(f"Total tests: {len(test_results)}, OK: {ok_count}, NOTOK: {notok_count}")
        logger.info("Sequential rate test completed")
    
    variation_thread = threading.Thread(target=variation_worker, daemon=True)
    variation_thread.start()
    
    return variation_thread, stop_event
