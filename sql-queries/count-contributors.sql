-- Query 2: Count the number of active contributors within the last 12 months
SELECT 
    COUNT(DISTINCT login) AS active_contributors_count,
    CASE 
        WHEN COUNT(DISTINCT login) > 3 THEN 'above 3' 
        ELSE 'below 3' 
    END AS contributor_category
FROM raw_contributors 
WHERE last_contribution >= datetime('now', '-1 year');
