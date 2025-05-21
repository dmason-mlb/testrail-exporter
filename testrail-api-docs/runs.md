# Runs API

This document describes how to work with test runs in TestRail using the API.

## Overview

Test runs in TestRail allow you to execute test cases and track their results. The API provides methods to retrieve and manage these runs.

## API Endpoints

### Get Run

```
GET index.php?/api/v2/get_run/{run_id}
```

Returns an existing test run.

#### Parameters:

- `run_id` (required): The ID of the test run

#### Response Example:

```json
{
  "id": 1,
  "suite_id": 1,
  "name": "Test Run 1",
  "description": "This is a test run",
  "milestone_id": 1,
  "assignedto_id": 1,
  "include_all": true,
  "is_completed": false,
  "completed_on": null,
  "config": "Chrome, Windows 10",
  "config_ids": [1, 2],
  "passed_count": 2,
  "blocked_count": 0,
  "untested_count": 3,
  "retest_count": 0,
  "failed_count": 0,
  "custom_status1_count": 0,
  "custom_status2_count": 0,
  "custom_status3_count": 0,
  "custom_status4_count": 0,
  "custom_status5_count": 0,
  "custom_status6_count": 0,
  "custom_status7_count": 0,
  "project_id": 1,
  "plan_id": null,
  "created_on": 1646317844,
  "created_by": 1,
  "url": "https://example.testrail.com/index.php?/runs/view/1"
}
```

### Get Runs

```
GET index.php?/api/v2/get_runs/{project_id}
```

Returns a list of test runs for a project.

#### Parameters:

- `project_id` (required): The ID of the project
- `created_after` (optional): Only return test runs created after this timestamp
- `created_before` (optional): Only return test runs created before this timestamp
- `created_by` (optional): A comma-separated list of creators (user IDs) to filter by
- `is_completed` (optional): `1` to return completed test runs only, `0` to return active test runs only
- `milestone_id` (optional): A comma-separated list of milestone IDs to filter by
- `suite_id` (optional): A comma-separated list of test suite IDs to filter by
- `limit` (optional): The number of test runs to return (defaults to 250)
- `offset` (optional): Where to start when returning test runs (defaults to 0)

### Add Run

```
POST index.php?/api/v2/add_run/{project_id}
```

Creates a new test run.

#### Parameters:

- `project_id` (required): The ID of the project

#### Request Fields:

- `suite_id` (required for projects with multiple suites): The ID of the test suite for the test run
- `name` (required): The name of the test run
- `description`: The description of the test run
- `milestone_id`: The ID of the milestone to link to the test run
- `assignedto_id`: The ID of the user the test run should be assigned to
- `include_all`: `true` to include all test cases from the test suite, `false` to use a custom case selection
- `case_ids`: An array of case IDs for the custom case selection (required if include_all is `false`)
- `config_ids`: An array of configuration IDs used for the test run
- `refs`: A comma-separated list of references/requirements for the test run

#### Request Example:

```json
{
  "suite_id": 1,
  "name": "Regression Test Run",
  "description": "Regression testing for release 2.0",
  "milestone_id": 1,
  "assignedto_id": 1,
  "include_all": false,
  "case_ids": [1, 2, 3, 4, 5],
  "config_ids": [1, 2]
}
```

### Update Run

```
POST index.php?/api/v2/update_run/{run_id}
```

Updates an existing test run.

#### Parameters:

- `run_id` (required): The ID of the test run

#### Request Fields:

- `name`: The name of the test run
- `description`: The description of the test run
- `milestone_id`: The ID of the milestone to link to the test run
- `assignedto_id`: The ID of the user the test run should be assigned to
- `include_all`: `true` to include all test cases from the test suite, `false` to use a custom case selection
- `case_ids`: An array of case IDs for the custom case selection (required if include_all is `false`)
- `refs`: A comma-separated list of references/requirements for the test run

### Close Run

```
POST index.php?/api/v2/close_run/{run_id}
```

Closes an existing test run and archives its tests and results.

#### Parameters:

- `run_id` (required): The ID of the test run

### Delete Run

```
POST index.php?/api/v2/delete_run/{run_id}
```

Deletes an existing test run.

#### Parameters:

- `run_id` (required): The ID of the test run

## Python Example

Here's a Python example for working with test runs:

