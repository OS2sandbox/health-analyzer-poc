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

echo "Checking metrics for repository: $OWNER/$REPO_NAME"
echo "=================================================="

# 1. Check for README and OSI-Approved License
echo "1. Checking for README and OSI-approved license..."
README_LICENSE_RESPONSE=$(curl -s -H "Authorization: bearer $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"query\": \"query { repository(owner: \\\"$OWNER\\\", name: \\\"$REPO_NAME\\\") { readme { name } licenseInfo { key name } } }\"
    }" https://api.github.com/graphql)

# Parse the response
HAS_README=$(echo "$README_LICENSE_RESPONSE" | grep -q '"readme":{' && echo "true" || echo "false")
HAS_LICENSE=$(echo "$README_LICENSE_RESPONSE" | grep -q '"licenseInfo":{' && echo "true" || echo "false")

if [ "$HAS_README" = "true" ] && [ "$HAS_LICENSE" = "true" ]; then
    echo "   README and OSI-approved license: PASS"
else
    echo "   README and OSI-approved license: FAIL"
fi

# 2. Check for at least one release in the last year
echo "2. Checking for releases in the last year..."
RELEASE_RESPONSE=$(curl -s -H "Authorization: bearer $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"query\": \"query { repository(owner: \\\"$OWNER\\\", name: \\\"$REPO_NAME\\\") { releases(last: 1, orderBy: {field: CREATED_AT, direction: DESC}) { edges { node { publishedAt } } } } }\"
    }" https://api.github.com/graphql)

# Check if the most recent release is within the last year
LATEST_RELEASE_DATE=$(echo "$RELEASE_RESPONSE" | grep -o '"publishedAt":"[^"]*"' | cut -d'"' -f4)
if [ -n "$LATEST_RELEASE_DATE" ]; then
    RELEASE_EPOCH=$(date -d "$LATEST_RELEASE_DATE" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%SZ" "$LATEST_RELEASE_DATE" +%s)
    YEAR_AGO_EPOCH=$(date -d "$SINCE_DATE" +%s 2>/dev/null || date -j -f "%Y-%m-%dT%H:%M:%SZ" "$SINCE_DATE" +%s)
    if [ "$RELEASE_EPOCH" -gt "$YEAR_AGO_EPOCH" ]; then
        echo "   Release in last year: yes"
    else
        echo "   Release in last year: no"
    fi
else
    echo "   Release in last year: no"
fi

# 3. Count active contributors (last 12 months)
echo "3. Counting active contributors in the last 12 months..."
CONTRIBUTORS_RESPONSE=$(curl -s -H "Authorization: bearer $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"query\": \"query { repository(owner: \\\"$OWNER\\\", name: \\\"$REPO_NAME\\\") { defaultBranchRef { target { ... on Commit { history(since: \\\"$SINCE_DATE\\\") { nodes { author { user { login } } } } } } } } }\"
    }" https://api.github.com/graphql)

# Extract and count unique logins
UNIQUE_CONTRIBUTORS=$(echo "$CONTRIBUTORS_RESPONSE" | grep -o '"login":"[^"]*"' | sort | uniq | wc -l)
if [ "$UNIQUE_CONTRIBUTORS" -gt 3 ]; then
    echo "   Number of active contributors: above 3 ($UNIQUE_CONTRIBUTORS)"
else
    echo "   Number of active contributors: below 3 ($UNIQUE_CONTRIBUTORS)"
fi

# 4. Count commits per month (last 12 months)
echo "4. Calculating average commits per month..."
COMMITS_RESPONSE=$(curl -s -H "Authorization: bearer $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"query\": \"query { repository(owner: \\\"$OWNER\\\", name: \\\"$REPO_NAME\\\") { defaultBranchRef { target { ... on Commit { history(since: \\\"$SINCE_DATE\\\") { totalCount } } } } } }\"
    }" https://api.github.com/graphql)

TOTAL_COMMITS=$(echo "$COMMITS_RESPONSE" | grep -o '"totalCount":[0-9]*' | cut -d':' -f2)
AVG_COMMITS_PER_MONTH=$((TOTAL_COMMITS / 12))
if [ "$AVG_COMMITS_PER_MONTH" -gt 2 ]; then
    echo "   Average commits per month: above 2 ($AVG_COMMITS_PER_MONTH)"
else
    echo "   Average commits per month: below 2 ($AVG_COMMITS_PER_MONTH)"
fi

# 5. Count open issues
echo "5. Counting open issues..."
ISSUES_RESPONSE=$(curl -s -H "Authorization: bearer $GITHUB_TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"query\": \"query { repository(owner: \\\"$OWNER\\\", name: \\\"$REPO_NAME\\\") { issues(states: OPEN) { totalCount } } }\"
    }" https://api.github.com/graphql)

OPEN_ISSUES=$(echo "$ISSUES_RESPONSE" | grep -o '"totalCount":[0-9]*' | cut -d':' -f2)
echo "   Number of open issues: $OPEN_ISSUES"
