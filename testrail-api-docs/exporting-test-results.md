# Exporting Test Results via the API

This document describes how to export test results from TestRail using the API.

## Overview

The TestRail API allows you to programmatically retrieve test results data for:
- Reporting purposes
- Integration with other tools
- Data analysis
- Custom dashboard creation

## Getting Test Results

To export test results, you can use the following API endpoints:

### Get Results for a Test

```
GET index.php?/api/v2/get_results/{test_id}
```

This endpoint returns all test results for a specific test.

#### Parameters:

- `test_id` (required): The ID of the test

#### Optional Parameters:

- `limit`: The number of results to return (default: 250)
- `offset`: Where to start when returning records (default: 0)
- `status_id`: A comma-separated list of status IDs to filter by

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
  "results": [
    {
      "id": 1,
      "test_id": 1,
      "status_id": 1,
      "created_by": 1,
      "created_on": 1646318000,
      "assignedto_id": null,
      "comment": "Test passed successfully",
      "version": null,
      "elapsed": "30s",
      "defects": null,
      "custom_field1": "Value 1"
    }
  ]
}
```

### Get Results for a Run

```
GET index.php?/api/v2/get_results_for_run/{run_id}
```

This endpoint returns all test results for a specific test run.

#### Parameters:

- `run_id` (required): The ID of the test run

### Get Results for Multiple Tests

```
GET index.php?/api/v2/get_results_for_cases/{run_id}/{case_ids}
```

This endpoint returns test results for specific test cases within a test run.

#### Parameters:

- `run_id` (required): The ID of the test run
- `case_ids` (required): A comma-separated list of case IDs

## Export Options

### Filtering Results

You can filter results by:
- Status (passed, failed, etc.)
- Date range
- Specific test cases or sections

### Pagination

Most endpoints support pagination with `limit` and `offset` parameters to handle large data sets.

## Python Example

Here's a Python example to export test results from a run:

```python
import requests
import json
import csv

def export_test_results(url, email, api_key, run_id, output_file):
    api_url = f"{url}/index.php?/api/v2/get_results_for_run/{run_id}"
    
    response = requests.get(
        api_url,
        auth=(email, api_key),
        headers={'Content-Type': 'application/json'}
    )
    
    data = response.json()
    results = data['results']
    
    # Write results to CSV
    with open(output_file, 'w', newline='') as csvfile:
        fieldnames = ['test_id', 'status_id', 'created_on', 'comment', 'elapsed']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for result in results:
            writer.writerow({
                'test_id': result['test_id'],
                'status_id': result['status_id'],
                'created_on': result['created_on'],
                'comment': result['comment'],
                'elapsed': result['elapsed']
            })
    
    return len(results)

# Usage example
count = export_test_results(
    url="https://example.testrail.com",
    email="your_email@example.com",
    api_key="your_api_key",
    run_id=123,
    output_file="test_results.csv"
)

print(f"Exported {count} test results to CSV")
```

## Best Practices

1. Use bulk API methods when possible to reduce the number of API calls
2. Implement pagination for large test runs
3. Handle rate limits by adding delays between requests
4. Include error handling for API requests
5. Store results in structured formats (CSV, JSON, database) for analysis

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
