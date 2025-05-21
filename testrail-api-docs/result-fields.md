# Result Fields API

This document describes how to work with result fields in TestRail using the API.

## Overview

Result fields define the attributes and custom fields that can be used for test results in TestRail. The API provides methods to retrieve and manage these fields.

## API Endpoints

### Get Result Fields

```
GET index.php?/api/v2/get_result_fields
```

Returns a list of available result fields.

#### Response Example:

```json
[
  {
    "id": 1,
    "type_id": 3,
    "name": "comment",
    "system_name": "comment",
    "label": "Comment",
    "description": "The comment or error message for the test result",
    "configs": [
      {
        "context": {
          "is_global": true,
          "project_ids": null
        },
        "options": {
          "is_required": false,
          "format": "markdown",
          "rows": "6"
        },
        "id": "1"
      }
    ],
    "display_order": 1,
    "is_multi": false,
    "is_active": true,
    "status_id": 1,
    "is_system": true,
    "include_all": true
  },
  {
    "id": 2,
    "type_id": 2,
    "name": "elapsed",
    "system_name": "elapsed",
    "label": "Elapsed",
    "description": "The time it took to execute the test",
    "configs": [
      {
        "context": {
          "is_global": true,
          "project_ids": null
        },
        "options": {
          "is_required": false,
          "default_value": ""
        },
        "id": "2"
      }
    ],
    "display_order": 2,
    "is_multi": false,
    "is_active": true,
    "status_id": 1,
    "is_system": true,
    "include_all": true
  }
]
```

### Add Result Field

```
POST index.php?/api/v2/add_result_field
```

Creates a new result field.

#### Request Fields:

- `type` (required): The type identifier for the new field (integer field or a custom field plugin identifier string)
- `name` (required): The name of the new field (used as meta name, e.g. "custom_field")
- `label` (required): The label of the new field (used in the user interface)
- `description`: The description of the new field
- `include_all`: Set flag to true if projects with the field enabled should show the field for all test results
- `template_ids`: An array of template IDs to include the field in
- `configs`: An array of field configurations

### Result Field Types

TestRail supports various field types for result fields:

1. `1` - String
2. `2` - Integer
3. `3` - Text
4. `4` - URL
5. `5` - Checkbox
6. `6` - Dropdown
7. `7` - User
8. `8` - Date
9. `9` - Milestone
10. `10` - Steps
11. `11` - Multi-select
12. `12` - Checked Checkbox

### Update Result Field

```
POST index.php?/api/v2/update_result_field/{field_id}
```

Updates an existing result field.

#### Parameters:

- `field_id` (required): The ID of the result field

#### Request Fields:

Same as `add_result_field`, except for the `type` field which cannot be changed.

### Delete Result Field

```
POST index.php?/api/v2/delete_result_field/{field_id}
```

Deletes an existing result field.

#### Parameters:

- `field_id` (required): The ID of the result field to delete

## Python Example

Here's a Python example for working with result fields:

```python
import requests
import json

class TestRailAPI:
    def __init__(self, url, email, api_key):
        self.url = url
        self.email = email
        self.api_key = api_key
        
    def get_result_fields(self):
        api_url = f"{self.url}/index.php?/api/v2/get_result_fields"
        
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'}
        )
        
        return response.json()
    
    def add_result_field(self, type_id, name, label, description=None, include_all=True, configs=None):
        api_url = f"{self.url}/index.php?/api/v2/add_result_field"
        
        payload = {
            "type": type_id,
            "name": name,
            "label": label,
            "include_all": include_all
        }
        
        if description:
            payload["description"] = description
            
        if configs:
            payload["configs"] = configs
        else:
            # Default configuration
            payload["configs"] = [
                {
                    "context": {
                        "is_global": True,
                        "project_ids": None
                    },
                    "options": {
                        "is_required": False,
                        "default_value": ""
                    }
                }
            ]
        
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

# Get all result fields
result_fields = testrail.get_result_fields()
print("Available result fields:")
for field in result_fields:
    system = " (system)" if field['is_system'] else ""
    print(f"- {field['label']}{system}: {field['description']}")

# Add a custom dropdown field
dropdown_options = {
    "is_required": False,
    "default_value": "",
    "items": "Pass with Minor Issues\nPass with Observations\nPass with Workarounds"
}

configs = [
    {
        "context": {
            "is_global": True,
            "project_ids": None
        },
        "options": dropdown_options
    }
]

new_field = testrail.add_result_field(
    type_id=6,  # Dropdown
    name="custom_pass_type",
    label="Pass Type",
    description="The type of pass result",
    configs=configs
)

print(f"Created new result field: {new_field['label']} (ID: {new_field['id']})")
```

## Using Custom Result Fields

When adding test results, you can include custom result fields:

```python
def add_result_with_custom_fields(test_id, status_id, custom_fields=None):
    api_url = f"{url}/index.php?/api/v2/add_result/{test_id}"
    
    payload = {
        "status_id": status_id
    }
    
    # Add custom fields
    if custom_fields:
        for field_name, field_value in custom_fields.items():
            if not field_name.startswith("custom_"):
                field_name = f"custom_{field_name}"
            payload[field_name] = field_value
    
    response = requests.post(
        api_url,
        auth=(email, api_key),
        headers={'Content-Type': 'application/json'},
        data=json.dumps(payload)
    )
    
    return response.json()

# Example usage:
result = add_result_with_custom_fields(
    test_id=1,
    status_id=1,  # Passed
    custom_fields={
        "pass_type": "Pass with Observations",
        "custom_tester_notes": "Test passed with minor UI inconsistencies"
    }
)

print(f"Added result with custom fields: {result['id']}")
```

## Best Practices

1. Use descriptive names and labels for custom fields
2. Consider the impact of adding or removing fields on existing test results
3. Use appropriate field types for different kinds of data
4. Keep the number of custom fields manageable to avoid cluttering the interface
5. Use global fields for data that spans multiple projects
6. Include clear descriptions for each field to help users understand its purpose
7. Consider required fields carefully to balance data collection with user efficiency

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
