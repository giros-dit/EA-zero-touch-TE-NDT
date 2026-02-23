# Prueba b5g

## Resultados Hosto to Host

### Resumen de Jitters y Pérdida de Paquetes

- **Jitters:** [0.005, 0.006, 0.02, 0.007, 0.058, 0.008, 0.015, 0.021, 0.009, 0.019]
- **Pérdida de paquetes (número):** [0, 100, 306, 5, 0, 0, 11, 6, 65, 105]
- **Total de paquetes enviados:** [124990, 124990, 124990, 124990, 124989, 124989, 124990, 124991, 124990, 124990]
- **Pérdida de paquetes (%):** [0.0, 0.08, 0.24, 0.004, 0.0, 0.0, 0.0088, 0.0048, 0.052, 0.084]

#### Estadísticas

- **Jitter:** media=0.0168 ms, min=0.005 ms, max=0.058 ms
- **Paquetes perdidos:** media=59.8, min=0, max=306
- **Pérdida de paquetes (%):** media=0.04736%, min=0.0%, max=0.24%

### Datos

#### Prueba 1

```
iperf 3.14
Linux hupf-h1 5.15.0-130-generic #140-Ubuntu SMP Wed Dec 18 17:59:53 UTC 2024 x86_64
Control connection MSS 1378
Time: Thu, 06 Mar 2025 09:13:09 UTC
Connecting to host fd00:0:2::2, port 5201
      Cookie: hotfpfmi56igf5vby3wtqatbh7yogoi73xfs
      Target Bitrate: 100000000
[  5] local fd00:0:1::1 port 54261 connected to fd00:0:2::2 port 5201
Starting Test: protocol: UDP, 1 streams, 1000 byte blocks, omitting 0 seconds, 10 second test, tos 0
[ ID] Interval           Transfer     Bitrate         Total Datagrams
[  5]   0.00-1.00   sec  11.9 MBytes  99.9 Mbits/sec  12490  
[  5]   1.00-2.00   sec  11.9 MBytes   100 Mbits/sec  12499  
[  5]   2.00-3.00   sec  11.9 MBytes   100 Mbits/sec  12501  
[  5]   3.00-4.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   4.00-5.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   5.00-6.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   6.00-7.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   7.00-8.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   8.00-9.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   9.00-10.00  sec  11.9 MBytes   100 Mbits/sec  12500  
- - - - - - - - - - - - - - - - - - - - - - - - -
Test Complete. Summary Results:
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-10.00  sec   119 MBytes   100 Mbits/sec  0.000 ms  0/124990 (0%)  sender
[  5]   0.00-10.00  sec   119 MBytes   100 Mbits/sec  0.005 ms  0/124990 (0%)  receiver
CPU Utilization: local/sender 9.3% (3.1%u/6.2%s), remote/receiver 12.4% (2.6%u/9.8%s)


iperf Done.

```

#### Prueba 2

```
iperf 3.14
Linux hupf-h1 5.15.0-130-generic #140-Ubuntu SMP Wed Dec 18 17:59:53 UTC 2024 x86_64
Control connection MSS 1378
Time: Thu, 06 Mar 2025 09:14:20 UTC
Connecting to host fd00:0:2::2, port 5201
      Cookie: rix2ei6qu6uwpbai4sbdmgwazk6ahqdufyzj
      Target Bitrate: 100000000
[  5] local fd00:0:1::1 port 44172 connected to fd00:0:2::2 port 5201
Starting Test: protocol: UDP, 1 streams, 1000 byte blocks, omitting 0 seconds, 10 second test, tos 0
[ ID] Interval           Transfer     Bitrate         Total Datagrams
[  5]   0.00-1.00   sec  11.9 MBytes  99.9 Mbits/sec  12490  
[  5]   1.00-2.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   2.00-3.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   3.00-4.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   4.00-5.00   sec  11.9 MBytes   100 Mbits/sec  12499  
[  5]   5.00-6.00   sec  11.9 MBytes   100 Mbits/sec  12501  
[  5]   6.00-7.00   sec  11.9 MBytes   100 Mbits/sec  12499  
[  5]   7.00-8.00   sec  11.9 MBytes   100 Mbits/sec  12501  
[  5]   8.00-9.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   9.00-10.00  sec  11.9 MBytes   100 Mbits/sec  12500  
- - - - - - - - - - - - - - - - - - - - - - - - -
Test Complete. Summary Results:
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-10.00  sec   119 MBytes   100 Mbits/sec  0.000 ms  0/124990 (0%)  sender
[  5]   0.00-10.00  sec   119 MBytes  99.9 Mbits/sec  0.006 ms  100/124990 (0.08%)  receiver
CPU Utilization: local/sender 9.4% (0.8%u/8.6%s), remote/receiver 12.7% (2.2%u/10.5%s)

iperf Done.

```

