# Milestones API

This document describes how to work with milestones in TestRail using the API.

## Overview

Milestones in TestRail allow you to track progress across test runs and test plans. The API provides methods to retrieve and manage these milestones.

## API Endpoints

### Get Milestone

```
GET index.php?/api/v2/get_milestone/{milestone_id}
```

Returns an existing milestone.

#### Parameters:

- `milestone_id` (required): The ID of the milestone

#### Response Example:

```json
{
  "id": 1,
  "name": "Release 1.0",
  "description": "First major release",
  "due_on": 1646419200,
  "start_on": 1642456800,
  "project_id": 1,
  "parent_id": null,
  "is_completed": false,
  "completed_on": null,
  "is_started": true,
  "started_on": 1642456800,
  "url": "https://example.testrail.com/index.php?/milestones/view/1"
}
```

### Get Milestones

```
GET index.php?/api/v2/get_milestones/{project_id}
```

Returns the list of milestones for a project.

#### Parameters:

- `project_id` (required): The ID of the project
- `is_completed` (optional): `0` to return incomplete milestones only, `1` to return completed milestones only
- `is_started` (optional): `0` to return milestones that have not been started, `1` to return started milestones only

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
  "milestones": [
    {
      "id": 1,
      "name": "Release 1.0",
      "description": "First major release",
      "due_on": 1646419200,
      "start_on": 1642456800,
      "project_id": 1,
      "parent_id": null,
      "is_completed": false,
      "completed_on": null,
      "is_started": true,
      "started_on": 1642456800,
      "url": "https://example.testrail.com/index.php?/milestones/view/1"
    },
    {
      "id": 2,
      "name": "Release 1.1",
      "description": "Minor update release",
      "due_on": 1649011200,
      "start_on": 1646419200,
      "project_id": 1,
      "parent_id": null,
      "is_completed": false,
      "completed_on": null,
      "is_started": false,
      "started_on": null,
      "url": "https://example.testrail.com/index.php?/milestones/view/2"
    }
  ]
}
```

### Add Milestone

```
POST index.php?/api/v2/add_milestone/{project_id}
```

Creates a new milestone.

#### Parameters:

- `project_id` (required): The ID of the project

#### Request Fields:

- `name` (required): The name of the new milestone
- `description`: The description of the new milestone
- `due_on`: The due date of the new milestone (as UNIX timestamp)
- `start_on`: The start date of the new milestone (as UNIX timestamp)
- `parent_id`: The ID of the parent milestone, if any
- `is_completed`: Whether the milestone is considered completed (`true` or `false`)
- `is_started`: Whether the milestone is considered started (`true` or `false`)

#### Request Example:

```json
{
  "name": "Release 1.2",
  "description": "Feature enhancement release",
  "due_on": 1651689600,
  "start_on": 1649011200
}
```

### Update Milestone

```
POST index.php?/api/v2/update_milestone/{milestone_id}
```

Updates an existing milestone.

#### Parameters:

- `milestone_id` (required): The ID of the milestone

#### Request Fields:

Same as `add_milestone`.

### Delete Milestone

```
POST index.php?/api/v2/delete_milestone/{milestone_id}
```

Deletes an existing milestone.

#### Parameters:

- `milestone_id` (required): The ID of the milestone to delete

## Python Example

Here's a Python example for working with milestones:

```python
import requests
import json
import time

class TestRailAPI:
    def __init__(self, url, email, api_key):
        self.url = url
        self.email = email
        self.api_key = api_key
        
    def get_milestones(self, project_id, is_completed=None, is_started=None):
        api_url = f"{self.url}/index.php?/api/v2/get_milestones/{project_id}"
        
        params = {}
        if is_completed is not None:
            params['is_completed'] = 1 if is_completed else 0
        if is_started is not None:
            params['is_started'] = 1 if is_started else 0
            
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'},
            params=params
        )
        
        return response.json()
    
    def add_milestone(self, project_id, name, description=None, due_on=None, start_on=None):
        api_url = f"{self.url}/index.php?/api/v2/add_milestone/{project_id}"
        
        payload = {
            "name": name
        }
        
        if description:
            payload["description"] = description
            
        if due_on:
            payload["due_on"] = due_on
            
        if start_on:
            payload["start_on"] = start_on
        
        response = requests.post(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        
        return response.json()
    
    def update_milestone(self, milestone_id, name=None, description=None, 
                         due_on=None, start_on=None, is_completed=None):
        api_url = f"{self.url}/index.php?/api/v2/update_milestone/{milestone_id}"
        
        payload = {}
        
        if name:
            payload["name"] = name
            
        if description is not None:
            payload["description"] = description
            
        if due_on:
            payload["due_on"] = due_on
            
        if start_on:
            payload["start_on"] = start_on
            
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

# Get active milestones
milestones = testrail.get_milestones(1, is_completed=False)
print("Active milestones:")
for milestone in milestones['milestones']:
    print(f"- {milestone['name']} (Due: {time.strftime('%Y-%m-%d', time.localtime(milestone['due_on']))})")

# Create a new milestone
# Calculate timestamps for 3 months from now
three_months = int(time.time()) + (90 * 24 * 60 * 60)
one_month = int(time.time()) + (30 * 24 * 60 * 60)

new_milestone = testrail.add_milestone(
    project_id=1,
    name="Release 2.0",
    description="Major feature release",
    start_on=one_month,
    due_on=three_months
)

print(f"Created milestone: {new_milestone['name']} (ID: {new_milestone['id']})")

# Mark a milestone as completed
testrail.update_milestone(1, is_completed=True)
print("Marked milestone as completed")
```

## Creating a Milestone Hierarchy

TestRail supports hierarchical milestones (parent-child relationships). Here's an example of creating a milestone hierarchy:

```python
# Create parent milestone
parent = testrail.add_milestone(
    project_id=1,
    name="Q2 2025",
    description="Q2 Releases"
)

# Create child milestones
releases = ["April Release", "May Release", "June Release"]
for release in releases:
    testrail.add_milestone(
        project_id=1,
        name=release,
        parent_id=parent['id']
    )

print(f"Created milestone hierarchy with parent: {parent['name']}")
```

## Best Practices

1. Create milestones that align with your project's release schedule
2. Use start and due dates to track milestone timelines
3. Create milestone hierarchies for better organization of related milestones
4. Update milestone status (started/completed) to reflect current project state
5. Link test plans and test runs to appropriate milestones

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
