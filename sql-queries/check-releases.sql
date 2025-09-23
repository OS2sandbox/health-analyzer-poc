-- Query 1: Check if there has been at least one release within the last year
SELECT 
    CASE 
        WHEN COUNT(*) > 0 THEN 'yes' 
        ELSE 'no' 
    END AS has_release_within_last_year
FROM raw_releases 
WHERE publishedAt >= datetime('now', '-1 year');
