mkdir -p .local/raw_data .local/metrics

chmod o+w .local/raw_data .local/metrics

podman kube play pipeline.yaml

podman kube down pipeline.yaml
