# BDDs API

This document describes how to work with Behavior-Driven Development (BDD) features in TestRail using the API.

## Overview

TestRail supports Behavior-Driven Development (BDD) by allowing you to create and manage BDD features and scenarios through the API. This integration enables teams to maintain BDD specifications alongside their test cases.

## API Endpoints

### Get BDDs

```
GET index.php?/api/v2/get_bdds/{project_id}
```

Returns a list of BDD features for a project.

#### Parameters:

- `project_id` (required): The ID of the project

#### Response Example:

```json
{
  "offset": 0,
  "limit": 250,
  "size": 1,
  "_links": {
    "next": null,
    "prev": null
  },
  "bdds": [
    {
      "id": 1,
      "project_id": 1,
      "name": "User Authentication",
      "slug": "user-authentication",
      "description": "Feature for user authentication flows",
      "content": "Feature: User Authentication\n\nScenario: Valid Login\nGiven I am on the login page\nWhen I enter valid credentials\nThen I should be logged in",
      "created_on": 1646317844,
      "created_by": 1,
      "updated_on": 1646317844,
      "updated_by": 1
    }
  ]
}
```

### Get BDD

```
GET index.php?/api/v2/get_bdd/{bdd_id}
```

Returns a specific BDD feature.

#### Parameters:

- `bdd_id` (required): The ID of the BDD feature

### Add BDD

```
POST index.php?/api/v2/add_bdd/{project_id}
```

Creates a new BDD feature in a project.

#### Parameters:

- `project_id` (required): The ID of the project

#### Request Fields:

- `name` (required): The name of the BDD feature
- `content` (required): The Gherkin content of the feature
- `description`: Optional description for the BDD feature

#### Request Example:

```json
{
  "name": "User Registration",
  "description": "Feature covering user registration flows",
  "content": "Feature: User Registration\n\nScenario: Successful Registration\nGiven I am on the registration page\nWhen I fill in valid details\nThen my account should be created"
}
```

### Update BDD

```
POST index.php?/api/v2/update_bdd/{bdd_id}
```

Updates an existing BDD feature.

#### Parameters:

- `bdd_id` (required): The ID of the BDD feature to update

#### Request Fields:

- `name`: The new name of the BDD feature
- `content`: The updated Gherkin content
- `description`: Updated description

### Delete BDD

```
POST index.php?/api/v2/delete_bdd/{bdd_id}
```

Deletes a BDD feature.

#### Parameters:

- `bdd_id` (required): The ID of the BDD feature to delete

## Python Example

Here's a Python example for creating a BDD feature:

```python
import requests
import json

def add_bdd_feature(url, email, api_key, project_id, name, content, description=None):
    api_url = f"{url}/index.php?/api/v2/add_bdd/{project_id}"
    
    payload = {
        "name": name,
        "content": content
    }
    
    if description:
        payload["description"] = description
    
    response = requests.post(
        api_url,
        auth=(email, api_key),
        headers={'Content-Type': 'application/json'},
        data=json.dumps(payload)
    )
    
    return response.json()

# Usage example
feature_content = """Feature: Shopping Cart
  As a customer
  I want to add items to my cart
  So that I can purchase them

  Scenario: Add item to empty cart
    Given I am on a product page
    When I click "Add to Cart"
    Then the item should be added to my cart
    And the cart count should be 1
"""

bdd = add_bdd_feature(
    url="https://example.testrail.com",
    email="your_email@example.com",
    api_key="your_api_key",
    project_id=1,
    name="Shopping Cart",
    content=feature_content,
    description="Features related to shopping cart functionality"
)

print(f"Created BDD feature ID: {bdd['id']}")
```

## Best Practices

1. Follow Gherkin syntax standards for BDD content
2. Keep scenarios focused and concise
3. Use consistent naming conventions for features
4. Link BDD features to relevant test cases when possible
5. Update BDD features when requirements change

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
