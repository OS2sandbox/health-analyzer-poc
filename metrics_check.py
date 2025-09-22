#!/usr/bin/env python3

import os
import sys
import json
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Check if required environment variables are set
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
OWNER = os.environ.get('OWNER')
REPO_NAME = os.environ.get('REPO_NAME')

if not all([GITHUB_TOKEN, OWNER, REPO_NAME]):
    logger.error("Please set GITHUB_TOKEN, OWNER, and REPO_NAME environment variables.")
    sys.exit(1)

# Headers for GraphQL API
headers = {
    'Authorization': f'bearer {GITHUB_TOKEN}',
    'Content-Type': 'application/json'
}

# GraphQL endpoint
url = 'https://api.github.com/graphql'

# Calculate the date for one year ago
one_year_ago = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%dT%H:%M:%SZ')

# GraphQL Queries with pagination and date filtering
ROOT_FILES_QUERY = '''
{
    repository(owner: "%s", name: "%s") {
        object(expression: "HEAD:") {
            ... on Tree {
                entries {
                    name
                }
            }
        }
    }
}
'''

LICENSE_QUERY = '''
{
    repository(owner: "%s", name: "%s") {
        licenseInfo {
            name
        }
    }
}
'''

RELEASES_QUERY = '''
query($cursor: String) {
    repository(owner: "%s", name: "%s") {
        releases(first: 100, orderBy: {field: CREATED_AT, direction: DESC}, after: $cursor) {
            edges {
                node {
                    name
                    publishedAt
                }
                cursor
            }
            pageInfo {
                hasNextPage
                endCursor
            }
        }
    }
}
'''

CONTRIBUTORS_QUERY = '''
query($cursor: String, $since: GitTimestamp!) {
    repository(owner: "%s", name: "%s") {
        defaultBranchRef {
            target {
                ... on Commit {
                    history(first: 100, since: $since, after: $cursor) {
                        nodes {
                            author {
                                user {
                                    login
                                }
                            }
                            committedDate
                        }
                        pageInfo {
                            hasNextPage
                            endCursor
                        }
                    }
                }
            }
        }
    }
}
'''

COMMITS_QUERY = '''
query($cursor: String, $since: GitTimestamp!) {
    repository(owner: "%s", name: "%s") {
        defaultBranchRef {
            target {
                ... on Commit {
                    history(first: 100, since: $since, after: $cursor) {
                        nodes {
                            messageHeadline
                            committedDate
                            author {
                                name
                            }
                        }
                        pageInfo {
                            hasNextPage
                            endCursor
                        }
                    }
                }
            }
        }
    }
}
'''

ISSUES_QUERY = '''
query($cursor: String) {
    repository(owner: "%s", name: "%s") {
        issues(first: 100, states: [OPEN, CLOSED], after: $cursor, orderBy: {field: CREATED_AT, direction: DESC}) {
            nodes {
                title
                state
                author {
                    login
                }
                createdAt
            }
            pageInfo {
                hasNextPage
                endCursor
            }
        }
    }
}
'''

def run_query(query: str, variables: Dict = {}) -> Optional[Dict[Any, Any]]:
    """Run a GraphQL query with variables and return the response"""
    try:
        logger.debug(f"Running query with variables: {variables}")
        response = requests.post(url, headers=headers, json={'query': query, 'variables': variables})
        if response.status_code == 200:
            logger.debug("Query successful")
            return response.json()
        else:
            logger.error(f"Query failed with status code {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Query failed with exception: {e}")
        return None

def paginate_github_query(
    query: str, 
    extract_function: Callable[[Dict], Tuple[List[Any], Optional[Dict]]], 
    initial_variables: Optional[Dict] = None
) -> List[Any]:
    """Generic pagination function for GitHub GraphQL API"""
    if initial_variables is None:
        initial_variables = {}
        
    all_data = []
    has_next_page = True
    cursor = None
    variables = initial_variables.copy()
    
    page_count = 0
    while has_next_page:
        page_count += 1
        logger.info(f"Fetching page {page_count}...")
        
        if cursor:
            variables['cursor'] = cursor
        else:
            # Remove cursor from variables if it's None
            variables.pop('cursor', None)
            
        result = run_query(query, variables)
        
        if not result:
            logger.warning("Query returned no result, stopping pagination")
            break
            
        data_batch, page_info = extract_function(result)
        all_data.extend(data_batch)
        
        logger.debug(f"Retrieved {len(data_batch)} items in this batch")
        
        if page_info and page_info.get('hasNextPage'):
            cursor = page_info.get('endCursor')
            logger.debug(f"Next cursor: {cursor}")
        else:
            has_next_page = False
    
    logger.info(f"Pagination complete. Total pages: {page_count}, Total items: {len(all_data)}")
    return all_data

