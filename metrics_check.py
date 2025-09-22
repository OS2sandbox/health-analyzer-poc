#!/usr/bin/env python3

import sys
import logging
from datetime import datetime
from github_client import GitHubClient
from metrics_processor import MetricsProcessor
from file_writer import FileWriter
from config import Configuration

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def main() -> None:
    logger.info("Starting metrics check")
    start_time = datetime.now()
    
    try:
        # Initialize components
        config = Configuration()
        github_client = GitHubClient(config)
        metrics_processor = MetricsProcessor(github_client, config)
        file_writer = FileWriter(config)
        
        owner = config.owner
        repo_name = config.repo_name
        
        logger.info(f"Processing repository: {owner}/{repo_name}")
        
        # Process each metric
        md_files = metrics_processor.get_root_md_files(owner, repo_name)
        file_writer.write_root_md_files(md_files)
        
        license_name = metrics_processor.get_license(owner, repo_name)
        file_writer.write_license(license_name)
        
        releases = metrics_processor.get_releases(owner, repo_name)
        file_writer.write_releases(releases)
        
        contributors = metrics_processor.get_contributors(owner, repo_name)
        file_writer.write_contributors(contributors)
        
        commits = metrics_processor.get_commits(owner, repo_name)
        file_writer.write_commits(commits)
        
        issues = metrics_processor.get_issues(owner, repo_name)
        file_writer.write_issues(issues)
        
        end_time = datetime.now()
        duration = end_time - start_time
        logger.info(f"Metrics check completed in {duration.total_seconds():.2f} seconds")
        
    except Exception as e:
        logger.error(f"Application failed: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
