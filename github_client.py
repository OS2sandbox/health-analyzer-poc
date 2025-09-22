#!/usr/bin/env python3

import os
import sys
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any

logger = logging.getLogger(__name__)

class GitHubClient:
    def __init__(self):
        # Check if required environment variables are set
        self.github_token = os.environ.get('GITHUB_TOKEN')
        self.owner = os.environ.get('OWNER')
        self.repo_name = os.environ.get('REPO_NAME')
        
        if not all([self.github_token, self.owner, self.repo_name]):
            logger.error("Please set GITHUB_TOKEN, OWNER, and REPO_NAME environment variables.")
            sys.exit(1)
        
        # Headers for GraphQL API
        self.headers = {
            'Authorization': f'bearer {self.github_token}',
            'Content-Type': 'application/json'
        }
        
        # GraphQL endpoint
        self.url = 'https://api.github.com/graphql'
        
        # Calculate the date for one year ago
        self.one_year_ago = (datetime.now() - timedelta(days=365)).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # GraphQL Queries
        self.ROOT_FILES_QUERY = '''
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
        
        self.LICENSE_QUERY = '''
        {
            repository(owner: "%s", name: "%s") {
                licenseInfo {
                    name
                }
            }
        }
        '''
        
        self.RELEASES_QUERY = '''
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
        
        self.CONTRIBUTORS_QUERY = '''
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
        
        self.COMMITS_QUERY = '''
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
        
        self.ISSUES_QUERY = '''
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
    
    def run_query(self, query: str, variables: Dict = {}) -> Optional[Dict[Any, Any]]:
        """Run a GraphQL query with variables and return the response"""
        try:
            logger.debug(f"Running query with variables: {variables}")
            response = requests.post(self.url, headers=self.headers, json={'query': query, 'variables': variables})
            if response.status_code == 200:
                logger.debug("Query successful")
                return response.json()
            else:
                logger.error(f"Query failed with status code {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Query failed with exception: {e}")
            return None