def write_root_md_files(md_files: List[str]) -> None:
    """Write the .md files in the root folder as JSONL"""
    logger.info(f"Writing {len(md_files)} .md files to root_md_files.jsonl")
    with open('root_md_files.jsonl', 'w') as f:
        for file in md_files:
            f.write(json.dumps({"file": file}) + '\n')

def write_license(license_name: str) -> None:
    """Write the repository license name as JSONL"""
    logger.info(f"Writing license to license.jsonl: {license_name}")
    with open('license.jsonl', 'w') as f:
        f.write(json.dumps({"license": license_name}) + '\n')

def write_releases(releases: List[Dict[str, str]]) -> None:
    """Write all releases with timestamps as JSONL"""
    logger.info(f"Writing {len(releases)} releases to releases.jsonl")
    with open('releases.jsonl', 'w') as f:
        for release in releases:
            f.write(json.dumps(release) + '\n')

def write_contributors(contributors: Dict[str, str]) -> None:
    """Write all contributors with their most recent contribution date as JSONL"""
    logger.info(f"Writing {len(contributors)} contributors to contributors.jsonl")
    with open('contributors.jsonl', 'w') as f:
        for login, date in contributors.items():
            f.write(json.dumps({"login": login, "last_contribution": date}) + '\n')

def write_commits(commits: List[Dict[str, str]]) -> None:
    """Write all commits as JSONL"""
    logger.info(f"Writing {len(commits)} commits to commits.jsonl")
    with open('commits.jsonl', 'w') as f:
        for commit in commits:
            f.write(json.dumps(commit) + '\n')

def write_issues(issues: List[Dict[str, str]]) -> None:
    """Write all issues with creator and status as JSONL"""
    logger.info(f"Writing {len(issues)} issues to issues.jsonl")
    with open('issues.jsonl', 'w') as f:
        for issue in issues:
            f.write(json.dumps(issue) + '\n')

def check_root_md_files(owner: str, repo_name: str) -> List[str]:
    """Check and return all .md files in the root folder"""
    logger.info("Checking root .md files...")
    query = ROOT_FILES_QUERY % (owner, repo_name)
    result = run_query(query)
    
    md_files = []
    if result and 'data' in result and result['data']['repository']['object']:
        entries = result['data']['repository']['object']['entries']
        md_files = [entry['name'] for entry in entries if entry['name'].endswith('.md')]
        logger.info(f"Found {len(md_files)} .md files in root")
    else:
        logger.warning("No .md files found or error occurred")
    write_root_md_files(md_files)
    return md_files

def check_license(owner: str, repo_name: str) -> str:
    """Check and return the repository license name"""
    logger.info("Checking license...")
    query = LICENSE_QUERY % (owner, repo_name)
    result = run_query(query)
    
    license_name = 'None'
    if result and 'data' in result:
        license_info = result['data']['repository']['licenseInfo']
        license_name = license_info['name'] if license_info else 'None'
        logger.info(f"License found: {license_name}")
    else:
        logger.warning("Error retrieving license information")
    write_license(license_name)
    return license_name

def check_releases(owner: str, repo_name: str) -> List[Dict[str, str]]:
    """Check and return all releases with timestamps from the past year"""
    logger.info("Checking releases...")
    def extract_releases(result: Dict) -> Tuple[List[Dict[str, str]], Optional[Dict]]:
        releases = []
        page_info = None
        
        if 'data' in result and result['data']['repository']:
            repo_data = result['data']['repository']
            if repo_data.get('releases'):
                release_edges = repo_data['releases']['edges']
                page_info = repo_data['releases']['pageInfo']
                
                # Filter releases from the past year
                for edge in release_edges:
                    published_at = edge['node']['publishedAt']
                    if published_at and published_at >= one_year_ago:
                        releases.append({
                            'name': edge['node']['name'] or 'Unnamed release',
                            'publishedAt': published_at
                        })
                    elif published_at and published_at < one_year_ago:
                        # Stop pagination if we've gone past the one-year boundary
                        logger.debug("Reached releases older than one year, stopping pagination")
                        return releases, None
                        
        return releases, page_info
    
    query = RELEASES_QUERY % (owner, repo_name)
    releases = paginate_github_query(query, extract_releases)
    logger.info(f"Found {len(releases)} releases in the past year")
    write_releases(releases)
    return releases

