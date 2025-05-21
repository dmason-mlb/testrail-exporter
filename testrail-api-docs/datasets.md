# Datasets API

This document describes how to work with datasets in TestRail using the API.

## Overview

Datasets in TestRail allow you to manage test data for use with test case parameterization. The API provides methods to retrieve and manage these datasets.

## API Endpoints

### Get Datasets

```
GET index.php?/api/v2/get_datasets/{project_id}
```

Returns a list of available datasets for a project.

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
  "datasets": [
    {
      "id": 1,
      "project_id": 1,
      "name": "Login Credentials",
      "description": "Test accounts for login testing",
      "created_by": 1,
      "created_on": 1646317844,
      "updated_by": 1,
      "updated_on": 1646317844
    },
    {
      "id": 2,
      "project_id": 1,
      "name": "Product Data",
      "description": "Test products for e-commerce testing",
      "created_by": 1,
      "created_on": 1646317900,
      "updated_by": 1,
      "updated_on": 1646317900
    }
  ]
}
```

### Get Dataset

```
GET index.php?/api/v2/get_dataset/{dataset_id}
```

Returns a specific dataset.

#### Parameters:

- `dataset_id` (required): The ID of the dataset

#### Response:

The response includes the dataset details and items:

```json
{
  "id": 1,
  "project_id": 1,
  "name": "Login Credentials",
  "description": "Test accounts for login testing",
  "items": [
    {
      "id": 1,
      "row": {
        "username": "testuser1",
        "password": "pass123",
        "role": "user"
      }
    },
    {
      "id": 2,
      "row": {
        "username": "testuser2",
        "password": "pass456",
        "role": "admin"
      }
    }
  ],
  "columns": [
    {
      "name": "username",
      "label": "Username",
      "description": "Username for login"
    },
    {
      "name": "password",
      "label": "Password",
      "description": "Password for login"
    },
    {
      "name": "role",
      "label": "Role",
      "description": "User role"
    }
  ],
  "created_by": 1,
  "created_on": 1646317844,
  "updated_by": 1,
  "updated_on": 1646317844
}
```

### Add Dataset

```
POST index.php?/api/v2/add_dataset/{project_id}
```

Creates a new dataset.

#### Parameters:

- `project_id` (required): The ID of the project

#### Request Fields:

- `name` (required): The name of the new dataset
- `description`: Optional description for the dataset
- `columns` (required): Array of column definitions
- `items`: Optional array of initial data items

#### Request Example:

```json
{
  "name": "Payment Methods",
  "description": "Test payment methods for checkout testing",
  "columns": [
    {
      "name": "method",
      "label": "Payment Method",
      "description": "Type of payment"
    },
    {
      "name": "card_number",
      "label": "Card Number",
      "description": "Credit card number"
    },
    {
      "name": "expiry",
      "label": "Expiry Date",
      "description": "Card expiration date"
    }
  ],
  "items": [
    {
      "row": {
        "method": "Visa",
        "card_number": "4111111111111111",
        "expiry": "12/25"
      }
    },
    {
      "row": {
        "method": "Mastercard",
        "card_number": "5555555555554444",
        "expiry": "10/24"
      }
    }
  ]
}
```

### Update Dataset

```
POST index.php?/api/v2/update_dataset/{dataset_id}
```

Updates an existing dataset.

#### Parameters:

- `dataset_id` (required): The ID of the dataset

#### Request Fields:

- `name`: New name for the dataset
- `description`: New description for the dataset

### Delete Dataset

```
POST index.php?/api/v2/delete_dataset/{dataset_id}
```

Deletes an existing dataset.

#### Parameters:

- `dataset_id` (required): The ID of the dataset to delete

### Add Dataset Item

```
POST index.php?/api/v2/add_dataset_item/{dataset_id}
```

Adds a new item to a dataset.

#### Parameters:

- `dataset_id` (required): The ID of the dataset

#### Request Fields:

- `row` (required): An object containing the column values for the new item

### Update Dataset Item

```
POST index.php?/api/v2/update_dataset_item/{dataset_id}/{item_id}
```

Updates an existing dataset item.

#### Parameters:

- `dataset_id` (required): The ID of the dataset
- `item_id` (required): The ID of the item to update

#### Request Fields:

- `row` (required): An object containing the updated column values

### Delete Dataset Item

```
POST index.php?/api/v2/delete_dataset_item/{dataset_id}/{item_id}
```

Deletes an existing dataset item.

#### Parameters:

- `dataset_id` (required): The ID of the dataset
- `item_id` (required): The ID of the item to delete

## Python Example

Here's a Python example for creating and managing datasets:

```python
import requests
import json

class TestRailAPI:
    def __init__(self, url, email, api_key):
        self.url = url
        self.email = email
        self.api_key = api_key
        
    def get_datasets(self, project_id):
        api_url = f"{self.url}/index.php?/api/v2/get_datasets/{project_id}"
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'}
        )
        return response.json()
    
    def add_dataset(self, project_id, name, columns, items=None, description=None):
        api_url = f"{self.url}/index.php?/api/v2/add_dataset/{project_id}"
        
        payload = {
            "name": name,
            "columns": columns
        }
        
        if description:
            payload["description"] = description
            
        if items:
            payload["items"] = items
            
        response = requests.post(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        
        return response.json()
    
    def add_dataset_item(self, dataset_id, row_data):
        api_url = f"{self.url}/index.php?/api/v2/add_dataset_item/{dataset_id}"
        
        payload = {
            "row": row_data
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

# Create a new dataset
columns = [
    {
        "name": "username",
        "label": "Username",
        "description": "Username for login"
    },
    {
        "name": "password",
        "label": "Password",
        "description": "Password for login"
    },
    {
        "name": "role",
        "label": "Role",
        "description": "User role"
    }
]

dataset = testrail.add_dataset(
    project_id=1,
    name="Test Accounts",
    columns=columns,
    description="Test accounts for system testing"
)

print(f"Created dataset ID: {dataset['id']}")

# Add items to the dataset
testrail.add_dataset_item(
    dataset_id=dataset['id'],
    row_data={
        "username": "regular_user",
        "password": "test123",
        "role": "user"
    }
)

testrail.add_dataset_item(
    dataset_id=dataset['id'],
    row_data={
        "username": "admin_user",
        "password": "admin123",
        "role": "administrator"
    }
)

print("Added items to dataset")
```

## Using Datasets with Test Cases

Datasets can be used with parameterized test cases. When creating or updating test cases, you can reference datasets and their columns in custom fields or steps, depending on your TestRail configuration.

## Best Practices

1. Create well-structured datasets with clear column names and descriptions
2. Group related test data into logical datasets
3. Consider using datasets for data-driven testing scenarios
4. Keep sensitive information (like passwords) secure by using placeholder values where possible
5. Maintain datasets regularly to ensure test data remains valid and up-to-date

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
