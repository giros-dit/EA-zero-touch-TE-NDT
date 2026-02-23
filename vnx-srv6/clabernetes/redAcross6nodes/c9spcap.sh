#!/bin/sh

kubectl exec -n across-tc32 -i deploy/$1 -- docker exec -i $1 tcpdump -U -nni $2 -w - | wireshark -k -i -