def check_contributors(owner: str, repo_name: str) -> Dict[str, str]:
    """Check and return all contributors with their most recent contribution date from the past year"""
    logger.info("Checking contributors...")
    def extract_contributors(result: Dict) -> Tuple[List[Dict[str, str]], Optional[Dict]]:
        contributors: Dict[str, str] = {}
        page_info = None
        
        if 'data' in result and result['data']['repository']:
            repo_data = result['data']['repository']
            if repo_data.get('defaultBranchRef') and repo_data['defaultBranchRef'].get('target'):
                target = repo_data['defaultBranchRef']['target']
                if target.get('history'):
                    history = target['history']
                    commit_nodes = history['nodes']
                    page_info = history['pageInfo']
                    
                    for commit in commit_nodes:
                        if commit.get('author') and commit['author'].get('user'):
                            login = commit['author']['user']['login']
                            date = commit['committedDate']
                            if login and date:
                                if login not in contributors or date > contributors[login]:
                                    contributors[login] = date
                                    
        return [contributors], page_info
    
    query = CONTRIBUTORS_QUERY % (owner, repo_name)
    contributor_list = paginate_github_query(query, extract_contributors, {'since': one_year_ago})
    
    # Merge all contributor dictionaries
    final_contributors: Dict[str, str] = {}
    for contributors in contributor_list:
        for login, date in contributors.items():
            if login not in final_contributors or date > final_contributors[login]:
                final_contributors[login] = date
                
    logger.info(f"Found {len(final_contributors)} contributors in the past year")
    write_contributors(final_contributors)
    return final_contributors

def check_commits(owner: str, repo_name: str) -> List[Dict[str, str]]:
    """Check and return all commits from the past year"""
    logger.info("Checking commits...")
    def extract_commits(result: Dict) -> Tuple[List[Dict[str, str]], Optional[Dict]]:
        commits = []
        page_info = None
        
        if 'data' in result and result['data']['repository']:
            repo_data = result['data']['repository']
            if repo_data.get('defaultBranchRef') and repo_data['defaultBranchRef'].get('target'):
                target = repo_data['defaultBranchRef']['target']
                if target.get('history'):
                    history = target['history']
                    commit_nodes = history['nodes']
                    page_info = history['pageInfo']
                    
                    for commit in commit_nodes:
                        commits.append({
                            'message': commit.get('messageHeadline', ''),
                            'date': commit.get('committedDate', ''),
                            'author': commit.get('author', {}).get('name', 'Unknown') if commit.get('author') else 'Unknown'
                        })
                        
        return commits, page_info
    
    query = COMMITS_QUERY % (owner, repo_name)
    commits = paginate_github_query(query, extract_commits, {'since': one_year_ago})
    logger.info(f"Found {len(commits)} commits in the past year")
    write_commits(commits)
    return commits

def check_issues(owner: str, repo_name: str) -> List[Dict[str, str]]:
    """Check and return all issues with creator and status from the past year"""
    logger.info("Checking issues...")
    def extract_issues(result: Dict) -> Tuple[List[Dict[str, str]], Optional[Dict]]:
        issues = []
        page_info = None
        
        if 'data' in result and result['data']['repository']:
            repo_data = result['data']['repository']
            if repo_data.get('issues'):
                issue_nodes = repo_data['issues']['nodes']
                page_info = repo_data['issues']['pageInfo']
                
                # Filter issues from the past year
                for issue in issue_nodes:
                    created_at = issue.get('createdAt')
                    if created_at and created_at >= one_year_ago:
                        issues.append({
                            'title': issue.get('title', ''),
                            'state': issue.get('state', ''),
                            'author': issue.get('author', {}).get('login', 'Unknown') if issue.get('author') else 'Unknown',
                            'createdAt': created_at
                        })
                    elif created_at and created_at < one_year_ago:
                        # Stop pagination if we've gone past the one-year boundary
                        logger.debug("Reached issues older than one year, stopping pagination")
                        return issues, None
                        
        return issues, page_info
    
    query = ISSUES_QUERY % (owner, repo_name)
    issues = paginate_github_query(query, extract_issues)
    logger.info(f"Found {len(issues)} issues in the past year")
    write_issues(issues)
    return issues

def main() -> None:
    logger.info(f"Starting metrics check for repository: {OWNER}/{REPO_NAME}")
    start_time = datetime.now()
    
    check_root_md_files(OWNER, REPO_NAME)
    check_license(OWNER, REPO_NAME)
    check_releases(OWNER, REPO_NAME)
    check_contributors(OWNER, REPO_NAME)
    check_commits(OWNER, REPO_NAME)
    check_issues(OWNER, REPO_NAME)
    
    end_time = datetime.now()
    duration = end_time - start_time
    logger.info(f"Metrics check completed in {duration.total_seconds():.2f} seconds")

if __name__ == '__main__':
    main()
