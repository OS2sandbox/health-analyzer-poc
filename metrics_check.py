#!/usr/bin/env python3

import os
import sys
import json
import requests
from datetime import datetime, timedelta

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

def run_query(query):
    """Run a GraphQL query and return the response"""
    response = requests.post(url, headers=headers, json={'query': query})
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Query failed with status code {response.status_code}")
        return None

def main():
    print(f"Checking metrics for repository: {OWNER}/{REPO_NAME}")
    print("=" * 50)
    
    # 1. List all .md files in the root folder
    print("1. Listing all .md files in the root folder...")
    query1 = f'''
    {{
        repository(owner: "{OWNER}", name: "{REPO_NAME}") {{
            object(expression: "HEAD:") {{
                ... on Tree {{
                    entries {{
                        name
                    }}
                }}
            }}
        }}
    }}
    '''
    print(f"   Query: {query1}")
    result1 = run_query(query1)
    print(f"   Raw response: {json.dumps(result1, indent=2)}")
    
    if result1:
        entries = result1['data']['repository']['object']['entries']
        md_files = [entry['name'] for entry in entries if entry['name'].endswith('.md')]
        print("   .md files in root:")
        for file in md_files:
            print(f"     - {file}")
    print()
    
    # 2. Get license name
    print("2. Getting license name...")
    query2 = f'''
    {{
        repository(owner: "{OWNER}", name: "{REPO_NAME}") {{
            licenseInfo {{
                name
            }}
        }}
    }}
    '''
    print(f"   Query: {query2}")
    result2 = run_query(query2)
    print(f"   Raw response: {json.dumps(result2, indent=2)}")
    
    if result2:
        license_info = result2['data']['repository']['licenseInfo']
        license_name = license_info['name'] if license_info else 'None'
        print(f"   License name: {license_name}")
    print()
    
    # 3. List all releases with timestamps
    print("3. Listing all releases with timestamps...")
    query3 = f'''
    {{
        repository(owner: "{OWNER}", name: "{REPO_NAME}") {{
            releases(last: 100, orderBy: {{field: CREATED_AT, direction: DESC}}) {{
                edges {{
                    node {{
                        name
                        publishedAt
                    }}
                }}
            }}
        }}
    }}
    '''
    print(f"   Query: {query3}")
    result3 = run_query(query3)
    print(f"   Raw response: {json.dumps(result3, indent=2)}")
    
    if result3:
        releases = result3['data']['repository']['releases']['edges']
        print("   Releases:")
        for release in releases:
            node = release['node']
            name = node['name'] or 'Unnamed release'
            published_at = node['publishedAt']
            print(f"     - {name}: {published_at}")
    print()
    
    # 4. List all contributors with their most recent contribution date
    print("4. Listing all contributors with their most recent contribution date...")
    query4 = f'''
    {{
        repository(owner: "{OWNER}", name: "{REPO_NAME}") {{
            defaultBranchRef {{
                target {{
                    ... on Commit {{
                        history(first: 100) {{
                            nodes {{
                                author {{
                                    user {{
                                        login
                                    }}
                                }}
                                committedDate
                            }}
                        }}
                    }}
                }}
            }}
        }}
    }}
    '''
    print(f"   Query: {query4}")
    result4 = run_query(query4)
    print(f"   Raw response: {json.dumps(result4, indent=2)}")
    
    if result4:
        commits = result4['data']['repository']['defaultBranchRef']['target']['history']['nodes']
        contributors = {}
        for commit in commits:
            if commit['author'] and commit['author']['user']:
                login = commit['author']['user']['login']
                date = commit['committedDate']
                # Track the latest date for each contributor
                if login not in contributors or date > contributors[login]:
                    contributors[login] = date
        
        print("   Contributors and their most recent contribution:")
        for login, date in contributors.items():
            print(f"     - {login}: {date}")
    print()
    
    # 5. List all commits
    print("5. Listing all commits...")
    query5 = f'''
    {{
        repository(owner: "{OWNER}", name: "{REPO_NAME}") {{
            defaultBranchRef {{
                target {{
                    ... on Commit {{
                        history(first: 100) {{
                            nodes {{
                                messageHeadline
                                committedDate
                                author {{
                                    name
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
    }}
    '''
    print(f"   Query: {query5}")
    result5 = run_query(query5)
    print(f"   Raw response: {json.dumps(result5, indent=2)}")
    
    if result5:
        commits = result5['data']['repository']['defaultBranchRef']['target']['history']['nodes']
        print("   Commits:")
        for commit in commits:
            message = commit['messageHeadline']
            date = commit['committedDate']
            author_name = commit['author']['name'] if commit['author'] else 'Unknown'
            print(f"     - {date}: {author_name} - {message}")
    print()
    
    # 6. List all issues with creator and status
    print("6. Listing all issues with creator and status...")
    query6 = f'''
    {{
        repository(owner: "{OWNER}", name: "{REPO_NAME}") {{
            issues(first: 100, states: [OPEN, CLOSED]) {{
                nodes {{
                    title
                    state
                    author {{
                        login
                    }}
                }}
            }}
        }}
    }}
    '''
    print(f"   Query: {query6}")
    result6 = run_query(query6)
    print(f"   Raw response: {json.dumps(result6, indent=2)}")
    
    if result6:
        issues = result6['data']['repository']['issues']['nodes']
        print("   Issues:")
        for issue in issues:
            title = issue['title']
            state = issue['state']
            author = issue['author']['login'] if issue['author'] else 'Unknown'
            print(f"     - {state}: {author} - {title}")

if __name__ == '__main__':
    main()
