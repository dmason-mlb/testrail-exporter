# Shared Steps API

This document describes how to work with shared steps in TestRail using the API.

## Overview

Shared steps in TestRail allow you to create reusable test steps that can be included in multiple test cases. The API provides methods to retrieve and manage these shared steps.

## API Endpoints

### Get Shared Step

```
GET index.php?/api/v2/get_shared_step/{shared_step_id}
```

Returns an existing shared step.

#### Parameters:

- `shared_step_id` (required): The ID of the shared step

#### Response Example:

```json
{
  "id": 1,
  "project_id": 1,
  "title": "Login to Application",
  "steps": [
    {
      "content": "Navigate to the login page",
      "expected": "Login page is displayed"
    },
    {
      "content": "Enter username and password",
      "expected": "Credentials are entered"
    },
    {
      "content": "Click the Login button",
      "expected": "User is logged in and redirected to the dashboard"
    }
  ],
  "refs": "REQ-1",
  "created_by": 1,
  "created_on": 1646317844,
  "updated_by": 1,
  "updated_on": 1646317844
}
```

### Get Shared Steps

```
GET index.php?/api/v2/get_shared_steps/{project_id}
```

Returns a list of shared steps for a project.

#### Parameters:

- `project_id` (required): The ID of the project

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
  "shared_steps": [
    {
      "id": 1,
      "project_id": 1,
      "title": "Login to Application",
      "steps_count": 3,
      "refs": "REQ-1",
      "created_by": 1,
      "created_on": 1646317844,
      "updated_by": 1,
      "updated_on": 1646317844
    },
    {
      "id": 2,
      "project_id": 1,
      "title": "Logout from Application",
      "steps_count": 2,
      "refs": "REQ-2",
      "created_by": 1,
      "created_on": 1646318000,
      "updated_by": 1,
      "updated_on": 1646318000
    }
  ]
}
```

### Add Shared Step

```
POST index.php?/api/v2/add_shared_step/{project_id}
```

Creates a new shared step.

#### Parameters:

- `project_id` (required): The ID of the project

#### Request Fields:

- `title` (required): The title of the shared step
- `steps` (required): An array of step objects with content and expected fields
- `refs`: A comma-separated list of references/requirements

#### Request Example:

```json
{
  "title": "Reset Password",
  "steps": [
    {
      "content": "Click 'Forgot Password' link",
      "expected": "Password reset page is displayed"
    },
    {
      "content": "Enter email address",
      "expected": "Email field is populated"
    },
    {
      "content": "Click 'Reset Password' button",
      "expected": "Password reset email is sent and confirmation message is displayed"
    }
  ],
  "refs": "REQ-3"
}
```

### Update Shared Step

```
POST index.php?/api/v2/update_shared_step/{shared_step_id}
```

Updates an existing shared step.

#### Parameters:

- `shared_step_id` (required): The ID of the shared step

#### Request Fields:

- `title`: The title of the shared step
- `steps`: An array of step objects with content and expected fields
- `refs`: A comma-separated list of references/requirements

### Delete Shared Step

```
POST index.php?/api/v2/delete_shared_step/{shared_step_id}
```

Deletes an existing shared step.

#### Parameters:

- `shared_step_id` (required): The ID of the shared step to delete

## Python Example

Here's a Python example for working with shared steps:

```python
import requests
import json

