-- Query 1: Check if there has been at least one release within the last year
SELECT 
    CASE 
        WHEN COUNT(*) > 0 THEN 'yes' 
        ELSE 'no' 
    END AS has_release_within_last_year,
    COUNT(*) > 0 AS has_release_within_last_year_bool
FROM raw_releases 
WHERE publishedAt >= CURRENT_DATE - INTERVAL '1 year';
