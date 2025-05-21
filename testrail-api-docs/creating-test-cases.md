# Creating Test Cases via the API

This document describes how to create test cases in TestRail using the API.

## Overview

TestRail's API allows you to programmatically create test cases. This can be useful for:
- Importing test cases from other systems
- Creating test cases based on requirements
- Automating test case creation for large projects

## Creating a Test Case

To create a test case, use the `add_case` endpoint:

```
POST index.php?/api/v2/add_case/{section_id}
```

### Required Parameters

- `section_id`: The ID of the section where the test case should be created

### Basic Request Example

```json
{
  "title": "My New Test Case",
  "type_id": 1,
  "priority_id": 2,
  "template_id": 1
}
```

### Response

If successful, this method returns the new test case using the same response format as `get_case`.

### System Fields

The following system fields are supported:

- `title` (required): The title of the test case
- `type_id`: The ID of the case type
- `priority_id`: The ID of the case priority
- `estimate`: The estimate, e.g. "30s" or "1m 45s"
- `milestone_id`: The ID of the milestone to link the test case to
- `refs`: A comma-separated list of references/requirements

### Custom Fields

Custom field parameters are also supported and must be submitted with their system name, prefixed with 'custom_'. For example:

```json
{
  "title": "My New Test Case",
  "type_id": 1,
  "priority_id": 2,
  "custom_steps": "Step 1: Do this\nStep 2: Do that",
  "custom_expected": "Expected result"
}
```

## Creating Multiple Test Cases

To create multiple test cases efficiently, you can use the API in a loop, but be mindful of rate limits on TestRail Cloud. Consider adding delays between requests or using bulk operations where available.

## Python Example

Here's a Python example for creating a test case:

```python
import requests
import json

def create_test_case(url, email, api_key, section_id, title, type_id=1, priority_id=2):
    api_url = f"{url}/index.php?/api/v2/add_case/{section_id}"
    payload = {
        "title": title,
        "type_id": type_id,
        "priority_id": priority_id
    }
    
    response = requests.post(
        api_url,
        auth=(email, api_key),
        headers={'Content-Type': 'application/json'},
        data=json.dumps(payload)
    )
    
    return response.json()

# Usage example
case = create_test_case(
    url="https://example.testrail.com",
    email="your_email@example.com",
    api_key="your_api_key",
    section_id=123,
    title="Login with valid credentials"
)

print(f"Created case ID: {case['id']}")
```

## Best Practices

1. Use consistent case types and priorities
2. Include detailed steps and expected results
3. Link test cases to requirements or user stories using the `refs` field
4. Organize test cases into appropriate sections
5. Include relevant custom fields based on your project's configuration

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
