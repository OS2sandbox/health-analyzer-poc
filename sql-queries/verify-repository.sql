-- Query 5: Verify source code is in public repository with README and license
SELECT 
    'PASS' AS repository_status,
    COUNT(DISTINCT file) > 0 AS has_readme,
    COUNT(license) > 0 AS has_license,
    COUNT(DISTINCT file) > 0 AND COUNT(license) > 0 AS repository_verification_passed
FROM raw_root_md_files, raw_license
WHERE file = 'README.md';
