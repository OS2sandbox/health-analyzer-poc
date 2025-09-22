#!/bin/bash

# Check if required environment variables are set
if [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN environment variable is not set."
    exit 1
fi

if [ -z "$OWNER" ]; then
    echo "Error: OWNER environment variable is not set."
    exit 1
fi

if [ -z "$REPO_NAME" ]; then
    echo "Error: REPO_NAME environment variable is not set."
    exit 1
fi

# Calculate the date one year ago in ISO 8601 format
SINCE_DATE=$(date -u -d "365 days ago" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -v-365d -u +"%Y-%m-%dT%H:%M:%SZ")
echo "Since date: $SINCE_DATE"

echo "Checking metrics for repository: $OWNER/$REPO_NAME"
echo "=================================================="

# 1. List all .md files in the root folder
echo "1. Listing all .md files in the root folder..."
QUERY1='{
    "query": "query { repository(owner: \"'"$OWNER"'\", name: \"'"$REPO_NAME"'\") { object(expression: \"HEAD:\") { ... on Tree { entries { name } } } } }"
}'
echo "   Query: $QUERY1"
ROOT_FILES_RESPONSE=$(curl -s -H "Authorization: bearer $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$QUERY1" https://api.github.com/graphql)
echo "   Raw response: $ROOT_FILES_RESPONSE"

# Extract .md files
echo "   .md files in root:"
echo "$ROOT_FILES_RESPONSE" | grep -o '"name":"[^"]*"' | cut -d'"' -f4 | grep '\.md$' | while read -r file; do
    echo "     - $file"
done
echo

# 2. Get license name
echo "2. Getting license name..."
QUERY2='{
    "query": "query { repository(owner: \"'"$OWNER"'\", name: \"'"$REPO_NAME"'\") { licenseInfo { name } } }"
}'
echo "   Query: $QUERY2"
LICENSE_RESPONSE=$(curl -s -H "Authorization: bearer $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$QUERY2" https://api.github.com/graphql)
echo "   Raw response: $LICENSE_RESPONSE"

# Extract license name
LICENSE_NAME=$(echo "$LICENSE_RESPONSE" | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
echo "   License name: ${LICENSE_NAME:-None}"
echo

# 3. List all releases with timestamps
echo "3. Listing all releases with timestamps..."
QUERY3='{
    "query": "query { repository(owner: \"'"$OWNER"'\", name: \"'"$REPO_NAME"'\") { releases(last: 100, orderBy: {field: CREATED_AT, direction: DESC}) { edges { node { name publishedAt } } } } }"
}'
echo "   Query: $QUERY3"
RELEASES_RESPONSE=$(curl -s -H "Authorization: bearer $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$QUERY3" https://api.github.com/graphql)
echo "   Raw response: $RELEASES_RESPONSE"

# Extract releases
echo "   Releases:"
echo "$RELEASES_RESPONSE" | grep -E '"name":|"publishedAt":' | while read -r line1 && read -r line2; do
    name=$(echo "$line1" | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
    date=$(echo "$line2" | grep -o '"publishedAt":"[^"]*"' | cut -d'"' -f4)
    echo "     - $name: $date"
done
echo

# 4. List all contributors with their most recent contribution date
echo "4. Listing all contributors with their most recent contribution date..."
QUERY4='{
    "query": "query { repository(owner: \"'"$OWNER"'\", name: \"'"$REPO_NAME"'\") { defaultBranchRef { target { ... on Commit { history(first: 100) { nodes { author { user { login } } committedDate } } } } } } }"
}'
echo "   Query: $QUERY4"
CONTRIBUTORS_RESPONSE=$(curl -s -H "Authorization: bearer $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$QUERY4" https://api.github.com/graphql)
echo "   Raw response: $CONTRIBUTORS_RESPONSE"

# Extract contributors and their latest commit dates
echo "   Contributors and their most recent contribution:"
# This is a simplified approach - in practice, you'd want to process this more carefully
echo "$CONTRIBUTORS_RESPONSE" | grep -E '"login":|"committedDate":' | while read -r line1 && read -r line2; do
    login=$(echo "$line1" | grep -o '"login":"[^"]*"' | cut -d'"' -f4)
    date=$(echo "$line2" | grep -o '"committedDate":"[^"]*"' | cut -d'"' -f4)
    if [ -n "$login" ] && [ -n "$date" ]; then
        echo "     - $login: $date"
    fi
done
echo

# 5. List all commits
echo "5. Listing all commits..."
QUERY5='{
    "query": "query { repository(owner: \"'"$OWNER"'\", name: \"'"$REPO_NAME"'\") { defaultBranchRef { target { ... on Commit { history(first: 100) { nodes { messageHeadline committedDate author { name } } } } } } } }"
}'
echo "   Query: $QUERY5"
COMMITS_RESPONSE=$(curl -s -H "Authorization: bearer $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$QUERY5" https://api.github.com/graphql)
echo "   Raw response: $COMMITS_RESPONSE"

# Extract commits
echo "   Commits:"
echo "$COMMITS_RESPONSE" | grep -E '"messageHeadline":|"committedDate":|"name":' | while read -r line1 && read -r line2 && read -r line3; do
    message=$(echo "$line1" | grep -o '"messageHeadline":"[^"]*"' | cut -d'"' -f4)
    date=$(echo "$line2" | grep -o '"committedDate":"[^"]*"' | cut -d'"' -f4)
    author=$(echo "$line3" | grep -o '"name":"[^"]*"' | cut -d'"' -f4)
    echo "     - $date: $author - $message"
done
echo

# 6. List all issues with creator and status
echo "6. Listing all issues with creator and status..."
QUERY6='{
    "query": "query { repository(owner: \"'"$OWNER"'\", name: \"'"$REPO_NAME"'\") { issues(first: 100, states: [OPEN, CLOSED]) { nodes { title state author { login } } } } }"
}'
echo "   Query: $QUERY6"
ISSUES_RESPONSE=$(curl -s -H "Authorization: bearer $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$QUERY6" https://api.github.com/graphql)
echo "   Raw response: $ISSUES_RESPONSE"

# Extract issues
echo "   Issues:"
echo "$ISSUES_RESPONSE" | grep -E '"title":|"state":|"login":' | while read -r line1 && read -r line2 && read -r line3; do
    title=$(echo "$line1" | grep -o '"title":"[^"]*"' | cut -d'"' -f4)
    state=$(echo "$line2" | grep -o '"state":"[^"]*"' | cut -d'"' -f4)
    author=$(echo "$line3" | grep -o '"login":"[^"]*"' | cut -d'"' -f4)
    echo "     - $state: $author - $title"
done
