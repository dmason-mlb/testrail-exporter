# Python Binding for TestRail API

This document describes how to use the TestRail API with Python.

## Requirements

- Python 3.x
- Requests library (`pip install requests`)

## TestRail API Python Client

TestRail provides an official Python client that you can use to interact with the TestRail API. This client simplifies the process of communicating with TestRail from your Python code.

## Basic Usage

Here's a basic example of how to use the TestRail API with Python:

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
    
    def add_result(self, test_id, status_id, comment=None):
        api_url = f"{self.url}/index.php?/api/v2/add_result/{test_id}"
        data = {
            'status_id': status_id
        }
        if comment:
            data['comment'] = comment
            
        response = requests.post(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'},
            data=json.dumps(data)
        )
        return response.json()
```

## Example: Adding Test Results

Here's an example of how to add test results to TestRail:

```python
# Initialize TestRail API client
testrail = TestRailAPI(
    url='https://example.testrail.com',
    email='your_email@example.com',
    api_key='your_api_key'
)

# Add a test result
result = testrail.add_result(
    test_id=123,
    status_id=1,  # 1 = Passed
    comment='Test completed successfully'
)

print(f"Result ID: {result['id']}")
```

## Error Handling

It's important to handle potential errors when working with the TestRail API:

```python
import requests
import json

class TestRailAPIError(Exception):
    pass

class TestRailAPI:
    # ... (initialization as before)
    
    def get_case(self, case_id):
        api_url = f"{self.url}/index.php?/api/v2/get_case/{case_id}"
        try:
            response = requests.get(
                api_url,
                auth=(self.email, self.api_key),
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()  # Raise exception for 4XX/5XX responses
            return response.json()
        except requests.exceptions.RequestException as e:
            raise TestRailAPIError(f"Error making request to TestRail API: {str(e)}")
```

## Working with Attachments

To upload attachments using the API, you must be using TestRail 5.7 or later. The attachment endpoints require special handling in Python.

## Rate Limiting Considerations

When making multiple API requests, consider implementing rate limiting to avoid hitting TestRail Cloud rate limits:

```python
import time

# Add delay between API calls
def get_multiple_cases(self, case_ids):
    results = []
    for case_id in case_ids:
        results.append(self.get_case(case_id))
        time.sleep(0.5)  # Add a 500ms delay between requests
    return results
```

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
