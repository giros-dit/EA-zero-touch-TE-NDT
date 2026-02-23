#!/bin/bash

while true; do
  pod=$(kubectl get pods --no-headers -o custom-columns=":metadata.name" | grep '^r3' | head -n 1)
  if [ -n "$pod" ]; then
    echo "Deleting pod: $pod"
    kubectl delete pod "$pod"
  else
    echo "No pod starting with 'r3' found."
  fi
  sleep 2
done
