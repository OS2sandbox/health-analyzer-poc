-- This query reads the JSON file and treats it as a table.
-- The file is an array of objects, so we can access fields directly.
SELECT
-- Extract the commit date and cast it to a TIMESTAMP
commit.author.date::TIMESTAMP AS commit_date,
-- Extract the author's login
author.login AS author_name,
-- Extract the commit message
commit.message AS commit_message,
-- Extract the commit SHA
sha AS commit_sha
FROM read_json_auto('commits.json');