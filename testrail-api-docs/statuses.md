# Statuses API

This document describes how to work with test statuses in TestRail using the API.

## Overview

Test statuses in TestRail define the possible outcomes of test executions. The API provides methods to retrieve and manage these statuses.

## API Endpoints

### Get Statuses

```
GET index.php?/api/v2/get_statuses
```

Returns a list of available test statuses.

#### Response Example:

```json
[
  {
    "id": 1,
    "name": "Passed",
    "label": "Passed",
    "color_bright": 12709313,
    "color_dark": 6667107,
    "color_medium": 9820525,
    "is_system": true,
    "is_untested": false,
    "is_final": true
  },
  {
    "id": 2,
    "name": "Blocked",
    "label": "Blocked",
    "color_bright": 16631751,
    "color_dark": 14503604,
    "color_medium": 15567677,
    "is_system": true,
    "is_untested": false,
    "is_final": true
  },
  {
    "id": 3,
    "name": "Untested",
    "label": "Untested",
    "color_bright": 15790322,
    "color_dark": 11053224,
    "color_medium": 13421772,
    "is_system": true,
    "is_untested": true,
    "is_final": false
  },
  {
    "id": 4,
    "name": "Retest",
    "label": "Retest",
    "color_bright": 16448250,
    "color_dark": 11743532,
    "color_medium": 14248954,
    "is_system": true,
    "is_untested": false,
    "is_final": false
  },
  {
    "id": 5,
    "name": "Failed",
    "label": "Failed",
    "color_bright": 16631751,
    "color_dark": 14503604,
    "color_medium": 15567677,
    "is_system": true,
    "is_untested": false,
    "is_final": true
  }
]
```

### Add Status

```
POST index.php?/api/v2/add_status
```

Creates a new test status.

#### Request Fields:

- `name` (required): The name of the new status
- `label` (required): The label of the new status
- `color_bright`: The bright color used for the status
- `color_dark`: The dark color used for the status
- `color_medium`: The medium color used for the status
- `is_final`: Whether the status is a final state or not
- `is_untested`: Whether the status represents an untested state

#### Request Example:

```json
{
  "name": "Passed with Observations",
  "label": "Passed*",
  "color_bright": 10730154,
  "color_dark": 6619364,
  "color_medium": 8674758,
  "is_final": true,
  "is_untested": false
}
```

### Update Status

```
POST index.php?/api/v2/update_status/{status_id}
```

Updates an existing test status.

#### Parameters:

- `status_id` (required): The ID of the test status

#### Request Fields:

Same as `add_status`.

### Delete Status

```
POST index.php?/api/v2/delete_status/{status_id}
```

Deletes an existing test status.

#### Parameters:

- `status_id` (required): The ID of the test status to delete

**Note:** System statuses (those with is_system = true) cannot be deleted.

## Python Example

Here's a Python example for working with test statuses:

