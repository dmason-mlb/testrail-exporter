# Sections API

This document describes how to work with test sections in TestRail using the API.

## Overview

Sections in TestRail allow you to organize test cases into logical groups. The API provides methods to retrieve and manage these sections.

## API Endpoints

### Get Section

```
GET index.php?/api/v2/get_section/{section_id}
```

Returns an existing section.

#### Parameters:

- `section_id` (required): The ID of the section

#### Response Example:

```json
{
  "id": 1,
  "suite_id": 1,
  "name": "Login Functionality",
  "description": "Test cases for user login features",
  "parent_id": null,
  "display_order": 1,
  "depth": 0
}
```

### Get Sections

```
GET index.php?/api/v2/get_sections/{project_id}&suite_id={suite_id}
```

Returns a list of sections for a project and test suite.

#### Parameters:

- `project_id` (required): The ID of the project
- `suite_id` (optional): The ID of the test suite (if the project has multiple suites)

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
  "sections": [
    {
      "id": 1,
      "suite_id": 1,
      "name": "Login Functionality",
      "description": "Test cases for user login features",
      "parent_id": null,
      "display_order": 1,
      "depth": 0
    },
    {
      "id": 2,
      "suite_id": 1,
      "name": "User Profile",
      "description": "Test cases for user profile management",
      "parent_id": null,
      "display_order": 2,
      "depth": 0
    }
  ]
}
```

### Add Section

```
POST index.php?/api/v2/add_section/{project_id}
```

Creates a new section.

#### Parameters:

- `project_id` (required): The ID of the project

#### Request Fields:

- `name` (required): The name of the new section
- `description`: The description of the new section
- `suite_id`: The ID of the test suite (if the project has multiple suites)
- `parent_id`: The ID of the parent section (if adding a sub-section)

#### Request Example:

```json
{
  "name": "Payment Processing",
  "description": "Test cases for payment processing features",
  "suite_id": 1,
  "parent_id": null
}
```

### Update Section

```
POST index.php?/api/v2/update_section/{section_id}
```

Updates an existing section.

#### Parameters:

- `section_id` (required): The ID of the section

#### Request Fields:

- `name`: The name of the section
- `description`: The description of the section
- `parent_id`: The ID of the parent section

### Delete Section

```
POST index.php?/api/v2/delete_section/{section_id}
```

Deletes an existing section.

#### Parameters:

- `section_id` (required): The ID of the section to delete

**Note:** Deleting a section also deletes all related test cases and sub-sections.

### Move Section

```
POST index.php?/api/v2/move_section/{section_id}
```

Moves a section to a different parent section.

#### Parameters:

- `section_id` (required): The ID of the section

#### Request Fields:

- `parent_id`: The ID of the parent section (set to 0 to move to the root level)
- `suite_id`: The ID of the test suite to move the section to (optional)

#### Request Example:

```json
{
  "parent_id": 3
}
```

## Python Example

Here's a Python example for working with sections:

```python
import requests
import json

class TestRailAPI:
    def __init__(self, url, email, api_key):
        self.url = url
        self.email = email
        self.api_key = api_key
        
    def get_sections(self, project_id, suite_id=None):
        api_url = f"{self.url}/index.php?/api/v2/get_sections/{project_id}"
        
        params = {}
        if suite_id:
            params['suite_id'] = suite_id
            
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'},
            params=params
        )
        
        return response.json()
    
    def add_section(self, project_id, name, description=None, suite_id=None, parent_id=None):
        api_url = f"{self.url}/index.php?/api/v2/add_section/{project_id}"
        
        payload = {
            "name": name
        }
        
        if description:
            payload["description"] = description
            
        if suite_id:
            payload["suite_id"] = suite_id
            
        if parent_id:
            payload["parent_id"] = parent_id
        
        response = requests.post(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        
        return response.json()
    
    def update_section(self, section_id, name=None, description=None, parent_id=None):
        api_url = f"{self.url}/index.php?/api/v2/update_section/{section_id}"
        
        payload = {}
        
        if name:
            payload["name"] = name
            
        if description is not None:
            payload["description"] = description
            
        if parent_id is not None:
            payload["parent_id"] = parent_id
        
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

# Get all sections in a project
sections = testrail.get_sections(1, suite_id=1)
print("Sections in project:")
for section in sections['sections']:
    indent = '  ' * section['depth']
    print(f"{indent}- {section['name']}")

# Create a new section
new_section = testrail.add_section(
    project_id=1,
    name="Registration Process",
    description="Test cases for user registration",
    suite_id=1
)
print(f"Created section: {new_section['name']} (ID: {new_section['id']})")

# Create a sub-section
sub_section = testrail.add_section(
    project_id=1,
    name="Email Verification",
    description="Test cases for email verification during registration",
    suite_id=1,
    parent_id=new_section['id']
)
print(f"Created sub-section: {sub_section['name']} under {new_section['name']}")

# Update a section
updated_section = testrail.update_section(
    section_id=new_section['id'],
    name="User Registration Process"
)
print(f"Updated section name to: {updated_section['name']}")
```

## Working with Section Hierarchies

TestRail supports hierarchical sections (parent-child relationships). Here's an example of creating a section hierarchy:

```python
def create_section_hierarchy(project_id, suite_id, structure):
    """
    Creates a section hierarchy in TestRail.
    
    structure: A dictionary with section names as keys and their sub-sections as values.
    Example:
    {
        "Frontend": {
            "Login": {},
            "Registration": {
                "Email Verification": {},
                "Profile Setup": {}
            }
        },
        "Backend": {
            "API": {},
            "Database": {}
        }
    }
    """
    section_ids = {}
    
    # Create top-level sections first
    for section_name, subsections in structure.items():
        section = testrail.add_section(
            project_id=project_id,
            name=section_name,
            suite_id=suite_id
        )
        section_ids[section_name] = section['id']
        
        # Create sub-sections (level 1)
        for subsection_name, sub_subsections in subsections.items():
            subsection = testrail.add_section(
                project_id=project_id,
                name=subsection_name,
                suite_id=suite_id,
                parent_id=section_ids[section_name]
            )
            section_ids[f"{section_name}/{subsection_name}"] = subsection['id']
            
            # Create sub-sub-sections (level 2)
            for sub_subsection_name in sub_subsections:
                sub_subsection = testrail.add_section(
                    project_id=project_id,
                    name=sub_subsection_name,
                    suite_id=suite_id,
                    parent_id=section_ids[f"{section_name}/{subsection_name}"]
                )
                section_ids[f"{section_name}/{subsection_name}/{sub_subsection_name}"] = sub_subsection['id']
    
    return section_ids

# Example usage:
structure = {
    "Frontend": {
        "Login": {},
        "Registration": {
            "Email Verification": {},
            "Profile Setup": {}
        }
    },
    "Backend": {
        "API": {},
        "Database": {}
    }
}

section_ids = create_section_hierarchy(1, 1, structure)
print("Created section hierarchy with the following paths:")
for path, section_id in section_ids.items():
    print(f"- {path} (ID: {section_id})")
```

## Working with Test Cases in Sections

Once you have sections set up, you can add test cases to them:

```python
def add_cases_to_section(section_id, cases):
    """
    Adds multiple test cases to a section.
    
    cases: A list of dictionaries with test case details.
    """
    results = []
    
    for case in cases:
        api_url = f"{url}/index.php?/api/v2/add_case/{section_id}"
        
        response = requests.post(
            api_url,
            auth=(email, api_key),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(case)
        )
        
        results.append(response.json())
    
    return results

# Example usage:
login_cases = [
    {
        "title": "Valid login with correct credentials",
        "type_id": 1,
        "priority_id": 2,
        "custom_steps": "1. Navigate to login page\n2. Enter valid username\n3. Enter valid password\n4. Click Login button",
        "custom_expected": "User is logged in successfully and redirected to dashboard"
    },
    {
        "title": "Invalid login with incorrect password",
        "type_id": 1,
        "priority_id": 2,
        "custom_steps": "1. Navigate to login page\n2. Enter valid username\n3. Enter invalid password\n4. Click Login button",
        "custom_expected": "Error message is displayed and user remains on login page"
    }
]

# Add cases to the "Login" section
login_section_id = section_ids["Frontend/Login"]
added_cases = add_cases_to_section(login_section_id, login_cases)
print(f"Added {len(added_cases)} test cases to Login section")
```

## Best Practices

1. Create a logical section hierarchy that mirrors your application's structure
2. Keep section names concise and descriptive
3. Use parent-child relationships for better organization
4. Ensure consistency in section naming conventions
5. Consider a balanced approach to section depth (avoid too many or too few levels)
6. Use section descriptions to provide context about the grouped test cases
7. Regularly review and refactor your section structure as your application evolves
8. Limit the number of test cases per section for better manageability

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
