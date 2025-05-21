# Templates API

This document describes how to work with templates in TestRail using the API.

## Overview

Templates in TestRail define the structure and fields for test cases. The API provides methods to retrieve and manage these templates.

## API Endpoints

### Get Template

```
GET index.php?/api/v2/get_template/{template_id}
```

Returns an existing template.

#### Parameters:

- `template_id` (required): The ID of the template

#### Response Example:

```json
{
  "id": 1,
  "name": "Test Case (Steps)",
  "is_default": true
}
```

### Get Templates

```
GET index.php?/api/v2/get_templates/{project_id}
```

Returns a list of available templates for a project.

#### Parameters:

- `project_id` (required): The ID of the project

#### Response Example:

```json
[
  {
    "id": 1,
    "name": "Test Case (Steps)",
    "is_default": true
  },
  {
    "id": 2,
    "name": "Test Case (Text)",
    "is_default": false
  },
  {
    "id": 3,
    "name": "Exploratory Session",
    "is_default": false
  }
]
```

### Add Template

```
POST index.php?/api/v2/add_template/{project_id}
```

Creates a new template.

#### Parameters:

- `project_id` (required): The ID of the project

#### Request Fields:

- `name` (required): The name of the new template
- `is_default` (optional): True if this template should be used as the default template

#### Request Example:

```json
{
  "name": "API Test Case",
  "is_default": false
}
```

### Update Template

```
POST index.php?/api/v2/update_template/{template_id}
```

Updates an existing template.

#### Parameters:

- `template_id` (required): The ID of the template

#### Request Fields:

- `name`: The name of the template
- `is_default`: True if this template should be used as the default template

### Delete Template

```
POST index.php?/api/v2/delete_template/{template_id}
```

Deletes an existing template.

#### Parameters:

- `template_id` (required): The ID of the template to delete

**Note:** You cannot delete a template if it's currently used by a test case.

## Python Example

Here's a Python example for working with templates:

```python
import requests
import json

class TestRailAPI:
    def __init__(self, url, email, api_key):
        self.url = url
        self.email = email
        self.api_key = api_key
        
    def get_templates(self, project_id):
        api_url = f"{self.url}/index.php?/api/v2/get_templates/{project_id}"
        
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'}
        )
        
        return response.json()
    
    def get_template(self, template_id):
        api_url = f"{self.url}/index.php?/api/v2/get_template/{template_id}"
        
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'}
        )
        
        return response.json()
    
    def add_template(self, project_id, name, is_default=False):
        api_url = f"{self.url}/index.php?/api/v2/add_template/{project_id}"
        
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
    
    def update_template(self, template_id, name=None, is_default=None):
        api_url = f"{self.url}/index.php?/api/v2/update_template/{template_id}"
        
        payload = {}
        
        if name:
            payload["name"] = name
            
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

# Get all templates in a project
templates = testrail.get_templates(1)
print("Templates in project:")
for template in templates:
    default = " (default)" if template['is_default'] else ""
    print(f"- {template['name']}{default}")

# Create a new template
new_template = testrail.add_template(
    project_id=1,
    name="Security Test Case",
    is_default=False
)
print(f"Created template: {new_template['name']} (ID: {new_template['id']})")

# Update a template
updated_template = testrail.update_template(
    template_id=new_template['id'],
    name="Security Test Case (OWASP)"
)
print(f"Updated template name to: {updated_template['name']}")
```

## Using Templates with Test Cases

When creating or updating test cases, you can specify which template to use with the `template_id` field:

```python
def add_case_with_template(section_id, title, template_id):
    """
    Creates a test case using a specific template.
    """
    api_url = f"{url}/index.php?/api/v2/add_case/{section_id}"
    
    payload = {
        "title": title,
        "template_id": template_id
    }
    
    response = requests.post(
        api_url,
        auth=(email, api_key),
        headers={'Content-Type': 'application/json'},
        data=json.dumps(payload)
    )
    
    return response.json()

# Example usage:
# Find the ID for "Security Test Case" template
security_template_id = new_template['id']

# Create a test case with this template
test_case = add_case_with_template(
    section_id=1,
    title="SQL Injection Test",
    template_id=security_template_id
)

print(f"Created test case with security template: {test_case['title']} (ID: {test_case['id']})")
```

## Common Template Types

TestRail includes several built-in templates, and you can create custom templates as needed. Here are some common template types:

1. **Test Case (Steps)**: Includes steps and expected results in a tabular format
2. **Test Case (Text)**: Includes a single text field for the test case
3. **Exploratory Session**: Used for exploratory testing with session details
4. **BDD**: Used for Behavior-Driven Development with Given/When/Then format

## Template Custom Fields

Templates determine which custom fields are available for test cases. When working with templates, be aware of the custom fields associated with each template. You can view and configure template custom fields in the TestRail administration settings.

## Best Practices

1. Create specialized templates for different types of testing
2. Keep template names clear and descriptive
3. Include only the necessary fields in each template to avoid clutter
4. Set appropriate default templates for your projects
5. Document the purpose and use cases for each template
6. Standardize templates across projects for consistency
7. Review and refine templates as your testing needs evolve
8. Consider using different templates for different phases of testing

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