#### Prueba 3

```
iperf 3.14
Linux hupf-h1 5.15.0-130-generic #140-Ubuntu SMP Wed Dec 18 17:59:53 UTC 2024 x86_64
Control connection MSS 1378
Time: Thu, 06 Mar 2025 09:15:30 UTC
Connecting to host fd00:0:2::2, port 5201
      Cookie: yls2gdolrjfzyflja765sapzgnaghaoz76xm
      Target Bitrate: 100000000
[  5] local fd00:0:1::1 port 35388 connected to fd00:0:2::2 port 5201
Starting Test: protocol: UDP, 1 streams, 1000 byte blocks, omitting 0 seconds, 10 second test, tos 0
[ ID] Interval           Transfer     Bitrate         Total Datagrams
[  5]   0.00-1.00   sec  11.9 MBytes  99.9 Mbits/sec  12489  
[  5]   1.00-2.00   sec  11.9 MBytes   100 Mbits/sec  12501  
[  5]   2.00-3.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   3.00-4.00   sec  11.9 MBytes   100 Mbits/sec  12499  
[  5]   4.00-5.00   sec  11.9 MBytes   100 Mbits/sec  12501  
[  5]   5.00-6.00   sec  11.9 MBytes   100 Mbits/sec  12499  
[  5]   6.00-7.00   sec  11.9 MBytes   100 Mbits/sec  12501  
[  5]   7.00-8.00   sec  11.9 MBytes   100 Mbits/sec  12499  
[  5]   8.00-9.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   9.00-10.00  sec  11.9 MBytes   100 Mbits/sec  12501  
- - - - - - - - - - - - - - - - - - - - - - - - -
Test Complete. Summary Results:
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-10.00  sec   119 MBytes   100 Mbits/sec  0.000 ms  0/124990 (0%)  sender
[  5]   0.00-10.00  sec   119 MBytes  99.7 Mbits/sec  0.020 ms  306/124990 (0.24%)  receiver
CPU Utilization: local/sender 9.3% (4.6%u/4.7%s), remote/receiver 13.5% (2.4%u/11.0%s)

iperf Done.
```

#### Prueba 4

```
iperf 3.14
Linux hupf-h1 5.15.0-130-generic #140-Ubuntu SMP Wed Dec 18 17:59:53 UTC 2024 x86_64
Control connection MSS 1378
Time: Thu, 06 Mar 2025 09:16:40 UTC
Connecting to host fd00:0:2::2, port 5201
      Cookie: ysazsgdfp2nxy6e64vpslmiyy2mstxrt5inl
      Target Bitrate: 100000000
[  5] local fd00:0:1::1 port 45548 connected to fd00:0:2::2 port 5201
Starting Test: protocol: UDP, 1 streams, 1000 byte blocks, omitting 0 seconds, 10 second test, tos 0
[ ID] Interval           Transfer     Bitrate         Total Datagrams
[  5]   0.00-1.00   sec  11.9 MBytes  99.9 Mbits/sec  12491  
[  5]   1.00-2.00   sec  11.9 MBytes   100 Mbits/sec  12498  
[  5]   2.00-3.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   3.00-4.00   sec  11.9 MBytes   100 Mbits/sec  12501  
[  5]   4.00-5.00   sec  11.9 MBytes   100 Mbits/sec  12499  
[  5]   5.00-6.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   6.00-7.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   7.00-8.00   sec  11.9 MBytes   100 Mbits/sec  12501  
[  5]   8.00-9.00   sec  11.9 MBytes   100 Mbits/sec  12501  
[  5]   9.00-10.00  sec  11.9 MBytes   100 Mbits/sec  12499  
- - - - - - - - - - - - - - - - - - - - - - - - -
Test Complete. Summary Results:
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-10.00  sec   119 MBytes   100 Mbits/sec  0.000 ms  0/124990 (0%)  sender
[  5]   0.00-10.00  sec   119 MBytes   100 Mbits/sec  0.007 ms  5/124990 (0.004%)  receiver
CPU Utilization: local/sender 9.3% (3.1%u/6.2%s), remote/receiver 12.7% (2.0%u/10.6%s)

iperf Done.

```