```python
import requests
import json

class TestRailAPI:
    def __init__(self, url, email, api_key):
        self.url = url
        self.email = email
        self.api_key = api_key
        
    def get_statuses(self):
        api_url = f"{self.url}/index.php?/api/v2/get_statuses"
        
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'}
        )
        
        return response.json()
    
    def add_status(self, name, label, is_final=True, is_untested=False, 
                   color_bright=None, color_dark=None, color_medium=None):
        api_url = f"{self.url}/index.php?/api/v2/add_status"
        
        payload = {
            "name": name,
            "label": label,
            "is_final": is_final,
            "is_untested": is_untested
        }
        
        if color_bright:
            payload["color_bright"] = color_bright
            
        if color_dark:
            payload["color_dark"] = color_dark
            
        if color_medium:
            payload["color_medium"] = color_medium
        
        response = requests.post(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        
        return response.json()
    
    def update_status(self, status_id, name=None, label=None, is_final=None, 
                      is_untested=None, color_bright=None, color_dark=None, color_medium=None):
        api_url = f"{self.url}/index.php?/api/v2/update_status/{status_id}"
        
        payload = {}
        
        if name:
            payload["name"] = name
            
        if label:
            payload["label"] = label
            
        if is_final is not None:
            payload["is_final"] = is_final
            
        if is_untested is not None:
            payload["is_untested"] = is_untested
            
        if color_bright:
            payload["color_bright"] = color_bright
            
        if color_dark:
            payload["color_dark"] = color_dark
            
        if color_medium:
            payload["color_medium"] = color_medium
        
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

# Get all test statuses
statuses = testrail.get_statuses()
print("Available test statuses:")
for status in statuses:
    system = " (system)" if status['is_system'] else ""
    final = " (final)" if status['is_final'] else ""
    untested = " (untested)" if status['is_untested'] else ""
    print(f"- {status['name']}{system}{final}{untested}")

# Create a new custom status
new_status = testrail.add_status(
    name="Passed with Workaround",
    label="Pass*",
    is_final=True,
    is_untested=False,
    color_bright=10730154,
    color_dark=6619364,
    color_medium=8674758
)

print(f"Created new status: {new_status['name']} (ID: {new_status['id']})")

# Update a status
updated_status = testrail.update_status(
    status_id=new_status['id'],
    label="Pass w/Workaround"
)

print(f"Updated status label to: {updated_status['label']}")
```

## Using Test Statuses in Test Results

When adding test results, you specify the status using the `status_id` field:

```python
def add_result(test_id, status_id, comment=None):
    api_url = f"{url}/index.php?/api/v2/add_result/{test_id}"
    
    payload = {
        "status_id": status_id
    }
    
    if comment:
        payload["comment"] = comment
    
    response = requests.post(
        api_url,
        auth=(email, api_key),
        headers={'Content-Type': 'application/json'},
        data=json.dumps(payload)
    )
    
    return response.json()

# Example usage:
# Find the ID for "Passed with Workaround" status
workaround_status_id = new_status['id']

# Add a test result with this status
result = add_result(
    test_id=1,
    status_id=workaround_status_id,
    comment="Test passed, but required a workaround for known issue BUG-123"
)

print(f"Added test result with status: {workaround_status_id}")
```

## Creating Custom Test Statuses

Here's an example of creating a set of custom test statuses for more granular result reporting:

```python
# Custom statuses for different failure types
failure_statuses = [
    {
        "name": "Failed - UI",
        "label": "UI Fail",
        "is_final": True,
        "is_untested": False,
        "color_bright": 16631751,  # Red (same as Failed)
        "color_dark": 14503604,
        "color_medium": 15567677
    },
    {
        "name": "Failed - API",
        "label": "API Fail",
        "is_final": True,
        "is_untested": False,
        "color_bright": 16631751,  # Red (same as Failed)
        "color_dark": 14503604,
        "color_medium": 15567677
    },
    {
        "name": "Failed - Database",
        "label": "DB Fail",
        "is_final": True,
        "is_untested": False,
        "color_bright": 16631751,  # Red (same as Failed)
        "color_dark": 14503604,
        "color_medium": 15567677
    }
]

# Create all the custom failure statuses
created_statuses = []
for status in failure_statuses:
    created = testrail.add_status(
        name=status["name"],
        label=status["label"],
        is_final=status["is_final"],
        is_untested=status["is_untested"],
        color_bright=status["color_bright"],
        color_dark=status["color_dark"],
        color_medium=status["color_medium"]
    )
    created_statuses.append(created)
    print(f"Created status: {created['name']} (ID: {created['id']})")
```

## Best Practices

1. Use standard statuses (Passed, Failed, Blocked, etc.) when possible for consistency
2. Create custom statuses only when they provide meaningful differentiation
3. Choose distinctive and intuitive labels for custom statuses
4. Select appropriate colors that align with your organization's status conventions
5. Consider whether a status should be marked as "final" based on your testing workflow
6. Use comments in test results to provide additional context beyond the status
7. Document custom statuses and their intended use cases for your team
8. Regularly review status usage and refine as needed

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
