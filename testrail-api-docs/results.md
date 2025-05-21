# Results API

This document describes how to work with test results in TestRail using the API.

## Overview

Test results in TestRail track the outcomes of executed tests. The API provides methods to retrieve and add test results.

## API Endpoints

### Get Results

```
GET index.php?/api/v2/get_results/{test_id}
```

Returns a list of test results for a test.

#### Parameters:

- `test_id` (required): The ID of the test
- `limit` (optional): The number of results to return (defaults to 250)
- `offset` (optional): Where to start when returning records (defaults to 0)
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
  "results": [
    {
      "id": 1,
      "test_id": 1,
      "status_id": 1,
      "created_by": 1,
      "created_on": 1646317844,
      "assignedto_id": null,
      "comment": "Test executed successfully",
      "version": "1.0",
      "elapsed": "30s",
      "defects": null,
      "custom_field1": "Value 1"
    },
    {
      "id": 2,
      "test_id": 1,
      "status_id": 5,
      "created_by": 1,
      "created_on": 1646318000,
      "assignedto_id": null,
      "comment": "Test failed - could not log in with valid credentials",
      "version": "1.1",
      "elapsed": "45s",
      "defects": "BUG-123",
      "custom_field1": "Value 1"
    }
  ]
}
```

### Get Results for Case

```
GET index.php?/api/v2/get_results_for_case/{run_id}/{case_id}
```

Returns a list of test results for a test case in a test run.

#### Parameters:

- `run_id` (required): The ID of the test run
- `case_id` (required): The ID of the test case
- `limit` (optional): The number of results to return (defaults to 250)
- `offset` (optional): Where to start when returning records (defaults to 0)
- `status_id` (optional): A comma-separated list of status IDs to filter by

### Get Results for Run

```
GET index.php?/api/v2/get_results_for_run/{run_id}
```

Returns a list of test results for a test run.

#### Parameters:

- `run_id` (required): The ID of the test run
- `created_after` (optional): Only return test results created after this timestamp
- `created_before` (optional): Only return test results created before this timestamp
- `created_by` (optional): A comma-separated list of creators (user IDs) to filter by
- `status_id` (optional): A comma-separated list of status IDs to filter by
- `limit` (optional): The number of results to return (defaults to 250)
- `offset` (optional): Where to start when returning records (defaults to 0)

### Add Result

```
POST index.php?/api/v2/add_result/{test_id}
```

Adds a new test result for a test.

#### Parameters:

- `test_id` (required): The ID of the test

#### Request Fields:

- `status_id` (required): The ID of the test status
- `comment`: The comment or error message for the test result
- `version`: The version or build tested
- `elapsed`: The time it took to execute the test (e.g. "30s" or "1m 45s")
- `defects`: A comma-separated list of defects linked to this test result
- `assignedto_id`: The ID of the user this test should be assigned to

Custom fields are also supported and must be submitted with their system name, prefixed with 'custom_'.

#### Request Example:

```json
{
  "status_id": 1,
  "comment": "Test executed successfully",
  "version": "1.0",
  "elapsed": "30s",
  "defects": "BUG-123",
  "custom_steps_results": [
    {
      "content": "Step 1",
      "expected": "Expected Result 1",
      "actual": "Actual Result 1",
      "status_id": 1
    },
    {
      "content": "Step 2",
      "expected": "Expected Result 2",
      "actual": "Actual Result 2",
      "status_id": 1
    }
  ]
}
```

### Add Result for Case

```
POST index.php?/api/v2/add_result_for_case/{run_id}/{case_id}
```

Adds a new test result for a test case in a test run.

#### Parameters:

- `run_id` (required): The ID of the test run
- `case_id` (required): The ID of the test case

#### Request Fields:

Same as `add_result`.

### Add Results

```
POST index.php?/api/v2/add_results/{test_id}
```

Adds multiple test results for a test.

#### Parameters:

- `test_id` (required): The ID of the test

#### Request Fields:

- `results` (required): An array of test results, each with the same fields as `add_result`

#### Request Example:

```json
{
  "results": [
    {
      "status_id": 1,
      "comment": "Test executed successfully",
      "version": "1.0",
      "elapsed": "30s"
    },
    {
      "status_id": 5,
      "comment": "Test failed - could not log in with valid credentials",
      "version": "1.1",
      "elapsed": "45s",
      "defects": "BUG-123"
    }
  ]
}
```

### Add Results for Cases

```
POST index.php?/api/v2/add_results_for_cases/{run_id}
```

Adds test results for multiple test cases in a test run.

#### Parameters:

- `run_id` (required): The ID of the test run

#### Request Fields:

- `results` (required): An array of test results, each with the same fields as `add_result` plus a `case_id` field

#### Request Example:

```json
{
  "results": [
    {
      "case_id": 1,
      "status_id": 1,
      "comment": "Test executed successfully",
      "version": "1.0"
    },
    {
      "case_id": 2,
      "status_id": 5,
      "comment": "Test failed - could not save changes",
      "version": "1.0",
      "defects": "BUG-124"
    }
  ]
}
```

## Python Example

Here's a Python example for working with test results:

```python
import requests
import json

