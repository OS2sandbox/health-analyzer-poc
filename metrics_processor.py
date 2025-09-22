#!/usr/bin/env python3

import logging
from typing import Dict, List, Tuple, Optional, Any
from github_client import GitHubClient

logger = logging.getLogger(__name__)

class MetricsProcessor:
    def __init__(self, github_client: GitHubClient):
        self.github_client = github_client
    
    def get_root_md_files(self, owner: str, repo_name: str) -> List[str]:
        """Get all .md files in the root folder"""
        logger.info("Checking root .md files...")
        query = self.github_client.ROOT_FILES_QUERY % (owner, repo_name)
        result = self.github_client.run_query(query)
        
        md_files = []
        if result and 'data' in result and result['data']['repository']['object']:
            entries = result['data']['repository']['object']['entries']
            md_files = [entry['name'] for entry in entries if entry['name'].endswith('.md')]
            logger.info(f"Found {len(md_files)} .md files in root")
        else:
            logger.warning("No .md files found or error occurred")
        return md_files
    
    def get_license(self, owner: str, repo_name: str) -> str:
        """Get the repository license name"""
        logger.info("Checking license...")
        query = self.github_client.LICENSE_QUERY % (owner, repo_name)
        result = self.github_client.run_query(query)
        
        license_name = 'None'
        if result and 'data' in result:
            license_info = result['data']['repository']['licenseInfo']
            license_name = license_info['name'] if license_info else 'None'
            logger.info(f"License found: {license_name}")
        else:
            logger.warning("Error retrieving license information")
        return license_name
    
    def _extract_releases(self, result: Dict) -> Tuple[List[Dict[str, str]], Optional[Dict]]:
        """Extract releases from GraphQL response"""
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
                    if published_at and published_at >= self.github_client.one_year_ago:
                        releases.append({
                            'name': edge['node']['name'] or 'Unnamed release',
                            'publishedAt': published_at
                        })
                    elif published_at and published_at < self.github_client.one_year_ago:
                        # Stop pagination if we've gone past the one-year boundary
                        logger.debug("Reached releases older than one year, stopping pagination")
                        return releases, None
                        
        return releases, page_info
    
    def get_releases(self, owner: str, repo_name: str) -> List[Dict[str, str]]:
        """Get all releases with timestamps from the past year"""
        logger.info("Checking releases...")
        query = self.github_client.RELEASES_QUERY % (owner, repo_name)
        releases = self._paginate_github_query(query, self._extract_releases)
        logger.info(f"Found {len(releases)} releases in the past year")
        return releases
    
    def _extract_contributors(self, result: Dict) -> Tuple[List[Dict[str, str]], Optional[Dict]]:
        """Extract contributors from GraphQL response"""
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
    
    def get_contributors(self, owner: str, repo_name: str) -> Dict[str, str]:
        """Get all contributors with their most recent contribution date from the past year"""
        logger.info("Checking contributors...")
        query = self.github_client.CONTRIBUTORS_QUERY % (owner, repo_name)
        contributor_list = self._paginate_github_query(query, self._extract_contributors, {'since': self.github_client.one_year_ago})
        
        # Merge all contributor dictionaries
        final_contributors: Dict[str, str] = {}
        for contributors in contributor_list:
            for login, date in contributors.items():
                if login not in final_contributors or date > final_contributors[login]:
                    final_contributors[login] = date
                    
        logger.info(f"Found {len(final_contributors)} contributors in the past year")
        return final_contributors
    
    def _extract_commits(self, result: Dict) -> Tuple[List[Dict[str, str]], Optional[Dict]]:
        """Extract commits from GraphQL response"""
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
    
    def get_commits(self, owner: str, repo_name: str) -> List[Dict[str, str]]:
        """Get all commits from the past year"""
        logger.info("Checking commits...")
        query = self.github_client.COMMITS_QUERY % (owner, repo_name)
        commits = self._paginate_github_query(query, self._extract_commits, {'since': self.github_client.one_year_ago})
        logger.info(f"Found {len(commits)} commits in the past year")
        return commits
    
    def _extract_issues(self, result: Dict) -> Tuple[List[Dict[str, str]], Optional[Dict]]:
        """Extract issues from GraphQL response"""
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
                    if created_at and created_at >= self.github_client.one_year_ago:
                        issues.append({
                            'title': issue.get('title', ''),
                            'state': issue.get('state', ''),
                            'author': issue.get('author', {}).get('login', 'Unknown') if issue.get('author') else 'Unknown',
                            'createdAt': created_at
                        })
                    elif created_at and created_at < self.github_client.one_year_ago:
                        # Stop pagination if we've gone past the one-year boundary
                        logger.debug("Reached issues older than one year, stopping pagination")
                        return issues, None
                        
        return issues, page_info
    
    def get_issues(self, owner: str, repo_name: str) -> List[Dict[str, str]]:
        """Get all issues with creator and status from the past year"""
        logger.info("Checking issues...")
        query = self.github_client.ISSUES_QUERY % (owner, repo_name)
        issues = self._paginate_github_query(query, self._extract_issues)
        logger.info(f"Found {len(issues)} issues in the past year")
        return issues
    
    def _paginate_github_query(
        self,
        query: str, 
        extract_function, 
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
                
            result = self.github_client.run_query(query, variables)
            
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
