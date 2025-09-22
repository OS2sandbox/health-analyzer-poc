select
  repository.name,
  repository.issues.totalCount as total_open_issues,
  repository.pullRequests.totalCount as total_open_pull_requests,
  repository.stargazers.totalCount as total_stargazers,
  repository.forks.totalCount as total_forks,
  repository.releases.totalCount as total_releases
from read_json_auto('sources/project_health.json')