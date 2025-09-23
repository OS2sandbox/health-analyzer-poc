-- Query 3: Count the number of commits per month within the last 12 months
SELECT 
    strftime('%Y-%m', date) AS month,
    COUNT(*) AS commits_count,
    CASE 
        WHEN COUNT(*) > 2 THEN 'above 2' 
        ELSE 'below 2' 
    END AS commits_category,
    COUNT(*) > 2 AS is_above_threshold
FROM raw_commits 
WHERE date >= CURRENT_DATE - INTERVAL '1 year'
GROUP BY strftime('%Y-%m', date)
ORDER BY month;
