# Priorities API

This document describes how to work with test case priorities in TestRail using the API.

## Overview

Priorities in TestRail define the importance of test cases. The API provides methods to retrieve and manage these priorities.

## API Endpoints

### Get Priorities

```
GET index.php?/api/v2/get_priorities
```

Returns a list of available test case priorities.

#### Response Example:

```json
[
  {
    "id": 1,
    "name": "Critical",
    "short_name": "Crit",
    "priority": 3,
    "is_default": false
  },
  {
    "id": 2,
    "name": "High",
    "short_name": "High",
    "priority": 2,
    "is_default": true
  },
  {
    "id": 3,
    "name": "Medium",
    "short_name": "Med",
    "priority": 1,
    "is_default": false
  },
  {
    "id": 4,
    "name": "Low",
    "short_name": "Low",
    "priority": 0,
    "is_default": false
  }
]
```

### Add Priority

```
POST index.php?/api/v2/add_priority
```

Creates a new test case priority.

#### Request Fields:

- `name` (required): The name of the new priority
- `short_name` (required): The short name or abbreviation of the priority
- `priority` (required): The priority value (used for ordering, higher values represent higher priorities)
- `is_default`: Whether this is the default priority for new test cases

#### Request Example:

```json
{
  "name": "Urgent",
  "short_name": "Urg",
  "priority": 4,
  "is_default": false
}
```

### Update Priority

```
POST index.php?/api/v2/update_priority/{priority_id}
```

Updates an existing priority.

#### Parameters:

- `priority_id` (required): The ID of the priority

#### Request Fields:

- `name`: The updated name of the priority
- `short_name`: The updated short name of the priority
- `priority`: The updated priority value
- `is_default`: Whether this is the default priority for new test cases

### Delete Priority

```
POST index.php?/api/v2/delete_priority/{priority_id}
```

Deletes an existing priority.

#### Parameters:

- `priority_id` (required): The ID of the priority to delete

## Python Example

Here's a Python example for working with priorities:

```python
import requests
import json

class TestRailAPI:
    def __init__(self, url, email, api_key):
        self.url = url
        self.email = email
        self.api_key = api_key
        
    def get_priorities(self):
        api_url = f"{self.url}/index.php?/api/v2/get_priorities"
        
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'}
        )
        
        return response.json()
    
    def add_priority(self, name, short_name, priority, is_default=False):
        api_url = f"{self.url}/index.php?/api/v2/add_priority"
        
        payload = {
            "name": name,
            "short_name": short_name,
            "priority": priority,
            "is_default": is_default
        }
        
        response = requests.post(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        
        return response.json()
    
    def update_priority(self, priority_id, name=None, short_name=None, priority=None, is_default=None):
        api_url = f"{self.url}/index.php?/api/v2/update_priority/{priority_id}"
        
        payload = {}
        
        if name:
            payload["name"] = name
            
        if short_name:
            payload["short_name"] = short_name
            
        if priority is not None:
            payload["priority"] = priority
            
        if is_default is not None:
            payload["is_default"] = is_default
        
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

# Get all priorities
priorities = testrail.get_priorities()
print("Available priorities (highest to lowest):")
for priority in sorted(priorities, key=lambda p: p['priority'], reverse=True):
    default_marker = " (default)" if priority['is_default'] else ""
    print(f"- {priority['name']} ({priority['short_name']}){default_marker}")

# Add a new priority
new_priority = testrail.add_priority(
    name="Blocker",
    short_name="Blk",
    priority=5
)
print(f"Created new priority: {new_priority['name']} (ID: {new_priority['id']})")

# Update a priority
updated_priority = testrail.update_priority(
    priority_id=new_priority['id'],
    short_name="BLK"
)
print(f"Updated priority short name to: {updated_priority['short_name']}")
```

## Using Priorities with Test Cases

When creating or updating test cases, you can specify the priority using the `priority_id` field:

```python
def add_case(self, section_id, title, priority_id=None):
    api_url = f"{self.url}/index.php?/api/v2/add_case/{section_id}"
    
    payload = {
        "title": title
    }
    
    if priority_id:
        payload["priority_id"] = priority_id
    
    response = requests.post(
        api_url,
        auth=(self.email, self.api_key),
        headers={'Content-Type': 'application/json'},
        data=json.dumps(payload)
    )
    
    return response.json()

# Find the ID for "Critical" priority
critical_id = next((p['id'] for p in priorities if p['name'] == 'Critical'), None)

if critical_id:
    # Create a critical test case
    critical_case = testrail.add_case(
        section_id=1,
        title="Verify secure payment processing",
        priority_id=critical_id
    )
    print(f"Created critical test case: {critical_case['title']}")
```

## Best Practices

1. Use a consistent set of priorities across all projects
2. Limit the number of priority levels to maintain clarity (4-5 is typically sufficient)
3. Use clear naming conventions that indicate the relative importance
4. Set appropriate default priorities to streamline test case creation
5. Consider using priorities in combination with other fields like type and status for comprehensive filtering

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
