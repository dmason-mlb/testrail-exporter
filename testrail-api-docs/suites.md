# Suites API

This document describes how to work with test suites in TestRail using the API.

## Overview

Test suites in TestRail are collections of test cases that can be grouped and organized. The API provides methods to retrieve and manage these suites.

## API Endpoints

### Get Suite

```
GET index.php?/api/v2/get_suite/{suite_id}
```

Returns an existing test suite.

#### Parameters:

- `suite_id` (required): The ID of the test suite

#### Response Example:

```json
{
  "id": 1,
  "name": "Master Test Suite",
  "description": "Primary test suite for application",
  "project_id": 1,
  "is_master": true,
  "is_baseline": false,
  "is_completed": false,
  "completed_on": null,
  "url": "https://example.testrail.com/index.php?/suites/view/1"
}
```

### Get Suites

```
GET index.php?/api/v2/get_suites/{project_id}
```

Returns a list of test suites for a project.

#### Parameters:

- `project_id` (required): The ID of the project

#### Response Example:

```json
[
  {
    "id": 1,
    "name": "Master Test Suite",
    "description": "Primary test suite for application",
    "project_id": 1,
    "is_master": true,
    "is_baseline": false,
    "is_completed": false,
    "completed_on": null,
    "url": "https://example.testrail.com/index.php?/suites/view/1"
  },
  {
    "id": 2,
    "name": "Regression Test Suite",
    "description": "Test suite for regression testing",
    "project_id": 1,
    "is_master": false,
    "is_baseline": false,
    "is_completed": false,
    "completed_on": null,
    "url": "https://example.testrail.com/index.php?/suites/view/2"
  }
]
```

### Add Suite

```
POST index.php?/api/v2/add_suite/{project_id}
```

Creates a new test suite.

#### Parameters:

- `project_id` (required): The ID of the project

#### Request Fields:

- `name` (required): The name of the new test suite
- `description`: The description of the new test suite

#### Request Example:

```json
{
  "name": "API Test Suite",
  "description": "Test suite for API testing"
}
```

### Update Suite

```
POST index.php?/api/v2/update_suite/{suite_id}
```

Updates an existing test suite.

#### Parameters:

- `suite_id` (required): The ID of the test suite

#### Request Fields:

- `name`: The name of the test suite
- `description`: The description of the test suite

### Delete Suite

```
POST index.php?/api/v2/delete_suite/{suite_id}
```

Deletes an existing test suite.

#### Parameters:

- `suite_id` (required): The ID of the test suite to delete

**Note:** Deleting a test suite also deletes all test cases, sections, and test runs in the test suite.

## Python Example

Here's a Python example for working with test suites:

```python
import requests
import json

class TestRailAPI:
    def __init__(self, url, email, api_key):
        self.url = url
        self.email = email
        self.api_key = api_key
        
    def get_suites(self, project_id):
        api_url = f"{self.url}/index.php?/api/v2/get_suites/{project_id}"
        
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'}
        )
        
        return response.json()
    
    def get_suite(self, suite_id):
        api_url = f"{self.url}/index.php?/api/v2/get_suite/{suite_id}"
        
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'}
        )
        
        return response.json()
    
    def add_suite(self, project_id, name, description=None):
        api_url = f"{self.url}/index.php?/api/v2/add_suite/{project_id}"
        
        payload = {
            "name": name
        }
        
        if description:
            payload["description"] = description
        
        response = requests.post(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        
        return response.json()
    
    def update_suite(self, suite_id, name=None, description=None):
        api_url = f"{self.url}/index.php?/api/v2/update_suite/{suite_id}"
        
        payload = {}
        
        if name:
            payload["name"] = name
            
        if description is not None:
            payload["description"] = description
        
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

# Get all test suites in a project
suites = testrail.get_suites(1)
print("Test suites in project:")
for suite in suites:
    master = " (master)" if suite['is_master'] else ""
    print(f"- {suite['name']}{master}")

# Create a new test suite
new_suite = testrail.add_suite(
    project_id=1,
    name="Mobile Test Suite",
    description="Test suite for mobile application testing"
)
print(f"Created test suite: {new_suite['name']} (ID: {new_suite['id']})")

# Update a test suite
updated_suite = testrail.update_suite(
    suite_id=new_suite['id'],
    description="Test suite for iOS and Android mobile application testing"
)
print(f"Updated test suite description for: {updated_suite['name']}")
```

## Test Suite Project Types in TestRail

TestRail supports three different project types with different suite modes:

1. **Single Suite Mode (1)**: Projects have only one test suite.
2. **Single Suite + Baselines Mode (2)**: Projects have one test suite with the ability to create baselines (snapshots).
3. **Multiple Suites Mode (3)**: Projects can have multiple test suites.

The Suites API is most relevant for projects using Multiple Suites Mode (3).

## Best Practices

1. Use descriptive names for test suites to clearly identify their purpose
2. Create separate test suites for distinct testing areas or objectives
3. Include detailed descriptions to help users understand the scope of each test suite
4. Consider organizing test suites by platform, feature area, or testing type
5. Plan test suite structure carefully as it impacts test case organization
6. Limit the number of test suites to maintain clarity and avoid confusion
7. Regularly review and refine your test suite structure as your application evolves
8. Document test suite organization and naming conventions for your team

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
