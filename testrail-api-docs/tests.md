# Tests API

This document describes how to work with tests in TestRail using the API.

## Overview

Tests in TestRail represent individual instances of test cases within a test run. The API provides methods to retrieve and manage these tests.

## API Endpoints

### Get Test

```
GET index.php?/api/v2/get_test/{test_id}
```

Returns an existing test.

#### Parameters:

- `test_id` (required): The ID of the test

#### Response Example:

```json
{
  "id": 1,
  "case_id": 1,
  "status_id": 1,
  "assignedto_id": 1,
  "run_id": 1,
  "title": "Verify login with valid credentials",
  "template_id": 1,
  "type_id": 1,
  "priority_id": 2,
  "estimate": "30s",
  "estimate_forecast": "45s",
  "refs": null,
  "milestone_id": null,
  "custom_field1": "Value 1",
  "custom_field2": "Value 2"
}
```

### Get Tests

```
GET index.php?/api/v2/get_tests/{run_id}
```

Returns a list of tests for a test run.

#### Parameters:

- `run_id` (required): The ID of the test run
- `status_id` (optional): A comma-separated list of status IDs to filter by

#### Response Example:

```json
{
  "offset": 0,
  "limit": 250,
  "size": 2,
  "_links": {
    "next": null,
    "prev": null
  },
  "tests": [
    {
      "id": 1,
      "case_id": 1,
      "status_id": 1,
      "assignedto_id": 1,
      "run_id": 1,
      "title": "Verify login with valid credentials",
      "template_id": 1,
      "type_id": 1,
      "priority_id": 2,
      "estimate": "30s",
      "estimate_forecast": "45s",
      "refs": null,
      "milestone_id": null,
      "custom_field1": "Value 1",
      "custom_field2": "Value 2"
    },
    {
      "id": 2,
      "case_id": 2,
      "status_id": 3,
      "assignedto_id": null,
      "run_id": 1,
      "title": "Verify login with invalid credentials",
      "template_id": 1,
      "type_id": 1,
      "priority_id": 2,
      "estimate": "30s",
      "estimate_forecast": "45s",
      "refs": null,
      "milestone_id": null,
      "custom_field1": "Value 1",
      "custom_field2": "Value 2"
    }
  ]
}
```

### Update Test

```
POST index.php?/api/v2/update_test/{test_id}
```

Updates an existing test (partial updates are supported).

#### Parameters:

- `test_id` (required): The ID of the test

#### Request Fields:

- `assignedto_id`: The ID of the user the test should be assigned to

### Update Tests

```
POST index.php?/api/v2/update_tests/{run_id}
```

Updates multiple existing tests (partial updates are supported).

#### Parameters:

- `run_id` (required): The ID of the test run

#### Request Fields:

- `test_ids` (required): A comma-separated list of test IDs to update
- `assignedto_id`: The ID of the user the tests should be assigned to

#### Request Example:

```json
{
  "test_ids": [1, 2, 3],
  "assignedto_id": 1
}
```

## Python Example

Here's a Python example for working with tests:

```python
import requests
import json

class TestRailAPI:
    def __init__(self, url, email, api_key):
        self.url = url
        self.email = email
        self.api_key = api_key
        
    def get_tests(self, run_id, status_id=None):
        api_url = f"{self.url}/index.php?/api/v2/get_tests/{run_id}"
        
        params = {}
        if status_id:
            params['status_id'] = status_id
            
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'},
            params=params
        )
        
        return response.json()
    
    def get_test(self, test_id):
        api_url = f"{self.url}/index.php?/api/v2/get_test/{test_id}"
        
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'}
        )
        
        return response.json()
    
    def update_test(self, test_id, assignedto_id):
        api_url = f"{self.url}/index.php?/api/v2/update_test/{test_id}"
        
        payload = {
            "assignedto_id": assignedto_id
        }
        
        response = requests.post(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        
        return response.json()
    
    def update_tests(self, run_id, test_ids, assignedto_id):
        api_url = f"{self.url}/index.php?/api/v2/update_tests/{run_id}"
        
        payload = {
            "test_ids": test_ids,
            "assignedto_id": assignedto_id
        }
        
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

# Get all tests in a run
tests = testrail.get_tests(1)
print(f"Found {len(tests['tests'])} tests in run")

# Get untested tests
untested_tests = testrail.get_tests(1, status_id=3)  # Status ID 3 = Untested
print(f"Found {len(untested_tests['tests'])} untested tests in run")

# Assign a test to a user
updated_test = testrail.update_test(1, assignedto_id=1)
print(f"Assigned test '{updated_test['title']}' to user ID: {updated_test['assignedto_id']}")

# Assign multiple tests to a user
test_ids = [test['id'] for test in untested_tests['tests']]
if test_ids:
    testrail.update_tests(1, test_ids, assignedto_id=1)
    print(f"Assigned {len(test_ids)} tests to user ID: 1")
```

