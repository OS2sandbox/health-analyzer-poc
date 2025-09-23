-- Query 4: Count the number of open issues
SELECT 
    COUNT(*) AS open_issues_count
FROM raw_issues 
WHERE state = 'OPEN';
