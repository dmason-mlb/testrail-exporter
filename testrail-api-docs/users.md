# Users API

This document describes how to work with users in TestRail using the API.

## Overview

The Users API provides access to user accounts in TestRail. You can retrieve user information, create new users, and update existing users.

## API Endpoints

### Get User

```
GET index.php?/api/v2/get_user/{user_id}
```

Returns an existing user.

#### Parameters:

- `user_id` (required): The ID of the user

#### Response Example:

```json
{
  "id": 1,
  "name": "John Smith",
  "email": "john.smith@example.com",
  "is_active": true,
  "role_id": 1,
  "role": "Lead",
  "groups": [1, 2],
  "group_ids": [1, 2]
}
```

### Get Users

```
GET index.php?/api/v2/get_users
```

Returns the list of users.

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
  "users": [
    {
      "id": 1,
      "name": "John Smith",
      "email": "john.smith@example.com",
      "is_active": true,
      "role_id": 1,
      "role": "Lead"
    },
    {
      "id": 2,
      "name": "Jane Doe",
      "email": "jane.doe@example.com",
      "is_active": true,
      "role_id": 2,
      "role": "Tester"
    }
  ]
}
```

### Get User by Email

```
GET index.php?/api/v2/get_user_by_email&email={email}
```

Returns an existing user by their email address.

#### Parameters:

- `email` (required): The email address of the user

#### Response Example:

```json
{
  "id": 1,
  "name": "John Smith",
  "email": "john.smith@example.com",
  "is_active": true,
  "role_id": 1,
  "role": "Lead",
  "groups": [1, 2],
  "group_ids": [1, 2]
}
```

### Add User

```
POST index.php?/api/v2/add_user
```

Creates a new user.

#### Request Fields:

- `email` (required): The email address of the new user
- `name` (required): The full name of the new user
- `password` (optional): The password of the new user (leave blank to send an invitation link)
- `role_id` (optional): The ID of the role for the new user
- `group_ids` (optional): An array of group IDs for the new user

#### Request Example:

```json
{
  "email": "new.user@example.com",
  "name": "New User",
  "password": "securepassword123",
  "role_id": 2,
  "group_ids": [1, 3]
}
```

### Update User

```
POST index.php?/api/v2/update_user/{user_id}
```

Updates an existing user.

#### Parameters:

- `user_id` (required): The ID of the user

#### Request Fields:

- `email`: The email address of the user
- `name`: The full name of the user
- `password`: The password of the user (leave blank to keep current password)
- `role_id`: The ID of the role for the user
- `is_active`: Whether the user is active (`true` or `false`)
- `group_ids`: An array of group IDs for the user

### Delete User

```
POST index.php?/api/v2/delete_user/{user_id}
```

Deletes an existing user.

#### Parameters:

- `user_id` (required): The ID of the user to delete

## Python Example

Here's a Python example for working with users:

```python
import requests
import json

class TestRailAPI:
    def __init__(self, url, email, api_key):
        self.url = url
        self.email = email
        self.api_key = api_key
        
    def get_users(self):
        api_url = f"{self.url}/index.php?/api/v2/get_users"
        
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'}
        )
        
        return response.json()
    
    def get_user(self, user_id):
        api_url = f"{self.url}/index.php?/api/v2/get_user/{user_id}"
        
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'}
        )
        
        return response.json()
    
    def get_user_by_email(self, email):
        api_url = f"{self.url}/index.php?/api/v2/get_user_by_email&email={email}"
        
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'}
        )
        
        return response.json()
    
    def add_user(self, email, name, password=None, role_id=None, group_ids=None):
        api_url = f"{self.url}/index.php?/api/v2/add_user"
        
        payload = {
            "email": email,
            "name": name
        }
        
        if password:
            payload["password"] = password
            
        if role_id:
            payload["role_id"] = role_id
            
        if group_ids:
            payload["group_ids"] = group_ids
        
        response = requests.post(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(payload)
        )
        
        return response.json()
    
    def update_user(self, user_id, email=None, name=None, password=None, 
                   role_id=None, is_active=None, group_ids=None):
        api_url = f"{self.url}/index.php?/api/v2/update_user/{user_id}"
        
        payload = {}
        
        if email:
            payload["email"] = email
            
        if name:
            payload["name"] = name
            
        if password:
            payload["password"] = password
            
        if role_id is not None:
            payload["role_id"] = role_id
            
        if is_active is not None:
            payload["is_active"] = is_active
            
        if group_ids:
            payload["group_ids"] = group_ids
        
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

# Get all users
users = testrail.get_users()
print("Users in TestRail:")
for user in users['users']:
    active = "" if user['is_active'] else " (inactive)"
    print(f"- {user['name']} ({user['email']}) - {user['role']}{active}")

# Find a user by email
user = testrail.get_user_by_email("jane.doe@example.com")
print(f"Found user: {user['name']} (ID: {user['id']})")

# Add a new user
new_user = testrail.add_user(
    email="new.tester@example.com",
    name="New Tester",
    role_id=2,  # Tester
    group_ids=[1]  # Add to group ID 1
)
print(f"Created new user: {new_user['name']} (ID: {new_user['id']})")

# Update a user
updated_user = testrail.update_user(
    user_id=new_user['id'],
    name="Updated Tester Name"
)
print(f"Updated user name to: {updated_user['name']}")

# Deactivate a user
deactivated_user = testrail.update_user(
    user_id=new_user['id'],
    is_active=False
)
print(f"Deactivated user: {deactivated_user['name']}")
```

## Bulk User Management

To efficiently manage multiple users, you can create helper functions:

```python
def get_inactive_users():
    """
    Gets all inactive users in TestRail.
    """
    users = get_users()['users']
    return [user for user in users if not user['is_active']]

def add_multiple_users(users_data):
    """
    Adds multiple users to TestRail.
    
    users_data: A list of dictionaries with user details.
    """
    results = []
    
    for user_data in users_data:
        try:
            user = add_user(
                email=user_data['email'],
                name=user_data['name'],
                role_id=user_data.get('role_id'),
                group_ids=user_data.get('group_ids')
            )
            results.append({
                'success': True,
                'user': user
            })
        except Exception as e:
            results.append({
                'success': False,
                'email': user_data['email'],
                'error': str(e)
            })
    
    return results

# Example usage:
users_to_add = [
    {
        'email': 'user1@example.com',
        'name': 'User One',
        'role_id': 2
    },
    {
        'email': 'user2@example.com',
        'name': 'User Two',
        'role_id': 2
    }
]

results = add_multiple_users(users_to_add)
for result in results:
    if result['success']:
        print(f"Added user: {result['user']['name']}")
    else:
        print(f"Failed to add user {result['email']}: {result['error']}")
```

## User Roles and Permissions

When creating or updating users, you can assign them to specific roles. TestRail includes several built-in roles, and you can create custom roles as needed. Here are some common role IDs:

1. Administrator
2. Tester
3. Lead
4. Read-only

To get the available roles, you can use the Roles API (`get_roles`).

## User Groups

Users can be assigned to groups for easier permission management. You can assign users to multiple groups when creating or updating them.

## Best Practices

1. Use descriptive names for users
2. Assign appropriate roles based on user responsibilities
3. Consider using groups for permission management
4. Deactivate rather than delete users when they no longer need access
5. Use secure passwords when creating users
6. Document your user management process
7. Regularly review user accounts and permissions
8. Consider implementing user synchronization with other systems

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
