#!/usr/bin/env python3

import json
import logging
import os
from typing import Dict, List
from config import Configuration

logger = logging.getLogger(__name__)

class FileWriter:
    def __init__(self, config: Configuration):
        self.config = config
    
    def _get_output_path(self, filename: str) -> str:
        """Get full path for output file"""
        return os.path.join(self.config.output_dir, filename)

    def write_root_md_files(self, md_files: List[str]) -> None:
        """Write the .md files in the root folder as JSONL"""
        output_file = self._get_output_path(self.config.root_md_files_output)
        logger.info(f"Writing {len(md_files)} .md files to {output_file}")
        with open(output_file, 'w') as f:
            for file in md_files:
                f.write(json.dumps({"file": file}) + '\n')

    def write_license(self, license_name: str) -> None:
        """Write the repository license name as JSONL"""
        output_file = self._get_output_path(self.config.license_output)
        logger.info(f"Writing license to {output_file}: {license_name}")
        with open(output_file, 'w') as f:
            f.write(json.dumps({"license": license_name}) + '\n')

    def write_releases(self, releases: List[Dict[str, str]]) -> None:
        """Write all releases with timestamps as JSONL"""
        output_file = self._get_output_path(self.config.releases_output)
        logger.info(f"Writing {len(releases)} releases to {output_file}")
        with open(output_file, 'w') as f:
            for release in releases:
                f.write(json.dumps(release) + '\n')

    def write_contributors(self, contributors: Dict[str, str]) -> None:
        """Write all contributors with their most recent contribution date as JSONL"""
        output_file = self._get_output_path(self.config.contributors_output)
        logger.info(f"Writing {len(contributors)} contributors to {output_file}")
        with open(output_file, 'w') as f:
            for login, date in contributors.items():
                f.write(json.dumps({"login": login, "last_contribution": date}) + '\n')

    def write_commits(self, commits: List[Dict[str, str]]) -> None:
        """Write all commits as JSONL"""
        output_file = self._get_output_path(self.config.commits_output)
        logger.info(f"Writing {len(commits)} commits to {output_file}")
        with open(output_file, 'w') as f:
            for commit in commits:
                f.write(json.dumps(commit) + '\n')

    def write_issues(self, issues: List[Dict[str, str]]) -> None:
        """Write all issues with creator and status as JSONL"""
        output_file = self._get_output_path(self.config.issues_output)
        logger.info(f"Writing {len(issues)} issues to {output_file}")
        with open(output_file, 'w') as f:
            for issue in issues:
                f.write(json.dumps(issue) + '\n')
