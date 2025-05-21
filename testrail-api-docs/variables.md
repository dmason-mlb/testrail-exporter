# Variables API

This document describes how to work with variables in TestRail using the API.

## Overview

Variables in TestRail allow you to create reusable values that can be referenced across test cases, test runs, and test plans. The API provides methods to retrieve and manage these variables.

## API Endpoints

### Get Variable

```
GET index.php?/api/v2/get_variable/{variable_id}
```

Returns an existing variable.

#### Parameters:

- `variable_id` (required): The ID of the variable

#### Response Example:

```json
{
  "id": 1,
  "project_id": 1,
  "name": "BASE_URL",
  "description": "Base URL for testing environment",
  "value": "https://example.com/api",
  "created_by": 1,
  "created_on": 1646317844,
  "updated_by": 1,
  "updated_on": 1646317844
}
```

### Get Variables

```
GET index.php?/api/v2/get_variables/{project_id}
```

Returns a list of variables for a project.

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
  "variables": [
    {
      "id": 1,
      "project_id": 1,
      "name": "BASE_URL",
      "description": "Base URL for testing environment",
      "value": "https://example.com/api",
      "created_by": 1,
      "created_on": 1646317844,
      "updated_by": 1,
      "updated_on": 1646317844
    },
    {
      "id": 2,
      "project_id": 1,
      "name": "ADMIN_USER",
      "description": "Admin username for testing",
      "value": "admin@example.com",
      "created_by": 1,
      "created_on": 1646318000,
      "updated_by": 1,
      "updated_on": 1646318000
    }
  ]
}
```

### Add Variable

```
POST index.php?/api/v2/add_variable/{project_id}
```

Creates a new variable.

#### Parameters:

- `project_id` (required): The ID of the project

#### Request Fields:

- `name` (required): The name of the new variable
- `value` (required): The value of the new variable
- `description`: The description of the new variable

#### Request Example:

```json
{
  "name": "API_KEY",
  "value": "abcd1234",
  "description": "API key for authentication"
}
```

### Update Variable

```
POST index.php?/api/v2/update_variable/{variable_id}
```

Updates an existing variable.

#### Parameters:

- `variable_id` (required): The ID of the variable

#### Request Fields:

- `name`: The name of the variable
- `value`: The value of the variable
- `description`: The description of the variable

### Delete Variable

```
POST index.php?/api/v2/delete_variable/{variable_id}
```

Deletes an existing variable.

#### Parameters:

- `variable_id` (required): The ID of the variable to delete

## Python Example

Here's a Python example for working with variables:

```python
import requests
import json

class TestRailAPI:
    def __init__(self, url, email, api_key):
        self.url = url
        self.email = email
        self.api_key = api_key
        
    def get_variables(self, project_id):
        api_url = f"{self.url}/index.php?/api/v2/get_variables/{project_id}"
        
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'}
        )
        
        return response.json()
    
    def get_variable(self, variable_id):
        api_url = f"{self.url}/index.php?/api/v2/get_variable/{variable_id}"
        
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'}
        )
        
        return response.json()
    
    def add_variable(self, project_id, name, value, description=None):
        api_url = f"{self.url}/index.php?/api/v2/add_variable/{project_id}"
        
        payload = {
            "name": name,
            "value": value
        }
        
        if description:
            payload["description"] = description
        
        response = requests.post(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        
        return response.json()
    
    def update_variable(self, variable_id, name=None, value=None, description=None):
        api_url = f"{self.url}/index.php?/api/v2/update_variable/{variable_id}"
        
        payload = {}
        
        if name:
            payload["name"] = name
            
        if value is not None:
            payload["value"] = value
            
        if description is not None:
            payload["description"] = description
        
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

# Get all variables in a project
variables = testrail.get_variables(1)
print("Variables in project:")
for variable in variables['variables']:
    print(f"- {variable['name']}: {variable['value']}")

# Create a new variable
new_variable = testrail.add_variable(
    project_id=1,
    name="TIMEOUT",
    value="30",
    description="Default timeout in seconds"
)
print(f"Created variable: {new_variable['name']} = {new_variable['value']}")

# Update a variable
updated_variable = testrail.update_variable(
    variable_id=new_variable['id'],
    value="60"
)
print(f"Updated variable {updated_variable['name']} to: {updated_variable['value']}")
```

## Using Variables in Test Cases

Variables can be referenced in test cases using the following syntax: `$variable_name`. When a test case is executed, TestRail replaces these references with the actual variable values.

## Environment-Specific Variables

You can create different variables for different environments by using a naming convention:

```python
# Create environment-specific variables
environments = ["DEV", "QA", "STAGING", "PROD"]
base_urls = {
    "DEV": "https://dev.example.com/api",
    "QA": "https://qa.example.com/api",
    "STAGING": "https://staging.example.com/api",
    "PROD": "https://api.example.com"
}

for env in environments:
    testrail.add_variable(
        project_id=1,
        name=f"{env}_BASE_URL",
        value=base_urls[env],
        description=f"Base URL for {env} environment"
    )
    
print(f"Created {len(environments)} environment-specific variables")
```

## Managing Sensitive Variables

For sensitive data like passwords or API keys, consider using a secure method for handling these values:

```python
def add_masked_variable(project_id, name, value, description=None):
    """
    Adds a variable with masked value in logs.
    """
    print(f"Adding variable {name} with masked value")
    
    return add_variable(project_id, name, value, description)

# Example usage:
add_masked_variable(
    project_id=1,
    name="DB_PASSWORD",
    value="sensitive-password-123",
    description="Database password (sensitive)"
)
```

## Variable Substitution in API Requests

When working with TestRail's API, you can use variables in your requests to make them more flexible:

```python
def create_test_run_with_variables(project_id, name, description=None):
    """
    Creates a test run with variable references in the description.
    
    The variables will be expanded when users view the test run in TestRail.
    """
    if not description:
        variables = get_variables(project_id)['variables']
        variable_list = "\n".join([f"- ${v['name']}: {v['value']}" for v in variables])
        description = f"Test run using the following variables:\n\n{variable_list}"
    
    # Create the test run
    api_url = f"{url}/index.php?/api/v2/add_run/{project_id}"
    
    payload = {
        "name": name,
        "description": description,
        "include_all": True
    }
    
    response = requests.post(
        api_url,
        auth=(email, api_key),
        headers={'Content-Type': 'application/json'},
        data=json.dumps(payload)
    )
    
    return response.json()

# Example usage:
test_run = create_test_run_with_variables(
    project_id=1,
    name="API Test Run"
)

print(f"Created test run with variable references: {test_run['name']} (ID: {test_run['id']})")
```

## Best Practices

1. Use meaningful names for variables (uppercase with underscores is a common convention)
2. Include descriptive comments for each variable
3. Group related variables together or use a consistent prefix
4. Consider environment-specific naming for variables that differ across environments
5. Use variables for values that are likely to change or need to be reused
6. Regularly review and update variables to ensure they remain current
7. Document the variables used in your project for reference
8. Be cautious when storing sensitive information in variables

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