class TestRailAPI:
    def __init__(self, url, email, api_key):
        self.url = url
        self.email = email
        self.api_key = api_key
        
    def get_shared_steps(self, project_id):
        api_url = f"{self.url}/index.php?/api/v2/get_shared_steps/{project_id}"
        
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'}
        )
        
        return response.json()
    
    def get_shared_step(self, shared_step_id):
        api_url = f"{self.url}/index.php?/api/v2/get_shared_step/{shared_step_id}"
        
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'}
        )
        
        return response.json()
    
    def add_shared_step(self, project_id, title, steps, refs=None):
        api_url = f"{self.url}/index.php?/api/v2/add_shared_step/{project_id}"
        
        payload = {
            "title": title,
            "steps": steps
        }
        
        if refs:
            payload["refs"] = refs
        
        response = requests.post(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        
        return response.json()
    
    def update_shared_step(self, shared_step_id, title=None, steps=None, refs=None):
        api_url = f"{self.url}/index.php?/api/v2/update_shared_step/{shared_step_id}"
        
        payload = {}
        
        if title:
            payload["title"] = title
            
        if steps:
            payload["steps"] = steps
            
        if refs is not None:
            payload["refs"] = refs
        
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

# Get all shared steps in a project
shared_steps = testrail.get_shared_steps(1)
print(f"Found {len(shared_steps['shared_steps'])} shared steps in project")

# Create a new shared step
login_steps = [
    {
        "content": "Navigate to the login page",
        "expected": "Login page is displayed"
    },
    {
        "content": "Enter username and password",
        "expected": "Credentials are entered"
    },
    {
        "content": "Click the Login button",
        "expected": "User is logged in and redirected to the dashboard"
    }
]

new_shared_step = testrail.add_shared_step(
    project_id=1,
    title="Login to Application",
    steps=login_steps,
    refs="REQ-1"
)

print(f"Created shared step: {new_shared_step['title']} (ID: {new_shared_step['id']})")

# Get details of a shared step
step_details = testrail.get_shared_step(new_shared_step['id'])
print(f"Shared step '{step_details['title']}' has {len(step_details['steps'])} steps")

# Update a shared step
updated_login_steps = login_steps.copy()
updated_login_steps.append({
    "content": "Verify user profile is displayed",
    "expected": "User's profile information is shown"
})

updated_shared_step = testrail.update_shared_step(
    shared_step_id=new_shared_step['id'],
    steps=updated_login_steps
)

print(f"Updated shared step now has {len(updated_shared_step['steps'])} steps")
```

## Using Shared Steps in Test Cases

Once you've created shared steps, you can reference them in test cases:

```python
def add_case_with_shared_steps(section_id, title, shared_step_ids, additional_steps=None):
    """
    Creates a test case that includes shared steps.
    
    shared_step_ids: A list of shared step IDs to include
    additional_steps: Optional list of additional step objects
    """
    api_url = f"{url}/index.php?/api/v2/add_case/{section_id}"
    
    # Format for including shared steps
    steps = []
    
    # Add shared steps references
    for step_id in shared_step_ids:
        steps.append({
            "shared_step_id": step_id
        })
    
    # Add additional steps if provided
    if additional_steps:
        steps.extend(additional_steps)
    
    payload = {
        "title": title,
        "custom_steps_separated": steps
    }
    
    response = requests.post(
        api_url,
        auth=(email, api_key),
        headers={'Content-Type': 'application/json'},
        data=json.dumps(payload)
    )
    
    return response.json()

# Example usage:
login_shared_step_id = new_shared_step['id']

additional_steps = [
    {
        "content": "Navigate to the Profile page",
        "expected": "Profile page is displayed"
    },
    {
        "content": "Update profile information",
        "expected": "Profile is updated and success message is displayed"
    }
]

test_case = add_case_with_shared_steps(
    section_id=1,
    title="Update User Profile",
    shared_step_ids=[login_shared_step_id],
    additional_steps=additional_steps
)

print(f"Created test case with shared steps: {test_case['title']} (ID: {test_case['id']})")
```

## Finding Cases Using a Shared Step

To find all test cases that use a particular shared step:

```python
def find_cases_using_shared_step(project_id, shared_step_id):
    """
    Finds all test cases that use a specific shared step.
    """
    # Get all test cases in the project
    api_url = f"{url}/index.php?/api/v2/get_cases/{project_id}"
    
    response = requests.get(
        api_url,
        auth=(email, api_key),
        headers={'Content-Type': 'application/json'}
    )
    
    cases = response.json()['cases']
    
    # Filter cases that use the shared step
    cases_using_step = []
    
    for case in cases:
        # Check if the case has custom_steps_separated field and it contains steps
        if 'custom_steps_separated' in case and case['custom_steps_separated']:
            # Parse the steps to find shared step references
            steps = case['custom_steps_separated']
            
            for step in steps:
                if isinstance(step, dict) and 'shared_step_id' in step and step['shared_step_id'] == shared_step_id:
                    cases_using_step.append(case)
                    break
    
    return cases_using_step

# Example usage:
cases = find_cases_using_shared_step(1, login_shared_step_id)
print(f"Found {len(cases)} test cases using the Login shared step:")
for case in cases:
    print(f"- {case['title']} (ID: {case['id']})")
```

## Best Practices

1. Create shared steps for commonly repeated sequences of actions
2. Keep shared steps focused on specific, reusable functionality
3. Use clear, descriptive titles for shared steps
4. Include detailed expected results for each step
5. Update shared steps carefully, considering the impact on all test cases that use them
6. Link shared steps to requirements or user stories using the refs field
7. Consider creating a library of shared steps for common functionality across projects
8. Document shared steps thoroughly to encourage reuse

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
