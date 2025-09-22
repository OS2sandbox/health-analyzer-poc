# GitHub Repository Metrics Collector

This project collects various metrics from GitHub repositories using the GitHub GraphQL API and outputs them as JSONL files. It's designed to help analyze repository activity, contributors, issues, and other key metrics.

## Features

- Collects root markdown files
- Retrieves repository license information
- Gathers release information with timestamps
- Tracks contributors and their most recent contribution dates
- Collects commit history
- Records issue information including creators and status

## Prerequisites

- Python 3.7+
- A GitHub personal access token with appropriate permissions

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The program can be configured using both a YAML configuration file and environment variables. Environment variables take precedence over the configuration file.

### Configuration File (config/config.yaml)

The default configuration file is located at `config/config.yaml`:

