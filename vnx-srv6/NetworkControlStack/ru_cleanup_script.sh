kubectl exec -it $(kubectl get pod -o name | grep ^pod/ru) -c ru -- \
  bash -c "ip -6 route | grep '^fd00:0:2::' | while read -r line; do ip -6 route del \$line; done"
kubectl delete pod $(kubectl get pod -o name | grep ^pod/ru | cut -d/ -f2)