#### Prueba 5

```
iperf 3.14
Linux hupf-h1 5.15.0-130-generic #140-Ubuntu SMP Wed Dec 18 17:59:53 UTC 2024 x86_64
Control connection MSS 1378
Time: Thu, 06 Mar 2025 09:17:51 UTC
Connecting to host fd00:0:2::2, port 5201
      Cookie: fmgyjcxmb2ofrvfy7wpplcwmo5slsqgurslz
      Target Bitrate: 100000000
[  5] local fd00:0:1::1 port 51533 connected to fd00:0:2::2 port 5201
Starting Test: protocol: UDP, 1 streams, 1000 byte blocks, omitting 0 seconds, 10 second test, tos 0
[ ID] Interval           Transfer     Bitrate         Total Datagrams
[  5]   0.00-1.00   sec  11.9 MBytes  99.9 Mbits/sec  12490  
[  5]   1.00-2.00   sec  11.9 MBytes   100 Mbits/sec  12499  
[  5]   2.00-3.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   3.00-4.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   4.00-5.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   5.00-6.00   sec  11.9 MBytes   100 Mbits/sec  12503  
[  5]   6.00-7.00   sec  11.9 MBytes   100 Mbits/sec  12498  
[  5]   7.00-8.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   8.00-9.00   sec  11.9 MBytes   100 Mbits/sec  12499  
[  5]   9.00-10.00  sec  11.9 MBytes   100 Mbits/sec  12500  
- - - - - - - - - - - - - - - - - - - - - - - - -
Test Complete. Summary Results:
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-10.00  sec   119 MBytes   100 Mbits/sec  0.000 ms  0/124989 (0%)  sender
[  5]   0.00-10.00  sec   119 MBytes   100 Mbits/sec  0.058 ms  0/124989 (0%)  receiver
CPU Utilization: local/sender 9.2% (0.0%u/9.2%s), remote/receiver 14.0% (2.5%u/11.5%s)

iperf Done.

```

#### Prueba 6

```
iperf 3.14
Linux hupf-h1 5.15.0-130-generic #140-Ubuntu SMP Wed Dec 18 17:59:53 UTC 2024 x86_64
Control connection MSS 1378
Time: Thu, 06 Mar 2025 09:19:01 UTC
Connecting to host fd00:0:2::2, port 5201
      Cookie: mc5b7ysbbu65yzwqz3yuutlc2t2wy7fir2wp
      Target Bitrate: 100000000
[  5] local fd00:0:1::1 port 55005 connected to fd00:0:2::2 port 5201
Starting Test: protocol: UDP, 1 streams, 1000 byte blocks, omitting 0 seconds, 10 second test, tos 0
[ ID] Interval           Transfer     Bitrate         Total Datagrams
[  5]   0.00-1.00   sec  11.9 MBytes  99.9 Mbits/sec  12490  
[  5]   1.00-2.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   2.00-3.00   sec  11.9 MBytes   100 Mbits/sec  12501  
[  5]   3.00-4.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   4.00-5.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   5.00-6.00   sec  11.9 MBytes   100 Mbits/sec  12499  
[  5]   6.00-7.00   sec  11.9 MBytes   100 Mbits/sec  12501  
[  5]   7.00-8.00   sec  11.9 MBytes   100 Mbits/sec  12498  
[  5]   8.00-9.00   sec  11.9 MBytes   100 Mbits/sec  12501  
[  5]   9.00-10.00  sec  11.9 MBytes   100 Mbits/sec  12499  
- - - - - - - - - - - - - - - - - - - - - - - - -
Test Complete. Summary Results:
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-10.00  sec   119 MBytes   100 Mbits/sec  0.000 ms  0/124989 (0%)  sender
[  5]   0.00-10.00  sec   119 MBytes   100 Mbits/sec  0.008 ms  0/124989 (0%)  receiver
CPU Utilization: local/sender 9.2% (2.3%u/6.9%s), remote/receiver 12.7% (1.7%u/11.0%s)

```