class TestRailAPI:
    def __init__(self, url, email, api_key):
        self.url = url
        self.email = email
        self.api_key = api_key
        
    def get_results_for_run(self, run_id, status_id=None, limit=None):
        api_url = f"{self.url}/index.php?/api/v2/get_results_for_run/{run_id}"
        
        params = {}
        if status_id:
            params['status_id'] = status_id
        if limit:
            params['limit'] = limit
            
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'},
            params=params
        )
        
        return response.json()
    
    def add_result(self, test_id, status_id, comment=None, version=None, elapsed=None, defects=None):
        api_url = f"{self.url}/index.php?/api/v2/add_result/{test_id}"
        
        payload = {
            "status_id": status_id
        }
        
        if comment:
            payload["comment"] = comment
            
        if version:
            payload["version"] = version
            
        if elapsed:
            payload["elapsed"] = elapsed
            
        if defects:
            payload["defects"] = defects
        
        response = requests.post(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        
        return response.json()
    
    def add_results_for_cases(self, run_id, results):
        api_url = f"{self.url}/index.php?/api/v2/add_results_for_cases/{run_id}"
        
        payload = {
            "results": results
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

# Get passed results for a run
passed_results = testrail.get_results_for_run(1, status_id=1)
print(f"Found {len(passed_results['results'])} passed results")

# Add a result for a test
result = testrail.add_result(
    test_id=1,
    status_id=1,  # Passed
    comment="Test executed successfully",
    version="1.0",
    elapsed="45s"
)
print(f"Added result ID: {result['id']}")

# Add results for multiple cases
case_results = [
    {
        "case_id": 1,
        "status_id": 1,
        "comment": "Login successful",
        "version": "1.0",
        "elapsed": "30s"
    },
    {
        "case_id": 2,
        "status_id": 1,
        "comment": "Profile update successful",
        "version": "1.0",
        "elapsed": "45s"
    }
]

results = testrail.add_results_for_cases(run_id=1, results=case_results)
print(f"Added {len(results)} results")
```

## Submitting Automated Test Results

A common use case for the Results API is submitting automated test results. Here's an example of how to do this:

```python
import requests
import json
import time

def submit_automated_test_results(url, email, api_key, run_id, test_results):
    """
    Submits automated test results to TestRail.
    
    test_results: A list of dictionaries with the following format:
    {
        'case_id': 123,        # The ID of the test case
        'status_name': 'passed',  # Status name (passed, failed, blocked, etc.)
        'comment': 'Test log...',  # Test log or comment
        'elapsed': '45s',        # Test execution time
        'version': '1.0'        # Version being tested
    }
    """
    # Map status names to TestRail status IDs
    status_map = {
        'passed': 1,
        'blocked': 2,
        'untested': 3,
        'retest': 4,
        'failed': 5
    }
    
    # Format the results for TestRail API
    formatted_results = []
    for result in test_results:
        status_id = status_map.get(result['status_name'].lower(), 3)  # Default to untested
        
        formatted_result = {
            'case_id': result['case_id'],
            'status_id': status_id,
            'comment': result.get('comment', ''),
            'elapsed': result.get('elapsed', ''),
            'version': result.get('version', '')
        }
        
        formatted_results.append(formatted_result)
    
    # Submit the results
    api_url = f"{url}/index.php?/api/v2/add_results_for_cases/{run_id}"
    
    payload = {
        "results": formatted_results
    }
    
    response = requests.post(
        api_url,
        auth=(email, api_key),
        headers={'Content-Type': 'application/json'},
        data=json.dumps(payload)
    )
    
    return response.json()

# Example usage:
automated_results = [
    {
        'case_id': 1,
        'status_name': 'passed',
        'comment': 'Login test passed successfully',
        'elapsed': '12s',
        'version': '1.0'
    },
    {
        'case_id': 2,
        'status_name': 'failed',
        'comment': 'Logout test failed - session remained active',
        'elapsed': '10s',
        'version': '1.0'
    }
]

results = submit_automated_test_results(
    url="https://example.testrail.com",
    email="your_email@example.com",
    api_key="your_api_key",
    run_id=1,
    test_results=automated_results
)

print(f"Submitted {len(results)} automated test results")
```

## Best Practices

1. Use bulk methods (`add_results_for_cases`) when submitting multiple test results to reduce API calls
2. Include meaningful comments and details in test results
3. Link test results to defects when failures occur
4. Properly format the elapsed time (e.g., "30s", "1m 45s")
5. Consider including version information to track results across builds
6. Use custom fields effectively to capture additional test data
7. Implement error handling and retries for API failures

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
