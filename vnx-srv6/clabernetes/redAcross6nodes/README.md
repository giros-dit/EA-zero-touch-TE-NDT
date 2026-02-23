# c9s 6 routers
Claberntes scenarios for studying and analyzing SRv6 (Segment Routing over IPv6 dataplane).


```
alias clabverter='sudo docker run --user $(id -u) \
    -v $(pwd):/clabernetes/work --rm \
    ghcr.io/giros-dit/clabernetes/clabverter'
```

```
clabverter --naming non-prefixed --outputDirectory ./converted --destinationNamespace across-tc32
```

### IPv6 and interfaces Tables

#### final sistem - edge router


| **Dispositivo** | **Interfaces** | **Dirección IPv6**   | **Router Interface** | **Router Interface IP**  | **Multusnet**       |
|-----------------|----------------|----------------------|----------------------|--------------------------|---------------------|
| **hupf-h1**     | eth1           | fd00:0:1::1/127      | ru - eth1            | fd00:0:1::/127           |`2001`               |
| **hgnb-h1**     | eth1           | fd00:0:2::2/64       | rg - eth1            | fd00:0:2::1/64           |`2002`               |
| **hgnb-h2**     | eth1           | fd00:0:2::3/64       | rg - eth1            | fd00:0:2::1/64           |`2002`               |
| **hgnb-h3**     | eth1           | fd00:0:2::4/64       | rg - eth1            | fd00:0:2::1/64           |`2002`               |


#### Links router-router

| **Router A**    | **Router B**    | **Router A IPv6**        | **Router B IPv6**          | **Multusnet**       |
|-----------------|-----------------|--------------------------|----------------------------|---------------------|
| **rg  - eth2**  | **r1  - eth1**  | `fcf0:0:1:6::1/64`       | `fcf0:0:1:6::2/64`         |`1001`               |
| **rg  - eth3**  | **r3  - eth1**  | `fcf0:0:3:6::1/64`       | `fcf0:0:1:6::2/64`         |`1004`               |
| **r1  - eth2**  | **r2  - eth1**  | `fcf0:0:1:2::1/64`       | `fcf0:0:1:2::2/64`         |`1002`               |
| **r3  - eth2**  | **r4  - eth1**  | `fcf0:0:3:4::1/64`       | `fcf0:0:3:4::2/64`         |`1005`               |
| **r2  - eth2**  | **ru  - eth2**  | `fcf0:0:2:5::1/64`       | `fcf0:0:2:5::2/64`         |`1003`               |
| **r4  - eth2**  | **ru  - eth3**  | `fcf0:0:4:5::1/64`       | `fcf0:0:4:5::2/64`         |`1006`               |


#### Routers ID

| **Router**      | **ID**               |
|-----------------|----------------------|
| **r1**          | `fcff:1::1/32`       |
| **r2**          | `fcff:2::1/32`       |
| **r3**          | `fcff:3::1/32`       |
| **r4**          | `fcff:4::1/32`       |
| **ru**          | `fcff:5::1/32`       |
| **rg**          | `fcff:6::1/32`       |


---