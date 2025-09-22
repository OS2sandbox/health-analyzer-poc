#!/usr/bin/env python3

import os
import sys
import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

# Check if required environment variables are set
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
OWNER = os.environ.get('OWNER')
REPO_NAME = os.environ.get('REPO_NAME')

if not all([GITHUB_TOKEN, OWNER, REPO_NAME]):
    print("Error: Please set GITHUB_TOKEN, OWNER, and REPO_NAME environment variables.")
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
        response = requests.post(url, headers=headers, json={'query': query, 'variables': variables})
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Query failed with status code {response.status_code}")
            return None
    except Exception as e:
        print(f"Query failed with exception: {e}")
        return None

def write_root_md_files(md_files: List[str]) -> None:
    """Write the .md files in the root folder as JSONL"""
    with open('root_md_files.jsonl', 'w') as f:
        for file in md_files:
            f.write(json.dumps({"file": file}) + '\n')

def write_license(license_name: str) -> None:
    """Write the repository license name as JSONL"""
    with open('license.jsonl', 'w') as f:
        f.write(json.dumps({"license": license_name}) + '\n')

def write_releases(releases: List[Dict[str, str]]) -> None:
    """Write all releases with timestamps as JSONL"""
    with open('releases.jsonl', 'w') as f:
        for release in releases:
            f.write(json.dumps(release) + '\n')

def write_contributors(contributors: Dict[str, str]) -> None:
    """Write all contributors with their most recent contribution date as JSONL"""
    with open('contributors.jsonl', 'w') as f:
        for login, date in contributors.items():
            f.write(json.dumps({"login": login, "last_contribution": date}) + '\n')

def write_commits(commits: List[Dict[str, str]]) -> None:
    """Write all commits as JSONL"""
    with open('commits.jsonl', 'w') as f:
        for commit in commits:
            f.write(json.dumps(commit) + '\n')

def write_issues(issues: List[Dict[str, str]]) -> None:
    """Write all issues with creator and status as JSONL"""
    with open('issues.jsonl', 'w') as f:
        for issue in issues:
            f.write(json.dumps(issue) + '\n')

def check_root_md_files(owner: str, repo_name: str) -> List[str]:
    """Check and return all .md files in the root folder"""
    query = ROOT_FILES_QUERY % (owner, repo_name)
    result = run_query(query)
    
    md_files = []
    if result and 'data' in result and result['data']['repository']['object']:
        entries = result['data']['repository']['object']['entries']
        md_files = [entry['name'] for entry in entries if entry['name'].endswith('.md')]
    write_root_md_files(md_files)
    return md_files

def check_license(owner: str, repo_name: str) -> str:
    """Check and return the repository license name"""
    query = LICENSE_QUERY % (owner, repo_name)
    result = run_query(query)
    
    license_name = 'None'
    if result and 'data' in result:
        license_info = result['data']['repository']['licenseInfo']
        license_name = license_info['name'] if license_info else 'None'
    write_license(license_name)
    return license_name

def check_releases(owner: str, repo_name: str) -> List[Dict[str, str]]:
    """Check and return all releases with timestamps from the past year"""
    releases = []
    has_next_page = True
    cursor = None
    
    while has_next_page:
        query = RELEASES_QUERY % (owner, repo_name)
        variables = {}
        if cursor:
            variables['cursor'] = cursor
            
        result = run_query(query, variables)
        
        if result and 'data' in result and result['data']['repository']['releases']:
            release_edges = result['data']['repository']['releases']['edges']
            
            # Filter releases from the past year
            for edge in release_edges:
                published_at = edge['node']['publishedAt']
                if published_at and published_at >= one_year_ago:
                    releases.append({
                        'name': edge['node']['name'] or 'Unnamed release',
                        'publishedAt': published_at
                    })
                elif published_at and published_at < one_year_ago:
                    # Stop if we've gone past the one-year boundary
                    has_next_page = False
                    break
            
            # Check pagination info
            page_info = result['data']['repository']['releases']['pageInfo']
            has_next_page = page_info['hasNextPage'] and has_next_page
            cursor = page_info['endCursor']
        else:
            has_next_page = False
    
    write_releases(releases)
    return releases

