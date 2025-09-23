mkdir -p .local/raw_data .local/metrics

chmod o+w .local/raw_data .local/metrics

podman run --rm \
  -e GITHUB_TOKEN_FILE=/app/token.txt \
  -v ./.token:/app/token.txt \
  -v $(pwd)/.local/raw_data:/app/output \
  codeberg.org/0xf1e/project-health-analyzer:latest

podman run --rm -it --name duckdb-importer -v "$(pwd)"/.local/raw_data:/raw_data -v "$(pwd)"/.local/metrics:/metrics docker.io/duckdb/duckdb duckdb /metrics/project_health.db -c "INSTALL json; LOAD json; CREATE OR REPLACE TABLE commits AS SELECT * FROM read_json_auto('/raw_data/commits.jsonl');"
