# Plans API

This document describes how to work with test plans in TestRail using the API.

## Overview

Test plans in TestRail allow you to organize and execute multiple test runs. The API provides methods to retrieve and manage these test plans.

## API Endpoints

### Get Plan

```
GET index.php?/api/v2/get_plan/{plan_id}
```

Returns an existing test plan.

#### Parameters:

- `plan_id` (required): The ID of the test plan

#### Response Example:

```json
{
  "id": 1,
  "name": "System Test Plan",
  "description": "Comprehensive system testing",
  "milestone_id": 1,
  "assignedto_id": 1,
  "is_completed": false,
  "completed_on": null,
  "passed_count": 5,
  "blocked_count": 0,
  "untested_count": 10,
  "retest_count": 0,
  "failed_count": 2,
  "custom_status1_count": 0,
  "custom_status2_count": 0,
  "custom_status3_count": 0,
  "custom_status4_count": 0,
  "custom_status5_count": 0,
  "custom_status6_count": 0,
  "custom_status7_count": 0,
  "project_id": 1,
  "created_on": 1646317844,
  "created_by": 1,
  "url": "https://example.testrail.com/index.php?/plans/view/1",
  "entries": [
    {
      "id": "3933d74b-4282-4c1f-be62-a641ab427063",
      "suite_id": 1,
      "name": "Login Tests",
      "runs": [
        {
          "id": 1,
          "suite_id": 1,
          "name": "Login Tests",
          "description": null,
          "milestone_id": 1,
          "assignedto_id": 1,
          "include_all": true,
          "is_completed": false,
          "completed_on": null,
          "config_ids": [],
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
          "created_on": 1646317844,
          "created_by": 1,
          "url": "https://example.testrail.com/index.php?/runs/view/1"
        }
      ]
    }
  ]
}
```

### Get Plans

```
GET index.php?/api/v2/get_plans/{project_id}
```

Returns a list of test plans for a project.

#### Parameters:

- `project_id` (required): The ID of the project
- `limit` (optional): The maximum number of test plans to return, defaults to 250
- `offset` (optional): The offset for the test plans, defaults to 0
- `created_after` (optional): Only return test plans created after this date (as UNIX timestamp)
- `created_before` (optional): Only return test plans created before this date (as UNIX timestamp)
- `created_by` (optional): A comma-separated list of creators (user IDs) to filter by
- `is_completed` (optional): `1` to return completed test plans only, `0` to return active test plans only
- `milestone_id` (optional): Only return test plans with the specified milestone

### Add Plan

```
POST index.php?/api/v2/add_plan/{project_id}
```

Creates a new test plan.

#### Parameters:

- `project_id` (required): The ID of the project

#### Request Fields:

- `name` (required): The name of the new test plan
- `description`: The description of the new test plan
- `milestone_id`: The ID of the milestone to link to the test plan
- `entries`: An array of objects describing the test runs of the test plan (see the example below)

#### Request Example:

```json
{
  "name": "UI Test Plan",
  "description": "UI testing for release 2.0",
  "milestone_id": 1,
  "entries": [
    {
      "suite_id": 1,
      "name": "Login & Authentication",
      "include_all": false,
      "case_ids": [1, 2, 3],
      "config_ids": [1, 2],
      "runs": [
        {
          "name": "Chrome Tests",
          "assignedto_id": 1,
          "include_all": false,
          "case_ids": [1, 2, 3],
          "config_ids": [1]
        },
        {
          "name": "Firefox Tests",
          "assignedto_id": 2,
          "include_all": false,
          "case_ids": [1, 2, 3],
          "config_ids": [2]
        }
      ]
    }
  ]
}
```

### Add Plan Entry

```
POST index.php?/api/v2/add_plan_entry/{plan_id}
```

Adds a new entry (test run) to a plan.

#### Parameters:

- `plan_id` (required): The ID of the test plan

#### Request Fields:

- `suite_id` (required): The ID of the test suite for the test run(s)
- `name`: The name of the test run(s)
- `description`: The description of the test run(s)
- `assignedto_id`: The ID of the user the test run(s) should be assigned to
- `include_all`: `true` to include all test cases from the test suite, `false` to use a custom case selection
- `case_ids`: An array of case IDs for the custom case selection
- `config_ids`: An array of configuration IDs used for the test runs (requires TestRail 3.1 or later)
- `runs`: An array of custom test runs, each run requires the same properties as adding a test run

### Update Plan

```
POST index.php?/api/v2/update_plan/{plan_id}
```

Updates an existing test plan.

#### Parameters:

- `plan_id` (required): The ID of the test plan

#### Request Fields:

- `name`: The name of the test plan
- `description`: The description of the test plan
- `milestone_id`: The ID of the milestone to link to the test plan
- `entries`: Entries can't be updated directly with this method, but you can use add_plan_entry/update_plan_entry/delete_plan_entry

