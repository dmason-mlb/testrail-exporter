# Introduction to the TestRail API

TestRail's API can be used to integrate TestRail with various tools, frameworks and third-party applications. The API is HTTP-based and can be used from virtually any framework, programming language and tool.

## API Overview

- TestRail's API is HTTP-based
- Submit data to TestRail via simple POST requests
- Request data via GET requests
- All requests and responses use the JSON format and UTF-8 encoding
- The API is part of TestRail and can be enabled in TestRail's administration area under Admin > Site Settings > API

## Before Using the API

Before reading through the API reference, make yourself familiar with TestRail's entities such as cases, runs & results, suites etc. Refer to TestRail's User Guide with getting started topics and best practices.

## Rate Limits

- The API is rate-limited on TestRail Cloud to ensure optimal performance for all users
- TestRail might return a 429 Too Many Requests response with a Retry-After header
- To avoid rate limits:
  - Use bulk API endpoints (e.g., add_results_for_cases instead of add_results_for_case)
  - Build a time delay into your API calls
  - Upgrade to TestRail Enterprise Cloud
- No API rate limits are built into TestRail Server installations

## Bulk API Endpoints

There are many bulk API endpoints available in TestRail that enable you to retrieve information about multiple cases, tests, or other TestRail entities with a single GET request.

## Finding IDs in TestRail

Many TestRail API endpoints require you to add an ID value in the request URL to specify certain projects, cases, test runs, and more. Here's how to find specific IDs in TestRail UI:

### Milestone ID
1. Go to the 'Dashboard' on your TestRail instance
2. Select a project from the list
3. Navigate to the 'Milestones' tab
4. Select a milestone from the list
5. Check the URL - the numeric character at the end is the Milestone ID
6. You can also get the ID next to Milestone Name
7. Omit the character 'M' when using API requests

### Test Plan ID
1. Go to the 'Dashboard' on your TestRail instance
2. Select a project from the list
3. Navigate to the 'Test Runs and Results' tab
4. Select a test plan from the list
5. Check the URL - the numeric character at the end is the Test Plan ID
6. You can also get the ID next to Test Plan Name
7. Omit the character 'R' when using API requests

## Response Format

The documentation uses truncated responses (indicated by `..`) for readability. For example:

```json
{
  "offset": 0,
  "limit": 250,
  "size": 250,
  "_links":{
    "next": "/api/v2/get_cases/1&limit=250&offset=250",
    "prev": null
  },
  "cases":[
    {
      "id": 1,
      "title": "..",
      ..
    },
    {
      "id": 2,
      "title": "..",
      ..
    },
    ..
  ]
}
```

This documentation is based on information available from the TestRail Support Center and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