```python
import requests
import json

class TestRailAPI:
    def __init__(self, url, email, api_key):
        self.url = url
        self.email = email
        self.api_key = api_key
        
    def get_runs(self, project_id, is_completed=None, milestone_id=None, limit=None):
        api_url = f"{self.url}/index.php?/api/v2/get_runs/{project_id}"
        
        params = {}
        if is_completed is not None:
            params['is_completed'] = 1 if is_completed else 0
        if milestone_id:
            params['milestone_id'] = milestone_id
        if limit:
            params['limit'] = limit
            
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'},
            params=params
        )
        
        return response.json()
    
    def add_run(self, project_id, suite_id, name, description=None, milestone_id=None, 
               assignedto_id=None, include_all=True, case_ids=None, config_ids=None):
        api_url = f"{self.url}/index.php?/api/v2/add_run/{project_id}"
        
        payload = {
            "suite_id": suite_id,
            "name": name,
            "include_all": include_all
        }
        
        if description:
            payload["description"] = description
            
        if milestone_id:
            payload["milestone_id"] = milestone_id
            
        if assignedto_id:
            payload["assignedto_id"] = assignedto_id
            
        if not include_all and case_ids:
            payload["case_ids"] = case_ids
            
        if config_ids:
            payload["config_ids"] = config_ids
        
        response = requests.post(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        
        return response.json()
    
    def update_run(self, run_id, name=None, description=None, milestone_id=None, 
                  assignedto_id=None, include_all=None, case_ids=None):
        api_url = f"{self.url}/index.php?/api/v2/update_run/{run_id}"
        
        payload = {}
        
        if name:
            payload["name"] = name
            
        if description is not None:
            payload["description"] = description
            
        if milestone_id is not None:
            payload["milestone_id"] = milestone_id
            
        if assignedto_id is not None:
            payload["assignedto_id"] = assignedto_id
            
        if include_all is not None:
            payload["include_all"] = include_all
            
        if not include_all and case_ids:
            payload["case_ids"] = case_ids
        
        response = requests.post(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        
        return response.json()
    
    def close_run(self, run_id):
        api_url = f"{self.url}/index.php?/api/v2/close_run/{run_id}"
        
        response = requests.post(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'}
        )
        
        return response.json()

# Usage example
testrail = TestRailAPI(
    url="https://example.testrail.com",
    email="your_email@example.com",
    api_key="your_api_key"
)

# Get active test runs
active_runs = testrail.get_runs(1, is_completed=False)
print(f"Found {len(active_runs['runs'])} active test runs")

# Create a new test run
new_run = testrail.add_run(
    project_id=1,
    suite_id=1,
    name="Smoke Test Run",
    description="Quick smoke test for release 2.0",
    include_all=False,
    case_ids=[1, 2, 3]
)

print(f"Created test run: {new_run['name']} (ID: {new_run['id']})")

# Update test run
updated_run = testrail.update_run(
    run_id=new_run['id'],
    name="Smoke Test Run - Updated",
    assignedto_id=1
)

print(f"Updated test run name to: {updated_run['name']}")

# Close test run
closed_run = testrail.close_run(new_run['id'])
print(f"Closed test run: {closed_run['name']}")
```

## Creating a Test Run with Configurations

Here's an example of creating a test run with specific configurations:

```python
# First, get the available configurations
def get_configs(project_id):
    api_url = f"{url}/index.php?/api/v2/get_configs/{project_id}"
    response = requests.get(
        api_url,
        auth=(email, api_key),
        headers={'Content-Type': 'application/json'}
    )
    return response.json()

configs = testrail.get_configs(1)

# Find configuration IDs for Chrome on Windows
browser_config = next((c['id'] for c in configs[0]['configs'] if c['name'] == 'Chrome'), None)
os_config = next((c['id'] for c in configs[1]['configs'] if c['name'] == 'Windows'), None)

if browser_config and os_config:
    # Create a test run with specific configurations
    run = testrail.add_run(
        project_id=1,
        suite_id=1,
        name="Chrome on Windows Test Run",
        include_all=True,
        config_ids=[browser_config, os_config]
    )
    
    print(f"Created test run with configurations: {run['config']}")
```

## Best Practices

1. Use descriptive names for test runs to clearly identify their purpose
2. Link test runs to appropriate milestones for better organization
3. Consider using configurations to create environment-specific test runs
4. Assign test runs to specific users for clear ownership
5. Close completed test runs to archive their results
6. Use selective test case inclusion when running focused tests
7. Include relevant references or requirements for traceability
8. Monitor test run status and progress through the API for reporting

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
