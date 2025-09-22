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

# GraphQL Queries
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
{
    repository(owner: "%s", name: "%s") {
        releases(last: 100, orderBy: {field: CREATED_AT, direction: DESC}) {
            edges {
                node {
                    name
                    publishedAt
                }
            }
        }
    }
}
'''

CONTRIBUTORS_QUERY = '''
{
    repository(owner: "%s", name: "%s") {
        defaultBranchRef {
            target {
                ... on Commit {
                    history(first: 100) {
                        nodes {
                            author {
                                user {
                                    login
                                }
                            }
                            committedDate
                        }
                    }
                }
            }
        }
    }
}
'''

COMMITS_QUERY = '''
{
    repository(owner: "%s", name: "%s") {
        defaultBranchRef {
            target {
                ... on Commit {
                    history(first: 100) {
                        nodes {
                            messageHeadline
                            committedDate
                            author {
                                name
                            }
                        }
                    }
                }
            }
        }
    }
}
'''

ISSUES_QUERY = '''
{
    repository(owner: "%s", name: "%s") {
        issues(first: 100, states: [OPEN, CLOSED]) {
            nodes {
                title
                state
                author {
                    login
                }
            }
        }
    }
}
'''

def run_query(query: str) -> Optional[Dict[Any, Any]]:
    """Run a GraphQL query and return the response"""
    try:
        response = requests.post(url, headers=headers, json={'query': query})
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Query failed with status code {response.status_code}")
            return None
    except Exception as e:
        print(f"Query failed with exception: {e}")
        return None

def print_root_md_files(md_files: List[str]) -> None:
    """Print the .md files in the root folder as JSON"""
    print(json.dumps({"metric": "root_md_files", "data": md_files}))

def print_license(license_name: str) -> None:
    """Print the repository license name as JSON"""
    print(json.dumps({"metric": "license", "data": license_name}))

def print_releases(releases: List[Dict[str, str]]) -> None:
    """Print all releases with timestamps as JSON"""
    print(json.dumps({"metric": "releases", "data": releases}))

def print_contributors(contributors: Dict[str, str]) -> None:
    """Print all contributors with their most recent contribution date as JSON"""
    print(json.dumps({"metric": "contributors", "data": contributors}))

def print_commits(commits: List[Dict[str, str]]) -> None:
    """Print all commits as JSON"""
    print(json.dumps({"metric": "commits", "data": commits}))

def print_issues(issues: List[Dict[str, str]]) -> None:
    """Print all issues with creator and status as JSON"""
    print(json.dumps({"metric": "issues", "data": issues}))

def check_root_md_files(owner: str, repo_name: str) -> List[str]:
    """Check and return all .md files in the root folder"""
    query = ROOT_FILES_QUERY % (owner, repo_name)
    result = run_query(query)
    
    md_files = []
    if result and 'data' in result and result['data']['repository']['object']:
        entries = result['data']['repository']['object']['entries']
        md_files = [entry['name'] for entry in entries if entry['name'].endswith('.md')]
    print_root_md_files(md_files)
    return md_files

def check_license(owner: str, repo_name: str) -> str:
    """Check and return the repository license name"""
    query = LICENSE_QUERY % (owner, repo_name)
    result = run_query(query)
    
    license_name = 'None'
    if result and 'data' in result:
        license_info = result['data']['repository']['licenseInfo']
        license_name = license_info['name'] if license_info else 'None'
    print_license(license_name)
    return license_name

def check_releases(owner: str, repo_name: str) -> List[Dict[str, str]]:
    """Check and return all releases with timestamps"""
    query = RELEASES_QUERY % (owner, repo_name)
    result = run_query(query)
    
    releases = []
    if result and 'data' in result and result['data']['repository']['releases']:
        release_edges = result['data']['repository']['releases']['edges']
        releases = [
            {
                'name': edge['node']['name'] or 'Unnamed release',
                'publishedAt': edge['node']['publishedAt']
            }
            for edge in release_edges
        ]
    print_releases(releases)
    return releases

def check_contributors(owner: str, repo_name: str) -> Dict[str, str]:
    """Check and return all contributors with their most recent contribution date"""
    query = CONTRIBUTORS_QUERY % (owner, repo_name)
    result = run_query(query)
    
    contributors: Dict[str, str] = {}
    if result and 'data' in result and result['data']['repository']['defaultBranchRef']:
        commits = result['data']['repository']['defaultBranchRef']['target']['history']['nodes']
        for commit in commits:
            if commit['author'] and commit['author']['user']:
                login = commit['author']['user']['login']
                date = commit['committedDate']
                if login not in contributors or date > contributors[login]:
                    contributors[login] = date
    print_contributors(contributors)
    return contributors

def check_commits(owner: str, repo_name: str) -> List[Dict[str, str]]:
    """Check and return all commits"""
    query = COMMITS_QUERY % (owner, repo_name)
    result = run_query(query)
    
    commits = []
    if result and 'data' in result and result['data']['repository']['defaultBranchRef']:
        commit_nodes = result['data']['repository']['defaultBranchRef']['target']['history']['nodes']
        commits = [
            {
                'message': commit['messageHeadline'],
                'date': commit['committedDate'],
                'author': commit['author']['name'] if commit['author'] else 'Unknown'
            }
            for commit in commit_nodes
        ]
    print_commits(commits)
    return commits

def check_issues(owner: str, repo_name: str) -> List[Dict[str, str]]:
    """Check and return all issues with creator and status"""
    query = ISSUES_QUERY % (owner, repo_name)
    result = run_query(query)
    
    issues = []
    if result and 'data' in result and result['data']['repository']['issues']:
        issue_nodes = result['data']['repository']['issues']['nodes']
        issues = [
            {
                'title': issue['title'],
                'state': issue['state'],
                'author': issue['author']['login'] if issue['author'] else 'Unknown'
            }
            for issue in issue_nodes
        ]
    print_issues(issues)
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
