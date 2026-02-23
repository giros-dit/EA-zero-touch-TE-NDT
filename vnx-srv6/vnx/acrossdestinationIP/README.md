# vnx-srv6
VNX scenarios for studying and analyzing SRv6 (Segment Routing over IPv6 dataplane).


##  Across

### Before launching the scenarios


To run the scenarios, it is necessary to add the following lines to the **/etc/sysctl.conf** file:

```
fs.file-max = 4194304
fs.inotify.max_queued_events = 2097152
fs.inotify.max_user_instances = 2097152
fs.inotify.max_user_watches = 2097152
```

Finally, restart the system or run **sysctl --system** to apply these changes.

---

### Launch scenario
Too launch it, run the next commands:

```
cd ./EscenarioAcross
python3 startscenario.py
```

### IPv6 and interfaces Tables

#### CORE Sistem - router


| **Dispositivo** | **Interfaces** | **VLAN** | **Dirección IPv6**   | **Router Interface** | **Router Interface IP**  |
|-----------------|----------------|----------|----------------------|----------------------|--------------------------|
| **gNB1**        | eth1.111       | 111      | fd00:0:2::1/127      | R11 - eth4.111       | fd00:0:2::/127           |
|                 | eth1.112       | 112      | fd00:0:2::3/127      | R11 - eth4.112       | fd00:0:2::2/127          |
|                 | eth1.113       | 113      | fd00:0:2::5/127      | R11 - eth4.113       | fd00:0:2::4/127          |
| **gNB2**        | eth1.121       | 121      | fd00:0:3::1/127      | R12 - eth4.121       | fd00:0:3::/127           |
|                 | eth1.122       | 122      | fd00:0:3::3/127      | R12 - eth4.122       | fd00:0:3::2/127          |
|                 | eth1.123       | 123      | fd00:0:3::5/127      | R12 - eth4.123       | fd00:0:3::4/127          |
| **UPF**         | eth1.111       | 111      | fd00:0:1::1/127      | R13 - eth4.111       | fd00:0:1::/127           |
|                 | eth1.112       | 112      | fd00:0:1::3/127      | R13 - eth4.112       | fd00:0:1::2/127          |
|                 | eth1.113       | 113      | fd00:0:1::5/127      | R13 - eth4.113       | fd00:0:1::4/127          |
|                 | eth1.121       | 121      | fd00:0:1::7/127      | R13 - eth4.121       | fd00:0:1::6/127          |
|                 | eth1.122       | 122      | fd00:0:1::9/127      | R13 - eth4.122       | fd00:0:1::8/127          |
|                 | eth1.123       | 123      | fd00:0:1::b/127      | R13 - eth4.123       | fd00:0:1::a/127          |


#### Links router-router

| **Router A**    | **Router B**    | **Router A IPv6**        | **Router B IPv6**          |
|-----------------|-----------------|--------------------------|----------------------------|
| **r1  - eth2**  | **r2  - eth2**  | `fcf0:0:1:2::1/64`       | `fcf0:0:1:2::2/64`         |
| **r1  - eth3**  | **r4  - eth2**  | `fcf0:0:1:4::1/64`       | `fcf0:0:1:4::2/64`         |
| **r1  - eth4**  | **r11 - eth2**  | `fcf0:0:1:11::1/64`      | `fcf0:0:1:11::2/64`        |
| **r2  - eth3**  | **r3  - eth2**  | `fcf0:0:2:3::1/64`       | `fcf0:0:2:3::2/64`         |
| **r2  - eth4**  | **r5  - eth2**  | `fcf0:0:2:5::1/64`       | `fcf0:0:2:5::2/64`         |
| **r2  - eth5**  | **r12 - eth2**  | `fcf0:0:2:12::1/64`      | `fcf0:0:2:12::2/64`        |
| **r3  - eth3**  | **r7  - eth2**  | `fcf0:0:3:7::1/64`       | `fcf0:0:3:7::2/64`         |
| **r3  - eth4**  | **r12 - eth3**  | `fcf0:0:3:12::1/64`      | `fcf0:0:3:12::2/64`        |
| **r3  - eth5**  | **r13 - eth2**  | `fcf0:0:3:13::1/64`      | `fcf0:0:3:13::2/64`        |
| **r4  - eth3**  | **r6  - eth2**  | `fcf0:0:4:6::1/64`       | `fcf0:0:4:6::2/64`         |
| **r4  - eth4**  | **r11 - eth3**  | `fcf0:0:4:11::1/64`      | `fcf0:0:4:11::2/64`        |
| **r5  - eth3**  | **r6  - eth3**  | `fcf0:0:5:6::1/64`       | `fcf0:0:5:6::2/64`         |
| **r6  - eth4**  | **r7  - eth3**  | `fcf0:0:6:7::1/64`       | `fcf0:0:6:7::2/64`         |
| **r7  - eth4**  | **r13 - eth3**  | `fcf0:0:7:13::1/64`      | `fcf0:0:7:13::2/64`        |

#### Routers ID

| **Router**      | **ID**               |
|-----------------|----------------------|
| **r1**          | `fcff:1::1/32`       |
| **r2**          | `fcff:2::1/32`       |
| **r3**          | `fcff:3::1/32`       |
| **r4**          | `fcff:4::1/32`       |
| **r5**          | `fcff:5::1/32`       |
| **r6**          | `fcff:6::1/32`       |
| **r7**          | `fcff:7::1/32`       |
| **r11**         | `fcff:11::1/32`      |
| **r12**         | `fcff:12::1/32`      |
| **r13**         | `fcff:13::1/32`      |

---
## SRv6 tunnels

### Python scritps to generate tunnels
There is a script to create SRv6 tunnels in EscenarioAcrross. To use it, first run the command; a help sheet is append with numbers to use in the script:

```
python3 createjson.py
```
#### Help sheet for createjson.py
| **router**     | **VLAN**   |         
|----------------|------------|
| **r1**         | 111        |
|                | 112        |
|                | 113        |
| **r2**         | 121        |
|                | 122        |
|                | 123        |

| **Router**     | **router_id** |         
|----------------|---------------|
| **r1**         | 1             |
| **r2**         | 2             |
| **r3**         | 3             |
| **r4**         | 4             |
| **r5**         | 5             |
| **r6**         | 6             |
| **r7**         | 7             |
| **r11**        | 11            |
| **r12**        | 12            |


### Linux commands for create tunnels
Example between gNB1 - UPF:
**r11**
```
ip -6 route add fd00:0:1::/64 encap seg6 mode encap segs fcff:4::1,fcff:13::1 dev eth4.111
```
**r13**
```
ip -6 route add fd00:0:2::/64 encap seg6 mode encap segs fcff:4::1,fcff:11::1 dev eth4.111
```
