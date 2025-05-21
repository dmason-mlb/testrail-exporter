# Attachments API

This document describes how to work with attachments in TestRail using the API.

## Overview

TestRail allows you to attach files to various entities such as test cases, test results, and more. The API provides endpoints to add and retrieve these attachments.

**Note:** To upload attachments using the API, you must be using TestRail 5.7 or later.

## Getting Attachments

### Get Attachments for Case

```
GET index.php?/api/v2/get_attachments_for_case/{case_id}
```

Returns a list of attachments for a test case.

#### Parameters:

- `case_id` (required): The ID of the test case

### Get Attachments for Test

```
GET index.php?/api/v2/get_attachments_for_test/{test_id}
```

Returns a list of attachments for a test.

#### Parameters:

- `test_id` (required): The ID of the test

### Get Attachment

```
GET index.php?/api/v2/get_attachment/{attachment_id}
```

Returns an attachment by ID.

#### Parameters:

- `attachment_id` (required): The ID of the attachment to retrieve

#### Response:

The response contains the attachment content with the appropriate Content-Type header.

## Adding Attachments

### Add Attachment to Case

```
POST index.php?/api/v2/add_attachment_to_case/{case_id}
```

Adds an attachment to a test case.

#### Parameters:

- `case_id` (required): The ID of the test case

### Add Attachment to Result

```
POST index.php?/api/v2/add_attachment_to_result/{result_id}
```

Adds an attachment to a test result.

#### Parameters:

- `result_id` (required): The ID of the test result

### Add Attachment to Plan

```
POST index.php?/api/v2/add_attachment_to_plan/{plan_id}
```

Adds an attachment to a test plan.

#### Parameters:

- `plan_id` (required): The ID of the test plan

### Add Attachment to Plan Entry

```
POST index.php?/api/v2/add_attachment_to_plan_entry/{plan_id}/{entry_id}
```

Adds an attachment to a test plan entry.

#### Parameters:

- `plan_id` (required): The ID of the test plan
- `entry_id` (required): The ID of the test plan entry

## Uploading Attachments

Unlike standard API requests, attachments must be uploaded using multipart/form-data encoding. The attachment should be included in the request as a file field named 'attachment'.

### Python Example for Uploading an Attachment

```python
import requests

def add_attachment_to_result(url, email, api_key, result_id, file_path):
    api_url = f"{url}/index.php?/api/v2/add_attachment_to_result/{result_id}"
    
    with open(file_path, 'rb') as file:
        files = {'attachment': (file_path.split('/')[-1], file, 'application/octet-stream')}
        
        response = requests.post(
            api_url,
            auth=(email, api_key),
            files=files
        )
    
    return response.json()

# Usage example
attachment = add_attachment_to_result(
    url="https://example.testrail.com",
    email="your_email@example.com",
    api_key="your_api_key",
    result_id=123,
    file_path="./screenshot.png"
)

print(f"Uploaded attachment ID: {attachment['id']}")
```

## Deleting Attachments

### Delete Attachment

```
POST index.php?/api/v2/delete_attachment/{attachment_id}
```

Deletes an attachment.

#### Parameters:

- `attachment_id` (required): The ID of the attachment to delete

## Best Practices

1. Keep attachment sizes reasonable to avoid upload issues
2. Use appropriate MIME types when uploading attachments
3. Consider compression for large files
4. Handle rate limits when uploading multiple attachments
5. Implement proper error handling for upload failures

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
