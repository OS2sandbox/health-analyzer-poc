mkdir -p .local/raw_data .local/metrics

chmod o+w .local/raw_data .local/metrics

podman run --rm \
  -e GITHUB_TOKEN_FILE=/app/token.txt \
  -v ./.token:/app/token.txt \
  -v $(pwd)/.local/raw_data:/app/output \
  codeberg.org/0xf1e/project-health-analyzer:latest

podman run --rm -it --name duckdb-importer -v "$(pwd)"/.local/raw_data:/raw_data -v "$(pwd)"/.local/metrics:/metrics docker.io/duckdb/duckdb duckdb /metrics/project_health.db -c "
  INSTALL json; 
  LOAD json; 
  CREATE OR REPLACE TABLE commits AS SELECT * FROM read_json_auto('/raw_data/commits.jsonl');
  CREATE OR REPLACE TABLE license AS SELECT * FROM read_json_auto('/raw_data/license.jsonl');
  CREATE OR REPLACE TABLE contributors AS SELECT * FROM read_json_auto('/raw_data/contributors.jsonl');
  CREATE OR REPLACE TABLE releases AS SELECT * FROM read_json_auto('/raw_data/releases.jsonl');
  CREATE OR REPLACE TABLE issues AS SELECT * FROM read_json_auto('/raw_data/issues.jsonl');
  CREATE OR REPLACE TABLE root_md_files AS SELECT * FROM read_json_auto('/raw_data/root_md_files.jsonl');
"
