# Network configuration parameters

# MAC addresses
SRC_MAC = "02:00:00:00:01:aa"
DST_MAC = "02:00:00:00:02:aa"

# Device MAC addresses
R1_MAC = SRC_MAC
R2_MAC = "02:00:00:00:01:ff"

# IP addresses
SRC_IP = "fd00:0:1::3"
DST_IPS = [f"fd00:0:2::b{str(i)}" for i in range(2, 12)]

# Device IP configuration
R1_IP = SRC_IP
R1_GATEWAY = "fd00:0:1::1"
R2_IP = "fd00:0:2::b1"
R2_GATEWAY = "fd00:0:2::1"
IP_PREFIX = 64

# API configuration
IXIA_API_LOCATION = "https://172.20.20.5:8443"
NCS_API_LOCATION = "http://localhost:5000"