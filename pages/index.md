# 📊 DuckDB Project Health

A quick dashboard showing the healh metrics for the DuckDB project.

```sql project_health_data
SELECT * FROM local_duckdb.project_health
```

<BigValue
data={project_health_data}
value=total_releases
label="Total Releases"
/>


<BigValue
data={project_health_data}
value=total_open_pull_requests
label="Total Open Pull Requests"
/>

<BigValue
data={project_health_data}
value=total_forks
label="Total Forks"
/>

<BigValue
data={project_health_data}
value=total_stargazers
label="Total Stargazers"
fmt=num0
comparisonDelta=true
downIsGood=true
neutralMin=10000
neutralMax=20000
/>