#### Prueba 7

```
iperf 3.14
Linux hupf-h1 5.15.0-130-generic #140-Ubuntu SMP Wed Dec 18 17:59:53 UTC 2024 x86_64
Control connection MSS 1378
Time: Thu, 06 Mar 2025 09:20:11 UTC
Connecting to host fd00:0:2::2, port 5201
      Cookie: yoti6yu6jx46ohwop6vewafrjtoehjgl6etf
      Target Bitrate: 100000000
[  5] local fd00:0:1::1 port 50789 connected to fd00:0:2::2 port 5201
Starting Test: protocol: UDP, 1 streams, 1000 byte blocks, omitting 0 seconds, 10 second test, tos 0
[ ID] Interval           Transfer     Bitrate         Total Datagrams
[  5]   0.00-1.00   sec  11.9 MBytes  99.9 Mbits/sec  12490  
[  5]   1.00-2.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   2.00-3.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   3.00-4.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   4.00-5.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   5.00-6.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   6.00-7.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   7.00-8.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   8.00-9.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   9.00-10.00  sec  11.9 MBytes   100 Mbits/sec  12500  
- - - - - - - - - - - - - - - - - - - - - - - - -
Test Complete. Summary Results:
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-10.00  sec   119 MBytes   100 Mbits/sec  0.000 ms  0/124990 (0%)  sender
[  5]   0.00-10.00  sec   119 MBytes   100 Mbits/sec  0.015 ms  11/124990 (0.0088%)  receiver
CPU Utilization: local/sender 9.5% (3.2%u/6.3%s), remote/receiver 12.7% (2.0%u/10.7%s)

iperf Done.

```

#### Prueba 8

```
iperf 3.14
Linux hupf-h1 5.15.0-130-generic #140-Ubuntu SMP Wed Dec 18 17:59:53 UTC 2024 x86_64
Control connection MSS 1378
Time: Thu, 06 Mar 2025 09:21:22 UTC
Connecting to host fd00:0:2::2, port 5201
      Cookie: 6lxki45zqjwxwjrjm6x6hi73vmodtesjulda
      Target Bitrate: 100000000
[  5] local fd00:0:1::1 port 44881 connected to fd00:0:2::2 port 5201
Starting Test: protocol: UDP, 1 streams, 1000 byte blocks, omitting 0 seconds, 10 second test, tos 0
[ ID] Interval           Transfer     Bitrate         Total Datagrams
[  5]   0.00-1.00   sec  11.9 MBytes  99.9 Mbits/sec  12491  
[  5]   1.00-2.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   2.00-3.00   sec  11.9 MBytes   100 Mbits/sec  12499  
[  5]   3.00-4.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   4.00-5.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   5.00-6.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   6.00-7.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   7.00-8.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   8.00-9.00   sec  11.9 MBytes   100 Mbits/sec  12501  
[  5]   9.00-10.00  sec  11.9 MBytes   100 Mbits/sec  12500  
- - - - - - - - - - - - - - - - - - - - - - - - -
Test Complete. Summary Results:
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-10.00  sec   119 MBytes   100 Mbits/sec  0.000 ms  0/124991 (0%)  sender
[  5]   0.00-10.00  sec   119 MBytes   100 Mbits/sec  0.021 ms  6/124991 (0.0048%)  receiver
CPU Utilization: local/sender 9.2% (2.3%u/6.9%s), remote/receiver 13.0% (2.2%u/10.8%s)

iperf Done.

```

#### Prueba 9

