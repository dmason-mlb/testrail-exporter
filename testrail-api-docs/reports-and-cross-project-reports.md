# Reports and Cross-Project Reports API

This document describes how to work with reports and cross-project reports in TestRail using the API.

## Overview

TestRail provides reporting functionality to analyze test results and progress. The API provides methods to manage and run these reports.

## API Endpoints

### Get Reports

```
GET index.php?/api/v2/get_reports/{project_id}
```

Returns a list of available reports for a project.

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
  "reports": [
    {
      "id": 1,
      "name": "Test Status Report",
      "description": "Shows the status of tests across test runs",
      "plugin": "status_reports",
      "report_url": "https://example.testrail.com/index.php?/reports/view/1",
      "template_id": 1,
      "created_on": 1646317844,
      "created_by": 1
    },
    {
      "id": 2,
      "name": "Test Coverage Report",
      "description": "Shows test coverage for requirements",
      "plugin": "coverage_reports",
      "report_url": "https://example.testrail.com/index.php?/reports/view/2",
      "template_id": 2,
      "created_on": 1646317900,
      "created_by": 1
    }
  ]
}
```

### Get Report

```
GET index.php?/api/v2/get_report/{report_id}
```

Returns an existing report.

#### Parameters:

- `report_id` (required): The ID of the report

### Run Report

```
GET index.php?/api/v2/run_report/{report_id}
```

Runs an existing report and returns the results.

#### Parameters:

- `report_id` (required): The ID of the report

#### Response:

The response format depends on the type of report and will include the report data in JSON format.

### Get Cross-Project Reports

```
GET index.php?/api/v2/get_cross_project_reports/{group_id}
```

Returns a list of available cross-project reports for a report group.

#### Parameters:

- `group_id` (required): The ID of the report group

#### Response:

Similar to the response format for `get_reports` but with cross-project reports.

### Run Cross-Project Report

```
GET index.php?/api/v2/run_cross_project_report/{cross_project_report_id}
```

Runs an existing cross-project report and returns the results.

#### Parameters:

- `cross_project_report_id` (required): The ID of the cross-project report

#### Response:

The response format depends on the type of report and will include the report data in JSON format.

## Python Example

Here's a Python example for working with reports:

```python
import requests
import json

class TestRailAPI:
    def __init__(self, url, email, api_key):
        self.url = url
        self.email = email
        self.api_key = api_key
        
    def get_reports(self, project_id):
        api_url = f"{self.url}/index.php?/api/v2/get_reports/{project_id}"
        
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'}
        )
        
        return response.json()
    
    def run_report(self, report_id):
        api_url = f"{self.url}/index.php?/api/v2/run_report/{report_id}"
        
        response = requests.get(
            api_url,
            auth=(self.email, self.api_key),
            headers={'Content-Type': 'application/json'}
        )
        
        return response.json()

# Usage example
testrail = TestRailAPI(
    url="https://example.testrail.com",
    email="your_email@example.com",
    api_key="your_api_key"
)

# Get all reports for project
reports = testrail.get_reports(1)
print("Available reports:")
for report in reports['reports']:
    print(f"- {report['name']}: {report['description']}")

# Find and run a specific report
status_report_id = next((r['id'] for r in reports['reports'] if r['name'] == 'Test Status Report'), None)

if status_report_id:
    # Run the report
    report_results = testrail.run_report(status_report_id)
    print(f"Report run completed with {len(report_results)} result rows")
    
    # Process report data (format depends on report type)
    # Example for a status report
    if 'status_totals' in report_results:
        print("Status totals:")
        for status, count in report_results['status_totals'].items():
            print(f"- {status}: {count}")
```

## Exporting Report Data

You can use the API to automate report generation and export the data to other systems:

```python
import csv
import os

def export_report_to_csv(report_data, file_path):
    """
    Exports report data to a CSV file.
    Assumes report_data has a 'rows' list with dictionary items.
    """
    if 'rows' not in report_data or not report_data['rows']:
        print("No data to export")
        return False
    
    # Extract field names from first row
    fieldnames = report_data['rows'][0].keys()
    
    with open(file_path, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(report_data['rows'])
    
    return True

# Run a report and export the data
report_results = testrail.run_report(status_report_id)
success = export_report_to_csv(report_results, "test_status_report.csv")

if success:
    print(f"Report exported to {os.path.abspath('test_status_report.csv')}")
```

## Building Custom Reports

While the API doesn't directly support creating custom reports, you can use the API to retrieve test data and build your own reports:

```python
# Example: Build a custom test execution trend report
def get_test_execution_trends(project_id, days=30):
    # Get all test runs in the last X days
    from_timestamp = int(time.time()) - (days * 86400)
    
    # Get all test runs
    runs = get_runs(project_id, created_after=from_timestamp)
    
    # Get all test results for each run
    trend_data = []
    for run in runs:
        results = get_results_for_run(run['id'])
        
        # Count status totals
        status_counts = {}
        for result in results:
            status_id = result['status_id']
            if status_id in status_counts:
                status_counts[status_id] += 1
            else:
                status_counts[status_id] = 1
        
        trend_data.append({
            'date': run['created_on'],
            'run_id': run['id'],
            'run_name': run['name'],
            'status_counts': status_counts
        })
    
    return trend_data
```

## Best Practices

1. Use the API to automate regular report generation
2. Export report data to external systems for additional analysis
3. Combine TestRail report data with data from other systems for comprehensive reporting
4. Consider caching report results when running resource-intensive reports
5. Be mindful of performance impact when running complex reports
6. Schedule report generation during off-peak hours for large datasets
7. Filter report data appropriately to focus on relevant information

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
