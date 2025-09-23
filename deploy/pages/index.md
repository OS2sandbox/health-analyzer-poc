# Repository Health Metrics

## Has there been at least one release within the last year?
```sql releases
SELECT * FROM 'check-releases';
```

## How many contributors have there been in the past 12 months?
```sql contributors
SELECT * FROM 'count-contributors';
```

## How many commits have there been in the past 12 months?
```sql commits
SELECT * FROM 'count-commits';
```

## How many issues are currently open?
```sql issues
SELECT * FROM 'count-open-issues';
```

## General Quality Checks
```sql verify
SELECT * FROM 'verify-repository';
```
