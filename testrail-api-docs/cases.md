# Cases API

This document describes how to work with test cases in TestRail using the API.

## Overview

The TestRail API provides methods to retrieve data about test cases (title, case fields, history) and to create, modify, or delete test cases.

## API Endpoints

### Get Case

```
GET index.php?/api/v2/get_case/{case_id}
```

Returns an existing test case.

#### Parameters:

- `case_id` (required): The ID of the test case

#### Response Example:

```json
{
  "id": 1,
  "title": "Print document history and attributes",
  "section_id": 1,
  "template_id": 1,
  "type_id": 2,
  "priority_id": 2,
  "milestone_id": null,
  "refs": null,
  "created_by": 1,
  "created_on": 1646317844,
  "updated_by": 1,
  "updated_on": 1646317844,
  "estimate": null,
  "estimate_forecast": "8m 40s",
  "suite_id": 1,
  "display_order": 1,
  "is_deleted": 0,
  "custom_automation_type": 0,
  "custom_preconds": null,
  "custom_steps": null,
  "custom_expected": null,
  "custom_steps_separated": null,
  "custom_mission": null,
  "custom_goals": null
}
```

### Add Case

```
POST index.php?/api/v2/add_case/{section_id}
```

Creates a new test case.

#### Parameters:

- `section_id` (required): The ID of the section the test case should be added to

#### Request Fields:

- `title` (required): The title of the test case
- `type_id`: The ID of the case type
- `priority_id`: The ID of the case priority
- `estimate`: The estimate, e.g. "30s" or "1m 45s"
- `milestone_id`: The ID of the milestone to link the test case to
- `refs`: A comma-separated list of references/requirements

Custom field parameters are also supported and must be submitted with their system name, prefixed with 'custom_'.

### Update Case

```
POST index.php?/api/v2/update_case/{case_id}
```

Updates an existing test case (partial updates are supported).

#### Parameters:

- `case_id` (required): The ID of the test case

This method supports the same POST fields as `add_case`. Updating a case's `section_id` requires TestRail 6.5.2 or later.

### Get History for Case

```
GET index.php?/api/v2/get_history_for_case/{case_id}
```

Returns the edit history for a test case.

#### Parameters:

- `case_id` (required): The ID of the test case

This endpoint requires TestRail 6.5.4 or later.

### Copy Cases to Section

```
POST index.php?/api/v2/copy_cases_to_section/{section_id}
```

Copies the list of cases to another suite/section.

#### Parameters:

- `section_id` (required): The ID of the target section

#### Request Fields:

- `case_ids` (required): An array of case IDs to copy

### Move Cases to Section

```
POST index.php?/api/v2/move_cases_to_section/{section_id}
```

Moves cases to another suite or section.

#### Parameters:

- `section_id` (required): The ID of the target section

#### Request Fields:

- `case_ids` (required): An array of case IDs to move

### Delete Case

```
POST index.php?/api/v2/delete_case/{case_id}
```

Deletes an existing test case.

#### Parameters:

- `case_id` (required): The ID of the test case to delete
- `soft` (optional): Whether to perform a soft delete (1) or hard delete (0)

**Warning:** Deleting a test case cannot be undone and also permanently deletes all test results in active test runs (test runs that haven't been closed/archived yet).

## Python Example

Here's a Python example for retrieving and updating a test case:

```python
import requests
import json

class TestRailAPI:
    def __init__(self, url, email, api_key):
        self.url = url
        self.email = email
        self.api_key = api_key
        
    def get_case(self, case_id):
        api_url = f"{self.url}/index.php?/api/v2/get_case/{case_id}"
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'}
        )
        return response.json()
    
    def update_case(self, case_id, updates):
        api_url = f"{self.url}/index.php?/api/v2/update_case/{case_id}"
        response = requests.post(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(updates)
        )
        return response.json()

# Usage example
testrail = TestRailAPI(
    url="https://example.testrail.com",
    email="your_email@example.com",
    api_key="your_api_key"
)

# Get case details
case = testrail.get_case(1)
print(f"Case title: {case['title']}")

# Update case
updated_case = testrail.update_case(1, {
    "title": "Updated test case title",
    "priority_id": 3,
    "custom_steps": "1. Navigate to login page\n2. Enter credentials\n3. Click Login"
})
print(f"Updated case: {updated_case['title']}")
```

## Bulk Operations

For efficient management of multiple test cases, you can use bulk update operations:

### Update Cases (Bulk)

```
POST index.php?/api/v2/update_cases/{project_id}
```

Updates multiple test cases in a single operation.

#### Parameters:

- `project_id` (required): The ID of the project

#### Request Fields:

- `case_ids` (required): An array of case IDs to update
- Other fields to update (same as `update_case`)

#### Request Example:

```json
{
  "case_ids": [1, 2, 3],
  "priority_id": 1,
  "estimate": "5m"
}
```

## Best Practices

1. Use bulk operations when working with multiple test cases
2. Include error handling for API requests
3. Be careful with case deletions as they cannot be undone
4. Maintain consistent case fields and formats across your test suite
5. Consider using case history for audit purposes

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
