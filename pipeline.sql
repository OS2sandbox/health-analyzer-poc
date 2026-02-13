INSTALL json; 
LOAD json; 
CREATE OR REPLACE TABLE raw_commits AS SELECT * FROM read_json_auto('/raw_data/commits.jsonl');
CREATE OR REPLACE TABLE raw_license AS SELECT * FROM read_json_auto('/raw_data/license.jsonl');
CREATE OR REPLACE TABLE raw_contributors AS SELECT * FROM read_json_auto('/raw_data/contributors.jsonl');
CREATE OR REPLACE TABLE raw_releases AS SELECT * FROM read_json_auto('/raw_data/releases.jsonl');
CREATE OR REPLACE TABLE raw_issues AS SELECT * FROM read_json_auto('/raw_data/issues.jsonl');
CREATE OR REPLACE TABLE raw_root_md_files AS SELECT * FROM read_json_auto('/raw_data/root_md_files.jsonl');
