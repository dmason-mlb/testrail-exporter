# Testing the TestRail Exporter

This document outlines how to test the TestRail Exporter application during development.

## Prerequisites

Before testing, ensure you have:

1. Python 3.6 or higher installed
2. Required packages installed via `pip install -r requirements.txt`
3. A TestRail account with API access
4. TestRail API key (available under My Settings > API Keys in TestRail)

## Running the Application for Testing

1. From the repository root directory, run:
   ```
   python testrail-exporter/main.py
   ```

2. The application should launch with the settings panel visible.

## Test Scenarios

### Connection Settings

1. **Test Default URL**:
   - The URL field should default to `https://testrail.testeng.mlbinfra.net`
   - The username and API key fields should be empty unless environment variables are set

2. **Test Connection**:
   - Enter valid credentials and click "Test Connection"
   - Status should show successful connection with number of projects found
   - Try with invalid credentials and verify error message

### Project Loading

1. **Load Projects**:
   - Click "Load Projects" with valid credentials
   - Project dropdown should populate with available projects
   - Select different projects and verify suite loading

### Suite and Section Navigation

1. **Suite Tree View**:
   - After selecting a project, verify suites appear in the tree view
   - Suites with sections should show expand/collapse indicators
   - Expand a suite to see its sections

2. **Tree Controls**:
   - Test "Expand All" and "Collapse All" buttons
   - Test "Check All" and "Uncheck All" buttons
   - Verify parent checkbox behavior when checking/unchecking children

### Export Functionality

1. **Export Selection**:
   - Select several suites and sections by checking their checkboxes
   - Click "Export" button
   - Verify save dialog appears with default name
   - Save to a location and verify JSON file is created

2. **Export Content**:
   - Open the exported JSON file
   - Verify project information is included
   - Verify selected suites and sections have their cases exported
   - Verify all case fields are present

### Error Handling

1. **Network Interruption**:
   - Disconnect from the network during an operation
   - Verify appropriate error message is displayed

2. **Invalid Export Directory**:
   - Set an invalid export directory
   - Verify appropriate handling/error message

## Reporting Issues

When reporting issues, please include:

1. Steps to reproduce the issue
2. Expected behavior
3. Actual behavior
4. Error messages (if any)
5. Environment details (OS, Python version)