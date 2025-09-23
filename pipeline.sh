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
  CREATE OR REPLACE TABLE raw_commits AS SELECT * FROM read_json_auto('/raw_data/commits.jsonl');
  CREATE OR REPLACE TABLE raw_license AS SELECT * FROM read_json_auto('/raw_data/license.jsonl');
  CREATE OR REPLACE TABLE raw_contributors AS SELECT * FROM read_json_auto('/raw_data/contributors.jsonl');
  CREATE OR REPLACE TABLE raw_releases AS SELECT * FROM read_json_auto('/raw_data/releases.jsonl');
  CREATE OR REPLACE TABLE raw_issues AS SELECT * FROM read_json_auto('/raw_data/issues.jsonl');
  CREATE OR REPLACE TABLE raw_root_md_files AS SELECT * FROM read_json_auto('/raw_data/root_md_files.jsonl');
"
