# Groups API

This document describes how to work with user groups in TestRail using the API.

## Overview

User groups in TestRail allow you to organize users and assign permissions to multiple users at once. The API provides methods to retrieve and manage these groups.

## API Endpoints

### Get Groups

```
GET index.php?/api/v2/get_groups
```

Returns a list of all user groups.

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
  "groups": [
    {
      "id": 1,
      "name": "Administrators",
      "is_default": false
    },
    {
      "id": 2,
      "name": "Testers",
      "is_default": true
    }
  ]
}
```

### Get Group

```
GET index.php?/api/v2/get_group/{group_id}
```

Returns an existing user group.

#### Parameters:

- `group_id` (required): The ID of the user group

#### Response Example:

```json
{
  "id": 1,
  "name": "Administrators",
  "is_default": false
}
```

### Add Group

```
POST index.php?/api/v2/add_group
```

Creates a new user group.

#### Request Fields:

- `name` (required): The name of the new group
- `is_default` (optional): Set to true to make this the default group for new users

#### Request Example:

```json
{
  "name": "QA Team",
  "is_default": false
}
```

### Update Group

```
POST index.php?/api/v2/update_group/{group_id}
```

Updates an existing user group.

#### Parameters:

- `group_id` (required): The ID of the user group

#### Request Fields:

- `name` (required): The new name for the group
- `is_default` (optional): Set to true to make this the default group for new users

### Delete Group

```
POST index.php?/api/v2/delete_group/{group_id}
```

Deletes an existing user group.

#### Parameters:

- `group_id` (required): The ID of the user group to delete

## Python Example

Here's a Python example for working with user groups:

```python
import requests
import json

class TestRailAPI:
    def __init__(self, url, email, api_key):
        self.url = url
        self.email = email
        self.api_key = api_key
        
    def get_groups(self):
        api_url = f"{self.url}/index.php?/api/v2/get_groups"
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'}
        )
        return response.json()
    
    def add_group(self, name, is_default=False):
        api_url = f"{self.url}/index.php?/api/v2/add_group"
        
        payload = {
            "name": name,
            "is_default": is_default
        }
        
        response = requests.post(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        
        return response.json()
    
    def update_group(self, group_id, name, is_default=None):
        api_url = f"{self.url}/index.php?/api/v2/update_group/{group_id}"
        
        payload = {
            "name": name
        }
        
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

# Get all groups
groups = testrail.get_groups()
print("Existing groups:")
for group in groups['groups']:
    default_marker = " (default)" if group['is_default'] else ""
    print(f"- {group['name']}{default_marker}")

# Create a new group
new_group = testrail.add_group("Development Team")
print(f"Created new group: {new_group['name']} (ID: {new_group['id']})")

# Update a group
updated_group = testrail.update_group(new_group['id'], "Dev Team")
print(f"Updated group name to: {updated_group['name']}")
```

## Managing Group Permissions

Group permissions are managed through TestRail's administration interface. The API doesn't currently provide direct methods to modify permission settings for groups.

## Best Practices

1. Create groups based on roles and responsibilities in your testing process
2. Use descriptive group names to clearly identify their purpose
3. Limit the number of users with administrative permissions
4. Review group memberships and permissions regularly
5. Consider setting a default group for new users to streamline onboarding

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
