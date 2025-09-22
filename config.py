#!/usr/bin/env python3

import yaml
import sys
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

class Configuration:
    def __init__(self, config_file: Optional[str] = None):
        # Get config file path from environment variable or use default
        self.config_file: str = config_file or os.environ.get('CONFIG_FILE', 'config.yaml')
        
        # Initialize default values
        self.owner: Optional[str] = None
        self.repo_name: Optional[str] = None
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
        
        self._load_config(self.config_file)
        
        # Override with environment variables if set
        self.owner = os.environ.get('REPO_OWNER') or self.owner
        self.repo_name = os.environ.get('REPO_NAME') or self.repo_name
    
    def _load_config(self, config_file: str) -> None:
        """Load configuration from YAML file"""
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                
                # Load repository configuration
                repo_config = config.get('repo', {})
                self.owner = repo_config.get('owner')
                self.repo_name = repo_config.get('name')
                
                # Load output configuration
                output_config = config.get('output', {})
                self.output_dir = output_config.get('directory', '.')
                self.root_md_files_output = output_config.get('root_md_files', 'root_md_files.jsonl')
                self.license_output = output_config.get('license', 'license.jsonl')
                self.releases_output = output_config.get('releases', 'releases.jsonl')
                self.contributors_output = output_config.get('contributors', 'contributors.jsonl')
                self.commits_output = output_config.get('commits', 'commits.jsonl')
                self.issues_output = output_config.get('issues', 'issues.jsonl')
                
                # Load GitHub API configuration
                self.github_api_url = config.get('github_api_url', 'https://api.github.com/graphql')
                self.pagination_limit = config.get('pagination_limit', 100)
                self.date_range_days = config.get('date_range_days', 365)
                self.request_timeout = config.get('request_timeout', 30)
                
        except FileNotFoundError:
            logger.error(f"{config_file} file not found.")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error parsing {config_file}: {e}")
            sys.exit(1)