### Update Plan Entry

```
POST index.php?/api/v2/update_plan_entry/{plan_id}/{entry_id}
```

Updates an existing plan entry (test run).

#### Parameters:

- `plan_id` (required): The ID of the test plan
- `entry_id` (required): The ID of the plan entry

#### Request Fields:

- `name`: The name of the test run(s)
- `description`: The description of the test run(s)
- `assignedto_id`: The ID of the user the test run(s) should be assigned to
- `include_all`: `true` to include all test cases from the test suite, `false` to use a custom case selection
- `case_ids`: An array of case IDs for the custom case selection
- `runs`: An array of custom test runs, each run requires the same properties as updating a test run

### Close Plan

```
POST index.php?/api/v2/close_plan/{plan_id}
```

Closes an existing test plan and archives its test runs and results.

#### Parameters:

- `plan_id` (required): The ID of the test plan

### Delete Plan

```
POST index.php?/api/v2/delete_plan/{plan_id}
```

Deletes an existing test plan.

#### Parameters:

- `plan_id` (required): The ID of the test plan

### Delete Plan Entry

```
POST index.php?/api/v2/delete_plan_entry/{plan_id}/{entry_id}
```

Deletes one or more existing test runs from a plan.

#### Parameters:

- `plan_id` (required): The ID of the test plan
- `entry_id` (required): The ID of the plan entry

## Python Example

Here's a Python example for working with test plans:

```python
import requests
import json

class TestRailAPI:
    def __init__(self, url, email, api_key):
        self.url = url
        self.email = email
        self.api_key = api_key
        
    def get_plan(self, plan_id):
        api_url = f"{self.url}/index.php?/api/v2/get_plan/{plan_id}"
        
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'}
        )
        
        return response.json()
    
    def add_plan(self, project_id, name, description=None, milestone_id=None, entries=None):
        api_url = f"{self.url}/index.php?/api/v2/add_plan/{project_id}"
        
        payload = {
            "name": name
        }
        
        if description:
            payload["description"] = description
            
        if milestone_id:
            payload["milestone_id"] = milestone_id
            
        if entries:
            payload["entries"] = entries
        
        response = requests.post(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        
        return response.json()
    
    def add_plan_entry(self, plan_id, suite_id, name=None, include_all=True, case_ids=None, config_ids=None):
        api_url = f"{self.url}/index.php?/api/v2/add_plan_entry/{plan_id}"
        
        payload = {
            "suite_id": suite_id,
            "include_all": include_all
        }
        
        if name:
            payload["name"] = name
            
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

# Usage example
testrail = TestRailAPI(
    url="https://example.testrail.com",
    email="your_email@example.com",
    api_key="your_api_key"
)

# Create a new test plan
plan = testrail.add_plan(
    project_id=1,
    name="Regression Test Plan",
    description="Regression testing for release 2.0",
    milestone_id=1
)

print(f"Created test plan: {plan['name']} (ID: {plan['id']})")

# Add an entry to the plan
entry = testrail.add_plan_entry(
    plan_id=plan['id'],
    suite_id=1,
    name="Core Functionality Tests",
    include_all=False,
    case_ids=[1, 2, 3, 4, 5]
)

print(f"Added plan entry: {entry['name']}")

# Get plan details
plan_details = testrail.get_plan(plan['id'])
print(f"Plan has {len(plan_details['entries'])} entries and {plan_details['untested_count']} untested tests")
```

## Creating a Test Plan with Multiple Configurations

Here's an example of creating a test plan with multiple configuration-specific test runs:

```python
# First, get the available configurations
def get_configs(self, project_id):
    api_url = f"{self.url}/index.php?/api/v2/get_configs/{project_id}"
    response = requests.get(
        api_url,
        auth=(self.email, self.api_key),
        headers={'Content-Type': 'application/json'}
    )
    return response.json()

configs = testrail.get_configs(1)

# Find configuration IDs
browser_configs = next((group['configs'] for group in configs if group['name'] == 'Browsers'), [])
browser_ids = [config['id'] for config in browser_configs]

# Create a plan with configuration-specific entries
entries = [
    {
        "suite_id": 1,
        "name": "Login Tests",
        "include_all": False,
        "case_ids": [1, 2, 3],
        "config_ids": browser_ids
    }
]

plan = testrail.add_plan(
    project_id=1,
    name="Cross-Browser Test Plan",
    entries=entries
)

print(f"Created test plan with {len(browser_ids)} browser configurations")
```

## Best Practices

1. Organize test plans around specific releases, milestones, or testing phases
2. Use meaningful names and descriptions for test plans and entries
3. Link test plans to appropriate milestones
4. Use configurations to create browser/platform-specific test runs
5. Close completed test plans to archive their results

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