## Adding Test Results

While the Tests API does not directly support adding test results, you can use the Results API to add results for tests:

```python
def add_result(test_id, status_id, comment=None, elapsed=None, version=None, defects=None):
    """
    Adds a result for a test.
    """
    api_url = f"{url}/index.php?/api/v2/add_result/{test_id}"
    
    payload = {
        "status_id": status_id
    }
    
    if comment:
        payload["comment"] = comment
        
    if elapsed:
        payload["elapsed"] = elapsed
        
    if version:
        payload["version"] = version
        
    if defects:
        payload["defects"] = defects
    
    response = requests.post(
        api_url,
        auth=(email, api_key),
        headers={'Content-Type': 'application/json'},
        data=json.dumps(payload)
    )
    
    return response.json()

# Example usage:
# Get a test
test = testrail.get_test(1)

# Add a result for the test
result = add_result(
    test_id=test['id'],
    status_id=1,  # Passed
    comment="Test completed successfully",
    elapsed="45s",
    version="1.0"
)

print(f"Added result for test '{test['title']}' with status: Passed")
```

## Filtering Tests by Status

Here's an example of getting tests filtered by multiple statuses:

```python
# Get all passed and failed tests
passed_failed_tests = testrail.get_tests(1, status_id="1,5")  # 1=Passed, 5=Failed
print(f"Found {len(passed_failed_tests['tests'])} passed or failed tests")

# Group tests by status
tests_by_status = {}
for test in passed_failed_tests['tests']:
    status_id = test['status_id']
    if status_id not in tests_by_status:
        tests_by_status[status_id] = []
    tests_by_status[status_id].append(test)

# Print count by status
for status_id, tests in tests_by_status.items():
    status_name = "Passed" if status_id == 1 else "Failed"
    print(f"{status_name}: {len(tests)} tests")
```

## Assigning Tests to Multiple Testers

Here's an example of assigning tests to multiple testers in a round-robin fashion:

```python
def assign_tests_round_robin(run_id, tester_ids):
    """
    Assigns tests in a run to multiple testers in a round-robin fashion.
    """
    # Get all tests in the run
    tests = get_tests(run_id)['tests']
    
    if not tests:
        print("No tests found in the run")
        return
    
    if not tester_ids:
        print("No testers provided")
        return
    
    # Assign tests in round-robin fashion
    assignments = {}
    for i, test in enumerate(tests):
        tester_id = tester_ids[i % len(tester_ids)]
        
        if tester_id not in assignments:
            assignments[tester_id] = []
            
        assignments[tester_id].append(test['id'])
    
    # Update tests with assignments
    for tester_id, test_ids in assignments.items():
        update_tests(run_id, test_ids, tester_id)
        print(f"Assigned {len(test_ids)} tests to tester ID: {tester_id}")

# Example usage:
tester_ids = [1, 2, 3]  # IDs of testers to assign tests to
assign_tests_round_robin(1, tester_ids)
```

## Working with Test Custom Fields

Tests include custom fields that were defined for the test case. You can access these custom fields when retrieving tests:

```python
def get_tests_with_custom_field(run_id, custom_field_name, custom_field_value):
    """
    Gets tests that have a specific value for a custom field.
    """
    # Get all tests in the run
    tests = get_tests(run_id)['tests']
    
    # Filter tests by custom field value
    matching_tests = []
    for test in tests:
        if custom_field_name in test and test[custom_field_name] == custom_field_value:
            matching_tests.append(test)
    
    return matching_tests

# Example usage:
automation_tests = get_tests_with_custom_field(1, "custom_automation_type", "2")  # 2 = Automated
print(f"Found {len(automation_tests)} automated tests")
```

## Best Practices

1. Use bulk update methods when modifying multiple tests to reduce API calls
2. Assign tests to appropriate users for clear ownership and accountability
3. Use filtering to focus on tests with specific statuses
4. Consider implementing test assignment strategies based on your testing needs
5. Track test execution progress by monitoring status changes
6. Use custom fields effectively to capture additional test metadata
7. Implement error handling and retries for API failures
8. Regularly review and balance test assignments among team members

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
