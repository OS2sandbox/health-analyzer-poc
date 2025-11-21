SELECT
    T.data.repository.stargazers.totalCount AS total_stargazers,
    T.data.repository.forks.totalCount AS total_forks,
    T.data.repository.issues.totalCount AS total_open_issues,
    T.data.repository.pullRequests.totalCount AS total_open_pull_requests,
    T.data.repository.releases.totalCount AS total_releases
FROM read_json_auto('sources/github/project_health.json') AS T
