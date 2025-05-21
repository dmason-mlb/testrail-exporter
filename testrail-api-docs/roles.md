# Roles API

This document describes how to work with user roles in TestRail using the API.

## Overview

Roles in TestRail define the permissions and access levels for users. The API provides methods to retrieve and manage these roles.

## API Endpoints

### Get Role

```
GET index.php?/api/v2/get_role/{role_id}
```

Returns an existing user role.

#### Parameters:

- `role_id` (required): The ID of the user role

#### Response Example:

```json
{
  "id": 1,
  "name": "Administrator",
  "is_default": false,
  "is_project_admin": true,
  "permissions": {
    "addProject": true,
    "addRun": true,
    "addTestsToRun": true,
    "addTestCase": true,
    "addMilestone": true,
    "addUserToProject": true,
    "assignUserToRun": true,
    "assignUserToCase": true,
    "closeRun": true,
    "closePlan": true,
    "deleteCase": true,
    "deleteCaseResults": true,
    "deleteMilestone": true,
    "deleteAttachment": true,
    "deletePlan": true,
    "deleteProject": true,
    "deleteRun": true,
    "deleteTestResults": true,
    "editCase": true,
    "editCaseCustomField": true,
    "editCaseInBulk": true,
    "editConfig": true,
    "editMilestone": true,
    "editPlan": true,
    "editProject": true,
    "editReports": true,
    "editResultsInBulk": true,
    "editRun": true,
    "editSections": true,
    "editSuite": true,
    "moveCase": true,
    "moveCases": true,
    "viewCases": true,
    "viewMilestones": true,
    "viewPlans": true,
    "viewProjects": true,
    "viewResultsAndActivity": true,
    "viewRuns": true,
    "viewStats": true,
    "viewSuites": true,
    "viewTestsInRun": true
  }
}
```

### Get Roles

```
GET index.php?/api/v2/get_roles
```

Returns a list of all available user roles.

#### Response Example:

```json
{
  "offset": 0,
  "limit": 250,
  "size": 3,
  "_links": {
    "next": null,
    "prev": null
  },
  "roles": [
    {
      "id": 1,
      "name": "Administrator",
      "is_default": false
    },
    {
      "id": 2,
      "name": "Tester",
      "is_default": true
    },
    {
      "id": 3,
      "name": "Read-only",
      "is_default": false
    }
  ]
}
```

### Add Role

```
POST index.php?/api/v2/add_role
```

Creates a new user role.

#### Request Fields:

- `name` (required): The name of the new role
- `is_default` (optional): Set to true to make this the default role for new users
- `is_project_admin` (optional): Set to true to make this role a project admin role
- `permissions` (required): A set of permissions for the role (see example below)

#### Request Example:

```json
{
  "name": "Test Manager",
  "is_default": false,
  "is_project_admin": false,
  "permissions": {
    "addRun": true,
    "addTestsToRun": true,
    "addTestCase": true,
    "addMilestone": true,
    "assignUserToRun": true,
    "assignUserToCase": true,
    "closeRun": true,
    "closePlan": true,
    "editCase": true,
    "editCaseCustomField": true,
    "editCaseInBulk": true,
    "editMilestone": true,
    "editPlan": true,
    "editRun": true,
    "editSections": true,
    "editSuite": true,
    "moveCase": true,
    "moveCases": true,
    "viewCases": true,
    "viewMilestones": true,
    "viewPlans": true,
    "viewProjects": true,
    "viewResultsAndActivity": true,
    "viewRuns": true,
    "viewStats": true,
    "viewSuites": true,
    "viewTestsInRun": true
  }
}
```

### Update Role

```
POST index.php?/api/v2/update_role/{role_id}
```

Updates an existing user role.

#### Parameters:

- `role_id` (required): The ID of the user role

#### Request Fields:

- `name`: The name of the role
- `is_default`: Set to true to make this the default role for new users
- `is_project_admin`: Set to true to make this role a project admin role
- `permissions`: A set of permissions for the role

### Delete Role

