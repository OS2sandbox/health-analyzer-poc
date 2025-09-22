#!/usr/bin/env python3

import yaml
import sys
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class Configuration:
    def __init__(self, config_file: str = 'config.yaml'):
        self.owner: Optional[str] = None
        self.repo_name: Optional[str] = None
        self.config_file: str = config_file
        self.output_dir: str = '.'
        self.root_md_files_output: str = 'root_md_files.jsonl'
        self.license_output: str = 'license.jsonl'
        self.releases_output: str = 'releases.jsonl'
        self.contributors_output: str = 'contributors.jsonl'
        self.commits_output: str = 'commits.jsonl'
        self.issues_output: str = 'issues.jsonl'
        
        # GitHub API configuration
        self.github_api_url: str = 'https://api.github.com/graphql'
        self.pagination_limit: int = 100
        self.date_range_days: int = 365
        self.request_timeout: int = 30
        
        self._load_config(config_file)
    
    def _load_config(self, config_file: str) -> None:
        """Load configuration from YAML file"""
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                self.owner = config.get('owner')
                self.repo_name = config.get('repo_name')
                self.output_dir = config.get('output_dir', '.')
                self.root_md_files_output = config.get('root_md_files_output', 'root_md_files.jsonl')
                self.license_output = config.get('license_output', 'license.jsonl')
                self.releases_output = config.get('releases_output', 'releases.jsonl')
                self.contributors_output = config.get('contributors_output', 'contributors.jsonl')
                self.commits_output = config.get('commits_output', 'commits.jsonl')
                self.issues_output = config.get('issues_output', 'issues.jsonl')
                
                # GitHub API configuration
                self.github_api_url = config.get('github_api_url', 'https://api.github.com/graphql')
                self.pagination_limit = config.get('pagination_limit', 100)
                self.date_range_days = config.get('date_range_days', 365)
                self.request_timeout = config.get('request_timeout', 30)
                
            if not self.owner or not self.repo_name:
                logger.error("Please ensure config.yaml contains 'owner' and 'repo_name' keys.")
                sys.exit(1)
                
        except FileNotFoundError:
            logger.error(f"{config_file} file not found.")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error parsing {config_file}: {e}")
            sys.exit(1)
