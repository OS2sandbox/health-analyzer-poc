#!/usr/bin/env python3

import os
import sys
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from config import Configuration

logger = logging.getLogger(__name__)

class GitHubClient:
    def __init__(self, config: Configuration):
        self.config = config
        
        # Check if GitHub token is set in config (from env var or config file)
        self.github_token = self.config.github_token
        
        if not self.github_token:
            logger.error("Please set GITHUB_TOKEN environment variable.")
            sys.exit(1)
        
        # Headers for GraphQL API
        self.headers = {
            'Authorization': f'bearer {self.github_token}',
            'Content-Type': 'application/json'
        }
        
        # GraphQL endpoint
        self.url = self.config.github_api_url
        
        # Calculate the date for specified days ago
        self.date_range_ago = (datetime.now() - timedelta(days=self.config.date_range_days)).strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # GraphQL Queries with configurable pagination limit
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
        
        self.RELEASES_QUERY = f'''
        query($cursor: String) {{
            repository(owner: "%s", name: "%s") {{
                releases(first: {self.config.pagination_limit}, orderBy: {{field: CREATED_AT, direction: DESC}}, after: $cursor) {{
                    edges {{
                        node {{
                            name
                            publishedAt
                        }}
                        cursor
                    }}
                    pageInfo {{
                        hasNextPage
                        endCursor
                    }}
                }}
            }}
        }}
        '''
        
        self.CONTRIBUTORS_QUERY = f'''
        query($cursor: String, $since: GitTimestamp!) {{
            repository(owner: "%s", name: "%s") {{
                defaultBranchRef {{
                    target {{
                        ... on Commit {{
                            history(first: {self.config.pagination_limit}, since: $since, after: $cursor) {{
                                nodes {{
                                    author {{
                                        user {{
                                            login
                                        }}
                                    }}
                                    committedDate
                                }}
                                pageInfo {{
                                    hasNextPage
                                    endCursor
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
        '''
        
        self.COMMITS_QUERY = f'''
        query($cursor: String, $since: GitTimestamp!) {{
            repository(owner: "%s", name: "%s") {{
                defaultBranchRef {{
                    target {{
                        ... on Commit {{
                            history(first: {self.config.pagination_limit}, since: $since, after: $cursor) {{
                                nodes {{
                                    messageHeadline
                                    committedDate
                                    author {{
                                        name
                                    }}
                                }}
                                pageInfo {{
                                    hasNextPage
                                    endCursor
                                }}
                            }}
                        }}
                    }}
                }}
            }}
        }}
        '''
        
        self.ISSUES_QUERY = f'''
        query($cursor: String) {{
            repository(owner: "%s", name: "%s") {{
                issues(first: {self.config.pagination_limit}, states: [OPEN, CLOSED], after: $cursor, orderBy: {{field: CREATED_AT, direction: DESC}}) {{
                    nodes {{
                        title
                        state
                        author {{
                            login
                        }}
                        createdAt
                    }}
                    pageInfo {{
                        hasNextPage
                        endCursor
                    }}
                }}
            }}
        }}
        '''
    
    def run_query(self, query: str, variables: Dict = {}) -> Optional[Dict[Any, Any]]:
        """Run a GraphQL query with variables and return the response"""
        try:
            logger.debug(f"Running query with variables: {variables}")
            response = requests.post(
                self.url, 
                headers=self.headers, 
                json={'query': query, 'variables': variables},
                timeout=self.config.request_timeout
            )
            if response.status_code == 200:
                logger.debug("Query successful")
                return response.json()
            else:
                logger.error(f"Query failed with status code {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Query failed with exception: {e}")
            return None