```
iperf 3.14
Linux hupf-h1 5.15.0-130-generic #140-Ubuntu SMP Wed Dec 18 17:59:53 UTC 2024 x86_64
Control connection MSS 1378
Time: Thu, 06 Mar 2025 09:22:32 UTC
Connecting to host fd00:0:2::2, port 5201
      Cookie: kxzhke3xckxglro3ed4b7fuaihkaywugfdgb
      Target Bitrate: 100000000
[  5] local fd00:0:1::1 port 42818 connected to fd00:0:2::2 port 5201
Starting Test: protocol: UDP, 1 streams, 1000 byte blocks, omitting 0 seconds, 10 second test, tos 0
[ ID] Interval           Transfer     Bitrate         Total Datagrams
[  5]   0.00-1.00   sec  11.9 MBytes  99.9 Mbits/sec  12490  
[  5]   1.00-2.00   sec  11.9 MBytes   100 Mbits/sec  12499  
[  5]   2.00-3.00   sec  11.9 MBytes   100 Mbits/sec  12502  
[  5]   3.00-4.00   sec  11.9 MBytes   100 Mbits/sec  12499  
[  5]   4.00-5.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   5.00-6.00   sec  11.9 MBytes   100 Mbits/sec  12499  
[  5]   6.00-7.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   7.00-8.00   sec  11.9 MBytes   100 Mbits/sec  12502  
[  5]   8.00-9.00   sec  11.9 MBytes   100 Mbits/sec  12498  
[  5]   9.00-10.00  sec  11.9 MBytes   100 Mbits/sec  12501  
- - - - - - - - - - - - - - - - - - - - - - - - -
Test Complete. Summary Results:
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-10.00  sec   119 MBytes   100 Mbits/sec  0.000 ms  0/124990 (0%)  sender
[  5]   0.00-10.00  sec   119 MBytes  99.9 Mbits/sec  0.009 ms  65/124990 (0.052%)  receiver
CPU Utilization: local/sender 9.3% (2.3%u/7.0%s), remote/receiver 12.3% (2.2%u/10.1%s)

iperf Done.
```

#### Prueba 10

```
iperf 3.14
Linux hupf-h1 5.15.0-130-generic #140-Ubuntu SMP Wed Dec 18 17:59:53 UTC 2024 x86_64
Control connection MSS 1378
Time: Thu, 06 Mar 2025 09:23:42 UTC
Connecting to host fd00:0:2::2, port 5201
      Cookie: ctiqxzqazahhjagworqzkbdfjrilhxpytxdb
      Target Bitrate: 100000000
[  5] local fd00:0:1::1 port 54812 connected to fd00:0:2::2 port 5201
Starting Test: protocol: UDP, 1 streams, 1000 byte blocks, omitting 0 seconds, 10 second test, tos 0
[ ID] Interval           Transfer     Bitrate         Total Datagrams
[  5]   0.00-1.00   sec  11.9 MBytes  99.9 Mbits/sec  12489  
[  5]   1.00-2.00   sec  11.9 MBytes   100 Mbits/sec  12501  
[  5]   2.00-3.00   sec  11.9 MBytes   100 Mbits/sec  12499  
[  5]   3.00-4.00   sec  11.9 MBytes   100 Mbits/sec  12501  
[  5]   4.00-5.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   5.00-6.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   6.00-7.00   sec  11.9 MBytes   100 Mbits/sec  12499  
[  5]   7.00-8.00   sec  11.9 MBytes   100 Mbits/sec  12501  
[  5]   8.00-9.00   sec  11.9 MBytes   100 Mbits/sec  12500  
[  5]   9.00-10.00  sec  11.9 MBytes   100 Mbits/sec  12500  
- - - - - - - - - - - - - - - - - - - - - - - - -
Test Complete. Summary Results:
[ ID] Interval           Transfer     Bitrate         Jitter    Lost/Total Datagrams
[  5]   0.00-10.00  sec   119 MBytes   100 Mbits/sec  0.000 ms  0/124990 (0%)  sender
[  5]   0.00-10.00  sec   119 MBytes  99.9 Mbits/sec  0.019 ms  105/124990 (0.084%)  receiver
CPU Utilization: local/sender 9.0% (6.7%u/2.2%s), remote/receiver 12.8% (2.6%u/10.2%s)

iperf Done.

```

## Resutlados router to router

### Resumen de BW

- **Bandwidths:** : [8.77, 9.18, 9.12, 9.08, 9.14, 9.13, 9.19, 9.11, 9.08, 9.14]
- **Bandwidth medio:** 9.094 Gbits/sec
- **Bandwidth mínimo:** 8.77 Gbits/sec
- **Bandwidth máximo:** 9.19 Gbits/sec

### Datos BW

#### Prueba 1

