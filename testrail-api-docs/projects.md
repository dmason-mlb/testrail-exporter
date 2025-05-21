# Projects API

This document describes how to work with projects in TestRail using the API.

## Overview

Projects are the main organizational unit in TestRail. The API provides methods to retrieve and manage these projects.

## API Endpoints

### Get Project

```
GET index.php?/api/v2/get_project/{project_id}
```

Returns an existing project.

#### Parameters:

- `project_id` (required): The ID of the project

#### Response Example:

```json
{
  "id": 1,
  "name": "Web Application",
  "announcement": "This project tracks issues for our web application.",
  "show_announcement": true,
  "is_completed": false,
  "completed_on": null,
  "suite_mode": 2,
  "url": "https://example.testrail.com/index.php?/projects/overview/1"
}
```

### Get Projects

```
GET index.php?/api/v2/get_projects
```

Returns the list of all projects.

#### Parameters:

- `is_completed` (optional): `0` to return active projects only, `1` to return completed projects only

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
  "projects": [
    {
      "id": 1,
      "name": "Web Application",
      "announcement": "This project tracks issues for our web application.",
      "show_announcement": true,
      "is_completed": false,
      "completed_on": null,
      "suite_mode": 2,
      "url": "https://example.testrail.com/index.php?/projects/overview/1"
    },
    {
      "id": 2,
      "name": "Mobile Application",
      "announcement": "This project tracks issues for our mobile applications.",
      "show_announcement": true,
      "is_completed": false,
      "completed_on": null,
      "suite_mode": 3,
      "url": "https://example.testrail.com/index.php?/projects/overview/2"
    }
  ]
}
```

### Add Project

```
POST index.php?/api/v2/add_project
```

Creates a new project.

#### Request Fields:

- `name` (required): The name of the new project
- `announcement`: The description and announcement for the new project
- `show_announcement`: `true` to show the announcement, `false` otherwise
- `suite_mode`: The suite mode of the new project (1 for single suite mode, 2 for single suite + baselines, 3 for multiple suites)

#### Request Example:

```json
{
  "name": "API Integration Project",
  "announcement": "Project for API integration testing",
  "show_announcement": true,
  "suite_mode": 3
}
```

### Update Project

```
POST index.php?/api/v2/update_project/{project_id}
```

Updates an existing project.

#### Parameters:

- `project_id` (required): The ID of the project

#### Request Fields:

- `name`: The name of the project
- `announcement`: The description and announcement for the project
- `show_announcement`: `true` to show the announcement, `false` otherwise
- `is_completed`: `true` to mark the project as completed, `false` otherwise

### Delete Project

```
POST index.php?/api/v2/delete_project/{project_id}
```

Deletes an existing project.

#### Parameters:

- `project_id` (required): The ID of the project to delete

## Python Example

Here's a Python example for working with projects:

```python
import requests
import json

class TestRailAPI:
    def __init__(self, url, email, api_key):
        self.url = url
        self.email = email
        self.api_key = api_key
        
    def get_projects(self, is_completed=None):
        api_url = f"{self.url}/index.php?/api/v2/get_projects"
        
        params = {}
        if is_completed is not None:
            params['is_completed'] = 1 if is_completed else 0
            
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'},
            params=params
        )
        
        return response.json()
    
    def add_project(self, name, announcement=None, show_announcement=True, suite_mode=3):
        api_url = f"{self.url}/index.php?/api/v2/add_project"
        
        payload = {
            "name": name,
            "suite_mode": suite_mode
        }
        
        if announcement:
            payload["announcement"] = announcement
            payload["show_announcement"] = show_announcement
        
        response = requests.post(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        
        return response.json()
    
    def update_project(self, project_id, name=None, announcement=None, 
                      show_announcement=None, is_completed=None):
        api_url = f"{self.url}/index.php?/api/v2/update_project/{project_id}"
        
        payload = {}
        
        if name:
            payload["name"] = name
            
        if announcement is not None:
            payload["announcement"] = announcement
            
        if show_announcement is not None:
            payload["show_announcement"] = show_announcement
            
        if is_completed is not None:
            payload["is_completed"] = is_completed
        
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

# Get all active projects
projects = testrail.get_projects(is_completed=False)
print("Active projects:")
for project in projects['projects']:
    print(f"- {project['name']} (ID: {project['id']}, Suite Mode: {project['suite_mode']})")

# Create a new project
new_project = testrail.add_project(
    name="Performance Testing",
    announcement="Project for performance and load testing",
    suite_mode=3  # Multiple test suites
)
print(f"Created new project: {new_project['name']} (ID: {new_project['id']})")

# Update a project
updated_project = testrail.update_project(
    project_id=new_project['id'],
    announcement="Project for performance, load, and stress testing"
)
print(f"Updated project announcement for: {updated_project['name']}")
```

## Understanding Suite Modes

TestRail supports three different suite modes for projects:

1. **Single Suite Mode (1)**: Only one test suite per project. Simple structure, ideal for smaller projects.
2. **Single Suite + Baselines Mode (2)**: One test suite with support for multiple baselines (snapshots of test cases at different points in time).
3. **Multiple Suites Mode (3)**: Multiple test suites per project. Allows organizing test cases into separate suites, ideal for complex projects.

When creating a project, it's important to choose the appropriate suite mode as it can't be changed later.

## Best Practices

1. Use clear, descriptive project names
2. Include relevant information in the project announcement
3. Choose the appropriate suite mode based on project complexity
4. Regularly review and archive completed projects
5. Maintain a consistent project structure across your TestRail instance

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
