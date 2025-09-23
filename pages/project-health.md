---
title: Project Health Dashboard
---

# Project Health Dashboard

## Release Activity
<DataTable data={project_health_query_1}>
  <Column id="has_release_within_last_year" title="Release in Last Year"/>
</DataTable>

## Active Contributors
<DataTable data={project_health_query_2}>
  <Column id="active_contributors_count" title="Active Contributors"/>
  <Column id="contributor_category" title="Category"/>
</DataTable>

## Monthly Commits (Last 12 Months)
<DataTable data={project_health_query_3}>
  <Column id="month" title="Month"/>
  <Column id="commits_count" title="Commits"/>
  <Column id="commits_category" title="Category"/>
</DataTable>

## Issue Tracking
<DataTable data={project_health_query_4}>
  <Column id="open_issues_count" title="Open Issues"/>
</DataTable>

## Repository Verification
<DataTable data={project_health_query_5}>
  <Column id="repository_status" title="Status"/>
  <Column id="has_readme" title="Has README"/>
  <Column id="has_license" title="Has License"/>
  <Column id="repository_verification_passed" title="Verification Passed"/>
</DataTable>
