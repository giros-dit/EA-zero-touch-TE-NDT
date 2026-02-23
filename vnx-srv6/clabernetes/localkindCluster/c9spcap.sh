#!/bin/sh

kubectl exec -n $1 -it $2 -- tcpdump -U -nni $3 -w - | wireshark -k -i -