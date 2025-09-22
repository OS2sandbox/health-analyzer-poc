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

def check_root_md_files(owner: str, repo_name: str) -> None:
    """Check and display all .md files in the root folder"""
    print("1. Listing all .md files in the root folder...")
    query = ROOT_FILES_QUERY % (owner, repo_name)
    result = run_query(query)
    
    if result and 'data' in result and result['data']['repository']['object']:
        entries = result['data']['repository']['object']['entries']
        md_files = [entry['name'] for entry in entries if entry['name'].endswith('.md')]
        print("   .md files in root:")
        for file in md_files:
            print(f"     - {file}")
    else:
        print("   No .md files found or error occurred")
    print()

def check_license(owner: str, repo_name: str) -> None:
    """Check and display the repository license name"""
    print("2. Getting license name...")
    query = LICENSE_QUERY % (owner, repo_name)
    result = run_query(query)
    
    if result and 'data' in result:
        license_info = result['data']['repository']['licenseInfo']
        license_name = license_info['name'] if license_info else 'None'
        print(f"   License name: {license_name}")
    else:
        print("   Error retrieving license information")
    print()

def check_releases(owner: str, repo_name: str) -> None:
    """Check and display all releases with timestamps"""
    print("3. Listing all releases with timestamps...")
    query = RELEASES_QUERY % (owner, repo_name)
    result = run_query(query)
    
    if result and 'data' in result and result['data']['repository']['releases']:
        releases = result['data']['repository']['releases']['edges']
        print("   Releases:")
        for release in releases:
            node = release['node']
            name = node['name'] or 'Unnamed release'
            published_at = node['publishedAt']
            print(f"     - {name}: {published_at}")
    else:
        print("   No releases found or error occurred")
    print()

def check_contributors(owner: str, repo_name: str) -> None:
    """Check and display all contributors with their most recent contribution date"""
    print("4. Listing all contributors with their most recent contribution date...")
    query = CONTRIBUTORS_QUERY % (owner, repo_name)
    result = run_query(query)
    
    if result and 'data' in result and result['data']['repository']['defaultBranchRef']:
        commits = result['data']['repository']['defaultBranchRef']['target']['history']['nodes']
        contributors: Dict[str, str] = {}
        for commit in commits:
            if commit['author'] and commit['author']['user']:
                login = commit['author']['user']['login']
                date = commit['committedDate']
                if login not in contributors or date > contributors[login]:
                    contributors[login] = date
        
        print("   Contributors and their most recent contribution:")
        for login, date in contributors.items():
            print(f"     - {login}: {date}")
    else:
        print("   No contributors found or error occurred")
    print()

def check_commits(owner: str, repo_name: str) -> None:
    """Check and display all commits"""
    print("5. Listing all commits...")
    query = COMMITS_QUERY % (owner, repo_name)
    result = run_query(query)
    
    if result and 'data' in result and result['data']['repository']['defaultBranchRef']:
        commits = result['data']['repository']['defaultBranchRef']['target']['history']['nodes']
        print("   Commits:")
        for commit in commits:
            message = commit['messageHeadline']
            date = commit['committedDate']
            author_name = commit['author']['name'] if commit['author'] else 'Unknown'
            print(f"     - {date}: {author_name} - {message}")
    else:
        print("   No commits found or error occurred")
    print()

def check_issues(owner: str, repo_name: str) -> None:
    """Check and display all issues with creator and status"""
    print("6. Listing all issues with creator and status...")
    query = ISSUES_QUERY % (owner, repo_name)
    result = run_query(query)
    
    if result and 'data' in result and result['data']['repository']['issues']:
        issues = result['data']['repository']['issues']['nodes']
        print("   Issues:")
        for issue in issues:
            title = issue['title']
            state = issue['state']
            author = issue['author']['login'] if issue['author'] else 'Unknown'
            print(f"     - {state}: {author} - {title}")
    else:
        print("   No issues found or error occurred")
    print()

def main() -> None:
    print(f"Checking metrics for repository: {OWNER}/{REPO_NAME}")
    print("=" * 50)
    
    check_root_md_files(OWNER, REPO_NAME)
    check_license(OWNER, REPO_NAME)
    check_releases(OWNER, REPO_NAME)
    check_contributors(OWNER, REPO_NAME)
    check_commits(OWNER, REPO_NAME)
    check_issues(OWNER, REPO_NAME)

if __name__ == '__main__':
    main()
