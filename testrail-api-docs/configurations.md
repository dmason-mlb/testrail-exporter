# Configurations API

This document describes how to work with configurations in TestRail using the API.

## Overview

Configurations in TestRail allow you to define different test environments or variations that your tests can be run against (such as browsers, operating systems, device types, etc.). The API provides methods to retrieve and manage these configurations.

## API Endpoints

### Get Configurations

```
GET index.php?/api/v2/get_configs/{project_id}
```

Returns a list of available configurations for a project.

#### Parameters:

- `project_id` (required): The ID of the project

#### Response Example:

```json
[
  {
    "id": 1,
    "name": "Browsers",
    "project_id": 1,
    "configs": [
      {
        "id": 1,
        "name": "Chrome",
        "group_id": 1
      },
      {
        "id": 2,
        "name": "Firefox",
        "group_id": 1
      },
      {
        "id": 3,
        "name": "Internet Explorer",
        "group_id": 1
      }
    ]
  },
  {
    "id": 2,
    "name": "Operating Systems",
    "project_id": 1,
    "configs": [
      {
        "id": 4,
        "name": "Windows",
        "group_id": 2
      },
      {
        "id": 5,
        "name": "macOS",
        "group_id": 2
      },
      {
        "id": 6,
        "name": "Linux",
        "group_id": 2
      }
    ]
  }
]
```

### Add Configuration Group

```
POST index.php?/api/v2/add_config_group/{project_id}
```

Creates a new configuration group.

#### Parameters:

- `project_id` (required): The ID of the project

#### Request Fields:

- `name` (required): The name of the new configuration group

### Add Configuration

```
POST index.php?/api/v2/add_config/{config_group_id}
```

Creates a new configuration.

#### Parameters:

- `config_group_id` (required): The ID of the configuration group

#### Request Fields:

- `name` (required): The name of the new configuration

### Update Configuration Group

```
POST index.php?/api/v2/update_config_group/{config_group_id}
```

Updates an existing configuration group.

#### Parameters:

- `config_group_id` (required): The ID of the configuration group

#### Request Fields:

- `name` (required): The new name of the configuration group

### Update Configuration

```
POST index.php?/api/v2/update_config/{config_id}
```

Updates an existing configuration.

#### Parameters:

- `config_id` (required): The ID of the configuration

#### Request Fields:

- `name` (required): The new name of the configuration

### Delete Configuration Group

```
POST index.php?/api/v2/delete_config_group/{config_group_id}
```

Deletes an existing configuration group including all configurations in the group.

#### Parameters:

- `config_group_id` (required): The ID of the configuration group to delete

### Delete Configuration

```
POST index.php?/api/v2/delete_config/{config_id}
```

Deletes an existing configuration.

#### Parameters:

- `config_id` (required): The ID of the configuration to delete

## Python Example

Here's a Python example for working with configurations:

```python
import requests
import json

class TestRailAPI:
    def __init__(self, url, email, api_key):
        self.url = url
        self.email = email
        self.api_key = api_key
        
    def get_configs(self, project_id):
        api_url = f"{self.url}/index.php?/api/v2/get_configs/{project_id}"
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'}
        )
        return response.json()
    
    def add_config_group(self, project_id, name):
        api_url = f"{self.url}/index.php?/api/v2/add_config_group/{project_id}"
        response = requests.post(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'name': name})
        )
        return response.json()
    
    def add_config(self, config_group_id, name):
        api_url = f"{self.url}/index.php?/api/v2/add_config/{config_group_id}"
        response = requests.post(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'},
            data=json.dumps({'name': name})
        )
        return response.json()

# Usage example
testrail = TestRailAPI(
    url="https://example.testrail.com",
    email="your_email@example.com",
    api_key="your_api_key"
)

# Get existing configurations
configs = testrail.get_configs(1)
print("Existing configuration groups:")
for group in configs:
    print(f"- {group['name']}")
    for config in group['configs']:
        print(f"  - {config['name']}")

# Add a new configuration group
new_group = testrail.add_config_group(1, "Mobile Devices")
print(f"Created new group: {new_group['name']} (ID: {new_group['id']})")

# Add configurations to the group
devices = ["iPhone", "Android", "iPad"]
for device in devices:
    config = testrail.add_config(new_group['id'], device)
    print(f"Added config: {config['name']} (ID: {config['id']})")
```

## Using Configurations with Test Runs

When creating a test run, you can specify configurations to use:

```python
def create_test_run_with_configs(url, email, api_key, project_id, suite_id, name, config_ids):
    api_url = f"{url}/index.php?/api/v2/add_run/{project_id}"
    
    payload = {
        "suite_id": suite_id,
        "name": name,
        "include_all": True,
        "config_ids": config_ids
    }
    
    response = requests.post(
        api_url,
        auth=(email, api_key),
        headers={'Content-Type': 'application/json'},
        data=json.dumps(payload)
    )
    
    return response.json()

# Find Chrome and Windows configuration IDs from the example response
chrome_id = 1
windows_id = 4

# Create a test run for Chrome on Windows
test_run = create_test_run_with_configs(
    url="https://example.testrail.com",
    email="your_email@example.com",
    api_key="your_api_key",
    project_id=1,
    suite_id=1,
    name="Smoke Test - Chrome on Windows",
    config_ids=[chrome_id, windows_id]
)

print(f"Created test run: {test_run['name']} (ID: {test_run['id']})")
```

## Best Practices

1. Create logical configuration groups based on your testing needs
2. Keep configuration names concise and consistent
3. Use configurations to reduce test case duplication
4. Create configurations for all relevant test environments
5. Consider using configurations in test plans to organize runs by environment

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