def check_contributors(owner: str, repo_name: str) -> Dict[str, str]:
    """Check and return all contributors with their most recent contribution date from the past year"""
    contributors: Dict[str, str] = {}
    has_next_page = True
    cursor = None
    
    while has_next_page:
        query = CONTRIBUTORS_QUERY % (owner, repo_name)
        variables = {'since': one_year_ago}
        if cursor:
            variables['cursor'] = cursor
            
        result = run_query(query, variables)
        
        if result and 'data' in result and result['data']['repository']['defaultBranchRef']:
            history = result['data']['repository']['defaultBranchRef']['target']['history']
            commits = history['nodes']
            
            for commit in commits:
                if commit['author'] and commit['author']['user']:
                    login = commit['author']['user']['login']
                    date = commit['committedDate']
                    if login not in contributors or date > contributors[login]:
                        contributors[login] = date
            
            # Check pagination info
            page_info = history['pageInfo']
            has_next_page = page_info['hasNextPage']
            cursor = page_info['endCursor']
        else:
            has_next_page = False
    
    write_contributors(contributors)
    return contributors

def check_commits(owner: str, repo_name: str) -> List[Dict[str, str]]:
    """Check and return all commits from the past year"""
    commits = []
    has_next_page = True
    cursor = None
    
    while has_next_page:
        query = COMMITS_QUERY % (owner, repo_name)
        variables = {'since': one_year_ago}
        if cursor:
            variables['cursor'] = cursor
            
        result = run_query(query, variables)
        
        if result and 'data' in result and result['data']['repository']['defaultBranchRef']:
            history = result['data']['repository']['defaultBranchRef']['target']['history']
            commit_nodes = history['nodes']
            
            for commit in commit_nodes:
                commits.append({
                    'message': commit['messageHeadline'],
                    'date': commit['committedDate'],
                    'author': commit['author']['name'] if commit['author'] else 'Unknown'
                })
            
            # Check pagination info
            page_info = history['pageInfo']
            has_next_page = page_info['hasNextPage']
            cursor = page_info['endCursor']
        else:
            has_next_page = False
    
    write_commits(commits)
    return commits

def check_issues(owner: str, repo_name: str) -> List[Dict[str, str]]:
    """Check and return all issues with creator and status from the past year"""
    issues = []
    has_next_page = True
    cursor = None
    
    while has_next_page:
        query = ISSUES_QUERY % (owner, repo_name)
        variables = {}
        if cursor:
            variables['cursor'] = cursor
            
        result = run_query(query, variables)
        
        if result and 'data' in result and result['data']['repository']['issues']:
            issue_nodes = result['data']['repository']['issues']['nodes']
            
            # Filter issues from the past year
            for issue in issue_nodes:
                created_at = issue['createdAt']
                if created_at and created_at >= one_year_ago:
                    issues.append({
                        'title': issue['title'],
                        'state': issue['state'],
                        'author': issue['author']['login'] if issue['author'] else 'Unknown',
                        'createdAt': created_at
                    })
                elif created_at and created_at < one_year_ago:
                    # Stop if we've gone past the one-year boundary
                    has_next_page = False
                    break
            
            # Check pagination info
            page_info = result['data']['repository']['issues']['pageInfo']
            has_next_page = page_info['hasNextPage'] and has_next_page
            cursor = page_info['endCursor']
        else:
            has_next_page = False
    
    write_issues(issues)
    return issues

def main() -> None:
    check_root_md_files(OWNER, REPO_NAME)
    check_license(OWNER, REPO_NAME)
    check_releases(OWNER, REPO_NAME)
    check_contributors(OWNER, REPO_NAME)
    check_commits(OWNER, REPO_NAME)
    check_issues(OWNER, REPO_NAME)

if __name__ == '__main__':
    main()
