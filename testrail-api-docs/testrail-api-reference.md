# TestRail API Reference for MCP Integration

This document provides a comprehensive reference for integrating the TestRail API with Model Context Protocol (MCP) servers. It consolidates essential information about the TestRail API, its endpoints, and implementation patterns to facilitate building a reliable MCP server.

## Table of Contents

- [Introduction](#introduction)
- [Authentication](#authentication)
- [Rate Limits](#rate-limits)
- [API Structure](#api-structure)
- [Core Entities](#core-entities)
  - [Projects](#projects)
  - [Suites](#suites)
  - [Test Cases](#test-cases)
  - [Test Runs](#test-runs)
  - [Test Results](#test-results)
- [Common Use Cases](#common-use-cases)
  - [Creating Test Cases](#creating-test-cases)
  - [Reporting Test Results](#reporting-test-results)
  - [Retrieving Test Information](#retrieving-test-information)
- [MCP Implementation Guidelines](#mcp-implementation-guidelines)
- [Error Handling](#error-handling)
- [Examples](#examples)

## Introduction

TestRail's API allows integration with various tools, frameworks, and third-party applications. It's HTTP-based and follows a RESTful approach, making it accessible from virtually any programming language or framework.

Key features:
- HTTP-based API with JSON request/response format
- UTF-8 encoding for all communications
- Basic authentication using API keys
- Comprehensive endpoints for all TestRail entities

## Authentication

TestRail API uses Basic Authentication with the following approach:

```
Authorization: Basic <base64-encoded-credentials>
```

Where credentials are in the format: `username:password` or `email:api_key`

For security reasons, it's recommended to use an API key rather than a password. API keys can be generated in TestRail's administration area under:

```
Profile > API Keys > Add Key
```

Example HTTP request header:
```
Authorization: Basic ZXhhbXBsZUB0ZXN0cmFpbC5jb206YXBpX2tleV9oZXJl
```

For MCP integration, the API key should be securely stored and accessed by the MCP server.

## Rate Limits

TestRail Cloud has built-in rate limits to ensure optimal performance for all users:

- When rate limits are exceeded, TestRail returns a 429 Too Many Requests response
- A Retry-After header indicates when the next request can be made
- Rate limits don't apply to TestRail Server (on-premise) installations

To avoid rate limiting:
- Use bulk API endpoints when possible (e.g., `add_results_for_cases` instead of multiple `add_result` calls)
- Implement time delays between API calls
- Consider upgrading to TestRail Enterprise Cloud for higher limits

## API Structure

All API endpoints follow this URL structure:
```
https://<your-instance>.testrail.io/index.php?/api/v2/<endpoint>
```

Requests use standard HTTP methods:
- GET: Retrieve data
- POST: Create or modify data

All requests and responses use JSON format. For example:

```json
{
  "title": "New Test Case",
  "type_id": 1,
  "priority_id": 3,
  "estimate": "30m"
}
```

## Core Entities

### Projects

Projects are the main organizational unit in TestRail. Each project can contain test suites, cases, runs, and results.

#### Get Project

```
GET index.php?/api/v2/get_project/{project_id}
```

Parameters:
- `project_id` (required): The ID of the project

Response example:
```json
{
  "id": 1,
  "name": "Web Application",
  "announcement": "Project announcement",
  "show_announcement": true,
  "is_completed": false,
  "completed_on": null,
  "suite_mode": 3,
  "url": "https://example.testrail.com/index.php?/projects/overview/1"
}
```

#### Get Projects

```
GET index.php?/api/v2/get_projects
```

Parameters:
- `is_completed` (optional): 0 for active projects, 1 for completed projects

Response includes a paginated list of all projects.

#### Add Project

```
POST index.php?/api/v2/add_project
```

Required fields:
- `name`: The name of the new project

Optional fields:
- `announcement`: Project description
- `show_announcement`: Boolean flag
- `suite_mode`: 1 (single suite), 2 (single suite + baselines), or 3 (multiple suites)

### Suites

Test suites are collections of test cases. In multi-suite mode, projects can have multiple test suites.

#### Get Suite

```
GET index.php?/api/v2/get_suite/{suite_id}
```

Parameters:
- `suite_id` (required): The ID of the test suite

#### Get Suites

```
GET index.php?/api/v2/get_suites/{project_id}
```

Parameters:
- `project_id` (required): The ID of the project

#### Add Suite

```
POST index.php?/api/v2/add_suite/{project_id}
```

Parameters:
- `project_id` (required): The ID of the project

Required fields:
- `name`: The name of the new test suite

Optional fields:
- `description`: The description of the new test suite

### Test Cases

Test cases define the test steps, expected results, and other test-related data.

#### Get Case

```
GET index.php?/api/v2/get_case/{case_id}
```

Parameters:
- `case_id` (required): The ID of the test case

#### Get Cases

```
GET index.php?/api/v2/get_cases/{project_id}&suite_id={suite_id}
```

Parameters:
- `project_id` (required): The ID of the project
- `suite_id` (optional): The ID of the test suite (required for multi-suite projects)

#### Add Case

```
POST index.php?/api/v2/add_case/{section_id}
```

Parameters:
- `section_id` (required): The ID of the section the test case should be added to

Required fields:
- `title`: The title of the test case

Optional fields:
- `type_id`: The ID of the case type
- `priority_id`: The ID of the case priority
- `estimate`: The time estimate (e.g., "30s" or "1m 45s")
- `milestone_id`: The ID of the milestone to link to
- `refs`: A comma-separated list of references

Custom fields use the prefix `custom_`, for example:
- `custom_steps`: Test steps
- `custom_expected`: Expected results

### Test Runs

Test runs represent test executions against specific test suites.

#### Get Run

```
GET index.php?/api/v2/get_run/{run_id}
```

Parameters:
- `run_id` (required): The ID of the test run

#### Get Runs

```
GET index.php?/api/v2/get_runs/{project_id}
```

Parameters:
- `project_id` (required): The ID of the project
- Several optional filtering parameters are available (created dates, milestone, etc.)

#### Add Run

```
POST index.php?/api/v2/add_run/{project_id}
```

Parameters:
- `project_id` (required): The ID of the project

Required fields:
- `name`: The name of the test run
- `suite_id`: The ID of the test suite (for multi-suite projects)

Optional fields:
- `description`: The description of the test run
- `milestone_id`: The ID of the milestone to link to
- `assignedto_id`: The ID of the user to assign the test run to
- `include_all`: Boolean to include all test cases (true) or a subset (false)
- `case_ids`: Array of case IDs to include (required if include_all is false)

### Test Results

Test results record the outcome of tests within a test run.

#### Get Results

```
GET index.php?/api/v2/get_results/{test_id}
```

Parameters:
- `test_id` (required): The ID of the test

#### Get Results for Run

```
GET index.php?/api/v2/get_results_for_run/{run_id}
```

Parameters:
- `run_id` (required): The ID of the test run
- Several optional filtering parameters are available

#### Add Result

```
POST index.php?/api/v2/add_result/{test_id}
```

Parameters:
- `test_id` (required): The ID of the test

Required fields:
- `status_id`: The ID of the test status (1=passed, 2=blocked, 3=untested, 4=retest, 5=failed)

Optional fields:
- `comment`: A comment or error message
- `version`: The tested version or build
- `elapsed`: The test execution time (e.g., "30s" or "1m 45s")
- `defects`: A comma-separated list of defect IDs
- `assignedto_id`: The ID of the user the test should be assigned to

#### Add Results for Cases

```
POST index.php?/api/v2/add_results_for_cases/{run_id}
```

Parameters:
- `run_id` (required): The ID of the test run

Required fields:
- `results`: An array of result objects, each containing:
  - `case_id`: The ID of the test case
  - `status_id`: The ID of the test status
  - Other optional fields as in `add_result`

## Common Use Cases

### Creating Test Cases

Creating test cases programmatically is useful for importing from other systems or generating test cases from requirements.

Example in Python:
```python
import requests
import json

def create_test_case(url, email, api_key, section_id, title, type_id=1, priority_id=2, 
                     custom_steps="", custom_expected=""):
    api_url = f"{url}/index.php?/api/v2/add_case/{section_id}"
    payload = {
        "title": title,
        "type_id": type_id, 
        "priority_id": priority_id
    }
    
    # Add custom fields if provided
    if custom_steps:
        payload["custom_steps"] = custom_steps
        
    if custom_expected:
        payload["custom_expected"] = custom_expected
    
    response = requests.post(
        api_url,
        auth=(email, api_key),
        headers={'Content-Type': 'application/json'},
        data=json.dumps(payload)
    )
    
    return response.json()
```

### Reporting Test Results

Reporting test results from automated testing tools is one of the most common API use cases.

Example in Python for reporting multiple results at once:
```python
import requests
import json

def add_results_for_cases(url, email, api_key, run_id, results):
    """
    Add results for multiple test cases in a single request.
    
    results: A list of dictionaries, each containing:
        - case_id: The ID of the test case
        - status_id: The ID of the test status (1=passed, 5=failed, etc.)
        - comment: Optional comment or error message
        - elapsed: Optional test execution time (e.g., "30s")
    """
    api_url = f"{url}/index.php?/api/v2/add_results_for_cases/{run_id}"
    
    payload = {
        "results": results
    }
    
    response = requests.post(
        api_url,
        auth=(email, api_key),
        headers={'Content-Type': 'application/json'},
        data=json.dumps(payload)
    )
    
    return response.json()

# Example usage
results = [
    {
        "case_id": 1,
        "status_id": 1,  # Passed
        "comment": "Test executed successfully",
        "elapsed": "15s"
    },
    {
        "case_id": 2,
        "status_id": 5,  # Failed
        "comment": "Test failed: could not submit form",
        "elapsed": "45s",
        "defects": "BUG-123"
    }
]

response = add_results_for_cases(
    url="https://example.testrail.com",
    email="your_email@example.com",
    api_key="your_api_key",
    run_id=1,
    results=results
)
```

### Retrieving Test Information

Retrieving test information is useful for dashboard creation, reporting, and analysis.

Example in Python for getting test results from a run:
```python
import requests
import json

def get_results_for_run(url, email, api_key, run_id, status_id=None, limit=None):
    api_url = f"{url}/index.php?/api/v2/get_results_for_run/{run_id}"
    
    params = {}
    if status_id:
        params['status_id'] = status_id
    if limit:
        params['limit'] = limit
        
    response = requests.get(
        api_url,
        auth=(email, api_key),
        headers={'Content-Type': 'application/json'},
        params=params
    )
    
    return response.json()
```
