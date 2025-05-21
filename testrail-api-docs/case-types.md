# Case Types API

This document describes how to work with case types in TestRail using the API.

## Overview

Case types define the different types of test cases that can be created in TestRail. The API provides methods to retrieve and manage these types.

## API Endpoints

### Get Case Types

```
GET index.php?/api/v2/get_case_types
```

Returns a list of available case types.

#### Response Example:

```json
[
  {
    "id": 1,
    "name": "Functional",
    "is_default": true
  },
  {
    "id": 2,
    "name": "Acceptance",
    "is_default": false
  },
  {
    "id": 3,
    "name": "Performance",
    "is_default": false
  }
]
```

### Add Case Type

```
POST index.php?/api/v2/add_case_type
```

Creates a new case type.

#### Request Fields:

- `name` (required): The name of the new case type
- `is_default` (optional): Set to true to make this case type the default

### Update Case Type

```
POST index.php?/api/v2/update_case_type/{type_id}
```

Updates an existing case type.

#### Parameters:

- `type_id` (required): The ID of the case type

#### Request Fields:

- `name`: The new name of the case type
- `is_default`: Set to true to make this case type the default

### Delete Case Type

```
POST index.php?/api/v2/delete_case_type/{type_id}
```

Deletes an existing case type.

#### Parameters:

- `type_id` (required): The ID of the case type to delete

## Python Example

Here's a Python example for getting case types:

```python
import requests

def get_case_types(url, email, api_key):
    api_url = f"{url}/index.php?/api/v2/get_case_types"
    
    response = requests.get(
        api_url,
        auth=(email, api_key),
        headers={'Content-Type': 'application/json'}
    )
    
    return response.json()

# Usage example
case_types = get_case_types(
    url="https://example.testrail.com",
    email="your_email@example.com",
    api_key="your_api_key"
)

# Print case types
for case_type in case_types:
    default_marker = " (default)" if case_type['is_default'] else ""
    print(f"Type ID: {case_type['id']} - {case_type['name']}{default_marker}")
```

## Creating a Custom Case Type

Here's an example of creating a custom case type:

```python
import requests
import json

def add_case_type(url, email, api_key, name, is_default=False):
    api_url = f"{url}/index.php?/api/v2/add_case_type"
    
    payload = {
        "name": name,
        "is_default": is_default
    }
    
    response = requests.post(
        api_url,
        auth=(email, api_key),
        headers={'Content-Type': 'application/json'},
        data=json.dumps(payload)
    )
    
    return response.json()

# Usage example
new_type = add_case_type(
    url="https://example.testrail.com",
    email="your_email@example.com",
    api_key="your_api_key",
    name="Regression"
)

print(f"Created case type ID: {new_type['id']}")
```

## Using Case Types with Test Cases

When creating or updating test cases, you can specify the case type using the `type_id` field:

```python
import requests
import json

def create_test_case(url, email, api_key, section_id, title, type_id):
    api_url = f"{url}/index.php?/api/v2/add_case/{section_id}"
    
    payload = {
        "title": title,
        "type_id": type_id
    }
    
    response = requests.post(
        api_url,
        auth=(email, api_key),
        headers={'Content-Type': 'application/json'},
        data=json.dumps(payload)
    )
    
    return response.json()

# Usage example
# First, get available case types
case_types = get_case_types(
    url="https://example.testrail.com",
    email="your_email@example.com",
    api_key="your_api_key"
)

# Find the ID for "Performance" case type
performance_type_id = next((t['id'] for t in case_types if t['name'] == 'Performance'), None)

if performance_type_id:
    # Create a new performance test case
    new_case = create_test_case(
        url="https://example.testrail.com",
        email="your_email@example.com",
        api_key="your_api_key",
        section_id=123,
        title="API Response Time Test",
        type_id=performance_type_id
    )
    
    print(f"Created test case ID: {new_case['id']}")
else:
    print("Performance case type not found")
```

## Best Practices

1. Use consistent case types across projects
2. Create case types that align with your testing methodology
3. Consider making the most commonly used case type the default
4. Limit the number of case types to maintain clarity
5. Document the purpose and usage of each case type

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
