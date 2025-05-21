# TestRail API Endpoints Used

This document outlines the TestRail API endpoints used in this application and their purposes.

## Authentication

TestRail API uses Basic Authentication with username and API key (not password).

## Base URL

The base URL for all API requests is: `https://<your-instance>/index.php?/api/v2/`

## Endpoints

### Projects

#### `GET get_projects`

- **Purpose**: Retrieve a list of all available projects
- **Parameters**:
  - `is_completed` (optional): 0 for active projects only, 1 for completed projects only
- **Response**: List of project objects with id, name, and other details
- **Used In**: Project dropdown population

#### `GET get_project/{project_id}`

- **Purpose**: Retrieve details for a specific project
- **Parameters**: 
  - `project_id` (required): The numeric ID of the project
- **Response**: Project object with all details
- **Used In**: Getting project details after selection

### Suites

#### `GET get_suites/{project_id}`

- **Purpose**: Retrieve all test suites for a specific project
- **Parameters**:
  - `project_id` (required): The numeric ID of the project
- **Response**: List of suite objects
- **Used In**: Populating the suite tree view

#### `GET get_suite/{suite_id}`

- **Purpose**: Retrieve details for a specific test suite
- **Parameters**:
  - `suite_id` (required): The numeric ID of the test suite
- **Response**: Suite object with all details
- **Used In**: Getting additional suite details when needed

### Sections

#### `GET get_sections/{project_id}`

- **Purpose**: Retrieve sections for a project and test suite
- **Parameters**:
  - `project_id` (required): The numeric ID of the project
  - `suite_id` (optional but required for multi-suite projects): Numeric ID of the test suite
- **Response**: List of section objects
- **Used In**: Populating section nodes under suites in the tree view

### Cases

#### `GET get_cases/{project_id}`

- **Purpose**: Retrieve test cases for a project, optionally filtered by suite and section
- **Parameters**:
  - `project_id` (required): The numeric ID of the project
  - `suite_id` (optional): Numeric ID of the test suite
  - `section_id` (optional): Numeric ID of the section
- **Response**: List of test case objects with details
- **Used In**: Exporting test cases for selected suites/sections

#### `GET get_case/{case_id}`

- **Purpose**: Retrieve details for a specific test case
- **Parameters**:
  - `case_id` (required): The numeric ID of the test case
- **Response**: Case object with all details
- **Used In**: Getting additional case details when needed

## API Response Processing

The application processes API responses as follows:

1. Projects are loaded into the dropdown menu
2. When a project is selected, suites for that project are retrieved
3. For each suite, sections are retrieved and organized in the tree view
4. When export is requested, cases are retrieved for all selected suites and sections
5. Case data is processed and exported to JSON or CSV format

## Error Handling

API errors are captured and displayed to the user through:
- Status messages in the UI
- Error dialogs with detailed information
- Progress indicators for long-running operations with counts and percentages
- Scrollable error messages that can be easily copied

The application implements additional error handling mechanisms:
- Automatic retry for connection failures (up to 3 times with exponential backoff)
- Timeout handling to prevent hanging on slow responses
- Detailed error messages with URLs and status codes
- JSON parsing error handling

## Rate Limiting

TestRail Cloud has rate limits. To mitigate issues:

- Use bulk endpoints where possible
- Process data in batches
- Provide feedback to users during long operations
- Handle 429 (Too Many Requests) errors appropriately