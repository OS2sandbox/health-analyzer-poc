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

# 1. Check for README and OSI-Approved License
echo "1. Checking for README and OSI-approved license..."
QUERY1='{
    "query": "query { repository(owner: \"'"$OWNER"'\", name: \"'"$REPO_NAME"'\") { readme { name } licenseInfo { key name } } }"
}'
echo "   Query: $QUERY1"
README_LICENSE_RESPONSE=$(curl -s -H "Authorization: bearer $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$QUERY1" https://api.github.com/graphql)
echo "   Raw response: $README_LICENSE_RESPONSE"

# Parse the response
HAS_README=$(echo "$README_LICENSE_RESPONSE" | grep -q '"readme":{' && echo "true" || echo "false")
HAS_LICENSE=$(echo "$README_LICENSE_RESPONSE" | grep -q '"licenseInfo":{' && echo "true" || echo "false")
echo "   Has README: $HAS_README"
echo "   Has License: $HAS_LICENSE"

if [ "$HAS_README" = "true" ] && [ "$HAS_LICENSE" = "true" ]; then
    echo "   Result: README and OSI-approved license: PASS"
else
    echo "   Result: README and OSI-approved license: FAIL"
fi
echo

# 2. Check for at least one release in the last year
echo "2. Checking for releases in the last year..."
QUERY2='{
    "query": "query { repository(owner: \"'"$OWNER"'\", name: \"'"$REPO_NAME"'\") { releases(last: 1, orderBy: {field: CREATED_AT, direction: DESC}) { edges { node { publishedAt } } } } }"
}'
echo "   Query: $QUERY2"
RELEASE_RESPONSE=$(curl -s -H "Authorization: bearer $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$QUERY2" https://api.github.com/graphql)
echo "   Raw response: $RELEASE_RESPONSE"

# Check if the most recent release is within the last year
LATEST_RELEASE_DATE=$(echo "$RELEASE_RESPONSE" | grep -o '"publishedAt":"[^"]*"' | cut -d'"' -f4)
echo "   Latest release date: $LATEST_RELEASE_DATE"
if [ -n "$LATEST_RELEASE_DATE" ]; then
    RELEASE_EPOCH=$(date -d "$LATEST_RELEASE_DATE" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%SZ" "$LATEST_RELEASE_DATE" +%s)
    YEAR_AGO_EPOCH=$(date -d "$SINCE_DATE" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%SZ" "$SINCE_DATE" +%s)
    echo "   Release epoch: $RELEASE_EPOCH"
    echo "   Year ago epoch: $YEAR_AGO_EPOCH"
    if [ "$RELEASE_EPOCH" -gt "$YEAR_AGO_EPOCH" ]; then
        echo "   Result: Release in last year: yes"
    else
        echo "   Result: Release in last year: no"
    fi
else
    echo "   Result: Release in last year: no"
fi
echo

# 3. Count active contributors (last 12 months)
echo "3. Counting active contributors in the last 12 months..."
QUERY3='{
    "query": "query { repository(owner: \"'"$OWNER"'\", name: \"'"$REPO_NAME"'\") { defaultBranchRef { target { ... on Commit { history(since: \"'"$SINCE_DATE"'\") { nodes { author { user { login } } } } } } } } }"
}'
echo "   Query: $QUERY3"
CONTRIBUTORS_RESPONSE=$(curl -s -H "Authorization: bearer $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$QUERY3" https://api.github.com/graphql)
echo "   Raw response: $CONTRIBUTORS_RESPONSE"

# Extract and count unique logins
UNIQUE_CONTRIBUTORS=$(echo "$CONTRIBUTORS_RESPONSE" | grep -o '"login":"[^"]*"' | sort | uniq | wc -l)
echo "   Unique contributors count: $UNIQUE_CONTRIBUTORS"
if [ "$UNIQUE_CONTRIBUTORS" -gt 3 ]; then
    echo "   Result: Number of active contributors: above 3 ($UNIQUE_CONTRIBUTORS)"
else
    echo "   Result: Number of active contributors: below 3 ($UNIQUE_CONTRIBUTORS)"
fi
echo

# 4. Count commits per month (last 12 months)
echo "4. Calculating average commits per month..."
QUERY4='{
    "query": "query { repository(owner: \"'"$OWNER"'\", name: \"'"$REPO_NAME"'\") { defaultBranchRef { target { ... on Commit { history(since: \"'"$SINCE_DATE"'\") { totalCount } } } } } }"
}'
echo "   Query: $QUERY4"
COMMITS_RESPONSE=$(curl -s -H "Authorization: bearer $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$QUERY4" https://api.github.com/graphql)
echo "   Raw response: $COMMITS_RESPONSE"

TOTAL_COMMITS=$(echo "$COMMITS_RESPONSE" | grep -o '"totalCount":[0-9]*' | cut -d':' -f2)
echo "   Total commits: $TOTAL_COMMITS"
AVG_COMMITS_PER_MONTH=$((TOTAL_COMMITS / 12))
echo "   Average commits per month: $AVG_COMMITS_PER_MONTH"
if [ "$AVG_COMMITS_PER_MONTH" -gt 2 ]; then
    echo "   Result: Average commits per month: above 2 ($AVG_COMMITS_PER_MONTH)"
else
    echo "   Result: Average commits per month: below 2 ($AVG_COMMITS_PER_MONTH)"
fi
echo

# 5. Count open issues
echo "5. Counting open issues..."
QUERY5='{
    "query": "query { repository(owner: \"'"$OWNER"'\", name: \"'"$REPO_NAME"'\") { issues(states: OPEN) { totalCount } } }"
}'
echo "   Query: $QUERY5"
ISSUES_RESPONSE=$(curl -s -H "Authorization: bearer $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -d "$QUERY5" https://api.github.com/graphql)
echo "   Raw response: $ISSUES_RESPONSE"

OPEN_ISSUES=$(echo "$ISSUES_RESPONSE" | grep -o '"totalCount":[0-9]*' | cut -d':' -f2)
echo "   Result: Number of open issues: $OPEN_ISSUES"