```
POST index.php?/api/v2/delete_role/{role_id}
```

Deletes an existing user role.

#### Parameters:

- `role_id` (required): The ID of the user role to delete

## Python Example

Here's a Python example for working with roles:

```python
import requests
import json

class TestRailAPI:
    def __init__(self, url, email, api_key):
        self.url = url
        self.email = email
        self.api_key = api_key
        
    def get_roles(self):
        api_url = f"{self.url}/index.php?/api/v2/get_roles"
        
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'}
        )
        
        return response.json()
    
    def get_role(self, role_id):
        api_url = f"{self.url}/index.php?/api/v2/get_role/{role_id}"
        
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'}
        )
        
        return response.json()
    
    def add_role(self, name, permissions, is_default=False, is_project_admin=False):
        api_url = f"{self.url}/index.php?/api/v2/add_role"
        
        payload = {
            "name": name,
            "is_default": is_default,
            "is_project_admin": is_project_admin,
            "permissions": permissions
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

# Get all roles
roles = testrail.get_roles()
print("Available roles:")
for role in roles['roles']:
    default_marker = " (default)" if role['is_default'] else ""
    print(f"- {role['name']}{default_marker}")

# Get detailed information for a specific role
role_id = roles['roles'][0]['id']
role_details = testrail.get_role(role_id)
print(f"\nPermissions for {role_details['name']}:")
for permission, enabled in role_details['permissions'].items():
    status = "Enabled" if enabled else "Disabled"
    print(f"- {permission}: {status}")

# Create a new role with read-only permissions
read_only_permissions = {
    # View permissions
    "viewCases": True,
    "viewMilestones": True,
    "viewPlans": True,
    "viewProjects": True,
    "viewResultsAndActivity": True,
    "viewRuns": True,
    "viewStats": True,
    "viewSuites": True,
    "viewTestsInRun": True,
    
    # Edit permissions
    "addProject": False,
    "addRun": False,
    "addTestsToRun": False,
    "addTestCase": False,
    "addMilestone": False,
    "addUserToProject": False,
    "assignUserToRun": False,
    "assignUserToCase": False,
    "closeRun": False,
    "closePlan": False,
    "deleteCase": False,
    "deleteCaseResults": False,
    "deleteMilestone": False,
    "deleteAttachment": False,
    "deletePlan": False,
    "deleteProject": False,
    "deleteRun": False,
    "deleteTestResults": False,
    "editCase": False,
    "editCaseCustomField": False,
    "editCaseInBulk": False,
    "editConfig": False,
    "editMilestone": False,
    "editPlan": False,
    "editProject": False,
    "editReports": False,
    "editResultsInBulk": False,
    "editRun": False,
    "editSections": False,
    "editSuite": False,
    "moveCase": False,
    "moveCases": False
}

new_role = testrail.add_role(
    name="Reporting User",
    permissions=read_only_permissions
)

print(f"\nCreated new role: {new_role['name']} (ID: {new_role['id']})")
```

## Role Permissions

TestRail roles include a wide range of permissions. Here are some of the key permission categories:

1. **View Permissions**: Control what users can see (projects, test cases, runs, results, etc.)
2. **Add Permissions**: Control what users can create (projects, test cases, runs, etc.)
3. **Edit Permissions**: Control what users can modify (existing cases, runs, plans, etc.)
4. **Delete Permissions**: Control what users can remove (cases, results, runs, etc.)
5. **Assignment Permissions**: Control who can assign users to tests or runs
6. **Administration Permissions**: Control who can manage projects, users, and settings

When creating a custom role, consider carefully which permissions to grant based on the user's responsibilities.

## Best Practices

1. Create roles based on job functions and responsibilities
2. Apply the principle of least privilege - only grant permissions that are necessary
3. Use descriptive names for roles to clearly identify their purpose
4. Consider creating specialized roles for specific tasks (e.g., "Reporting User", "Test Designer")
5. Review roles and permissions regularly to ensure they remain appropriate
6. Document the purpose and permissions of each role for reference
7. Test new roles to ensure they have the intended access levels

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