```
------------------------------------------------------------
Client connecting to fcff:2::1, TCP port 5001
TCP window size: 45.0 KByte (default)
------------------------------------------------------------
[  1] local fcf0:0:1:2::1 port 35752 connected with fcff:2::1 port 5001
[ ID] Interval       Transfer     Bandwidth
[  1] 0.0000-10.0096 sec  10.2 GBytes  8.77 Gbits/sec
```

#### Prueba 2

```
iperf
------------------------------------------------------------
Client connecting to fcff:2::1, TCP port 5001
TCP window size: 45.0 KByte (default)
------------------------------------------------------------
[  1] local fcf0:0:1:2::1 port 58728 connected with fcff:2::1 port 5001
[ ID] Interval       Transfer     Bandwidth
[  1] 0.0000-10.0099 sec  10.7 GBytes  9.18 Gbits/sec
```

#### Prueba 3

```
------------------------------------------------------------
Client connecting to fcff:2::1, TCP port 5001
TCP window size: 45.0 KByte (default)
------------------------------------------------------------
[  1] local fcf0:0:1:2::1 port 47750 connected with fcff:2::1 port 5001
[ ID] Interval       Transfer     Bandwidth
[  1] 0.0000-10.0175 sec  10.6 GBytes  9.12 Gbits/sec
```

#### Prueba 4

```
------------------------------------------------------------
Client connecting to fcff:2::1, TCP port 5001
TCP window size: 45.0 KByte (default)
------------------------------------------------------------
[  1] local fcf0:0:1:2::1 port 45430 connected with fcff:2::1 port 5001
[ ID] Interval       Transfer     Bandwidth
[  1] 0.0000-10.0091 sec  10.6 GBytes  9.08 Gbits/sec
```

#### Prueba 5

```
------------------------------------------------------------
Client connecting to fcff:2::1, TCP port 5001
TCP window size: 45.0 KByte (default)
------------------------------------------------------------
[  1] local fcf0:0:1:2::1 port 48560 connected with fcff:2::1 port 5001
[ ID] Interval       Transfer     Bandwidth
[  1] 0.0000-10.0141 sec  10.7 GBytes  9.14 Gbits/sec
```

#### Prueba 6

```
------------------------------------------------------------
Client connecting to fcff:2::1, TCP port 5001
TCP window size: 45.0 KByte (default)
------------------------------------------------------------
[  1] local fcf0:0:1:2::1 port 48970 connected with fcff:2::1 port 5001
[ ID] Interval       Transfer     Bandwidth
[  1] 0.0000-10.0055 sec  10.6 GBytes  9.13 Gbits/sec
```

#### Prueba 7

```
-------------------------------------------------------------
Client connecting to fcff:2::1, TCP port 5001
TCP window size: 45.0 KByte (default)
------------------------------------------------------------
[  1] local fcf0:0:1:2::1 port 51356 connected with fcff:2::1 port 5001
[ ID] Interval       Transfer     Bandwidth
[  1] 0.0000-10.0059 sec  10.7 GBytes  9.19 Gbits/sec
```

#### Prueba 8

```
------------------------------------------------------------
Client connecting to fcff:2::1, TCP port 5001
TCP window size: 45.0 KByte (default)
------------------------------------------------------------
[  1] local fcf0:0:1:2::1 port 42916 connected with fcff:2::1 port 5001
[ ID] Interval       Transfer     Bandwidth
[  1] 0.0000-10.0045 sec  10.6 GBytes  9.11 Gbits/sec
```

#### Prueba 9

```
------------------------------------------------------------
Client connecting to fcff:2::1, TCP port 5001
TCP window size: 45.0 KByte (default)
------------------------------------------------------------
[  1] local fcf0:0:1:2::1 port 42284 connected with fcff:2::1 port 5001
[ ID] Interval       Transfer     Bandwidth
[  1] 0.0000-10.0094 sec  10.6 GBytes  9.08 Gbits/sec
```

#### Prueba 10

```
------------------------------------------------------------
Client connecting to fcff:2::1, TCP port 5001
TCP window size: 45.0 KByte (default)
------------------------------------------------------------
[  1] local fcf0:0:1:2::1 port 48510 connected with fcff:2::1 port 5001
[ ID] Interval       Transfer     Bandwidth
[  1] 0.0000-10.0049 sec  10.6 GBytes  9.14 Gbits/sec

