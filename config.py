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
        self._load_config(config_file)
    
    def _load_config(self, config_file: str) -> None:
        """Load configuration from YAML file"""
        try:
            with open(config_file, 'r') as f:
                config = yaml.safe_load(f)
                self.owner = config.get('owner')
                self.repo_name = config.get('repo_name')
                
            if not self.owner or not self.repo_name:
                logger.error("Please ensure config.yaml contains 'owner' and 'repo_name' keys.")
                sys.exit(1)
                
        except FileNotFoundError:
            logger.error(f"{config_file} file not found.")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Error parsing {config_file}: {e}")
            sys.exit(1)
