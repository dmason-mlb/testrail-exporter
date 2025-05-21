# Case Fields API

This document describes how to work with case fields in TestRail using the API.

## Overview

Case fields define the attributes and custom fields that can be used for test cases in TestRail. The API provides methods to retrieve and manage these fields.

## API Endpoints

### Get Case Fields

```
GET index.php?/api/v2/get_case_fields
```

Returns a list of available case fields.

#### Response Example:

```json
[
  {
    "id": 1,
    "name": "steps",
    "system_name": "custom_steps",
    "label": "Steps",
    "description": "The test case steps",
    "type_id": 11,
    "location_id": 1,
    "display_order": 1,
    "configs": [
      {
        "context": {
          "is_global": true,
          "project_ids": null
        },
        "options": {
          "is_required": false,
          "default_value": "",
          "format": "markdown",
          "rows": "5"
        },
        "id": "1"
      }
    ],
    "is_multi": false,
    "is_active": true,
    "status_id": 1,
    "is_system": true,
    "include_all": true,
    "template_ids": [
      1,
      2,
      3
    ]
  }
]
```

### Add Case Field

```
POST index.php?/api/v2/add_case_field
```

Creates a new case field.

#### Request Fields:

- `type` (required): The type identifier for the new field (integer field or a custom field plugin identifier string)
- `name` (required): The name of the new field (used as meta name, e.g. "custom_field")
- `label` (required): The label of the new field (used in the user interface)
- `description`: The description of the new field
- `include_all`: Set flag to true if projects with the field enabled should show the field for all templates
- `template_ids`: An array of template IDs to include the field in
- `configs`: An array of field configurations

### Case Field Types

TestRail supports various field types for case fields:

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

### Update Case Field

```
POST index.php?/api/v2/update_case_field/{field_id}
```

Updates an existing case field.

#### Parameters:

- `field_id` (required): The ID of the case field

#### Request Fields:

Same as `add_case_field`, except for the `type` field which cannot be changed.

### Delete Case Field

```
POST index.php?/api/v2/delete_case_field/{field_id}
```

Deletes an existing case field.

#### Parameters:

- `field_id` (required): The ID of the case field to delete

## Python Example

Here's a Python example for getting case fields:

```python
import requests

def get_case_fields(url, email, api_key):
    api_url = f"{url}/index.php?/api/v2/get_case_fields"
    
    response = requests.get(
        api_url,
        auth=(email, api_key),
        headers={'Content-Type': 'application/json'}
    )
    
    return response.json()

# Usage example
case_fields = get_case_fields(
    url="https://example.testrail.com",
    email="your_email@example.com",
    api_key="your_api_key"
)

# Print field names and types
for field in case_fields:
    print(f"Field: {field['label']} (Type: {field['type_id']})")
```

## Creating a Custom Dropdown Field

Here's an example of creating a custom dropdown field:

```python
import requests
import json

def add_custom_dropdown_field(url, email, api_key, name, label, options):
    api_url = f"{url}/index.php?/api/v2/add_case_field"
    
    payload = {
        "type": 6,  # Dropdown type
        "name": name,
        "label": label,
        "include_all": True,
        "configs": [
            {
                "context": {
                    "is_global": True,
                    "project_ids": None
                },
                "options": {
                    "is_required": False,
                    "default_value": "",
                    "items": options
                }
            }
        ]
    }
    
    response = requests.post(
        api_url,
        auth=(email, api_key),
        headers={'Content-Type': 'application/json'},
        data=json.dumps(payload)
    )
    
    return response.json()

# Usage example
field = add_custom_dropdown_field(
    url="https://example.testrail.com",
    email="your_email@example.com",
    api_key="your_api_key",
    name="custom_browser",
    label="Browser",
    options="Chrome\nFirefox\nSafari\nEdge"
)

print(f"Created field ID: {field['id']}")
```

## Best Practices

1. Use descriptive names and labels for custom fields
2. Consider the impact of adding or removing fields on existing test cases
3. Use appropriate field types for different kinds of data
4. Keep the number of custom fields manageable to avoid cluttering the interface
5. Use global fields for data that spans multiple projects

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
