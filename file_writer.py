#!/usr/bin/env python3

import json
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class FileWriter:
    def write_root_md_files(self, md_files: List[str]) -> None:
        """Write the .md files in the root folder as JSONL"""
        logger.info(f"Writing {len(md_files)} .md files to root_md_files.jsonl")
        with open('root_md_files.jsonl', 'w') as f:
            for file in md_files:
                f.write(json.dumps({"file": file}) + '\n')

    def write_license(self, license_name: str) -> None:
        """Write the repository license name as JSONL"""
        logger.info(f"Writing license to license.jsonl: {license_name}")
        with open('license.jsonl', 'w') as f:
            f.write(json.dumps({"license": license_name}) + '\n')

    def write_releases(self, releases: List[Dict[str, str]]) -> None:
        """Write all releases with timestamps as JSONL"""
        logger.info(f"Writing {len(releases)} releases to releases.jsonl")
        with open('releases.jsonl', 'w') as f:
            for release in releases:
                f.write(json.dumps(release) + '\n')

    def write_contributors(self, contributors: Dict[str, str]) -> None:
        """Write all contributors with their most recent contribution date as JSONL"""
        logger.info(f"Writing {len(contributors)} contributors to contributors.jsonl")
        with open('contributors.jsonl', 'w') as f:
            for login, date in contributors.items():
                f.write(json.dumps({"login": login, "last_contribution": date}) + '\n')

    def write_commits(self, commits: List[Dict[str, str]]) -> None:
        """Write all commits as JSONL"""
        logger.info(f"Writing {len(commits)} commits to commits.jsonl")
        with open('commits.jsonl', 'w') as f:
            for commit in commits:
                f.write(json.dumps(commit) + '\n')

    def write_issues(self, issues: List[Dict[str, str]]) -> None:
        """Write all issues with creator and status as JSONL"""
        logger.info(f"Writing {len(issues)} issues to issues.jsonl")
        with open('issues.jsonl', 'w') as f:
            for issue in issues:
                f.write(json.dumps(issue) + '\n')
