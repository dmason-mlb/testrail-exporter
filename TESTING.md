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
   # Standard method
   python testrail_exporter/main.py
   
   # For macOS users with Tcl/Tk compatibility issues
   ./run_testrail_exporter.sh
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
   - Test "Save Settings" button and verify settings are persisted when reopening the app

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
   - Test both "Export JSON" and "Export CSV" buttons
   - Verify save dialog appears with appropriate default name
   - Save to a location and verify files are created
   - Check progress indicators during export

2. **JSON Export Content**:
   - Open the exported JSON file
   - Verify project information is included
   - Verify selected suites and sections have their cases exported
   - Verify all case fields are present

3. **CSV Export Content**:
   - Open the exported CSV file
   - Verify all test cases are included
   - Verify columns for all fields are present
   - Verify CSV can be opened in spreadsheet applications

### Error Handling

1. **Network Interruption**:
   - Disconnect from the network during an operation
   - Verify appropriate error message is displayed
   - Verify retry mechanism works when network is restored

2. **Invalid Export Directory**:
   - Set an invalid export directory
   - Verify appropriate handling/error message
   
3. **Configuration File Testing**:
   - Delete configuration file in ~/.testrail_exporter/
   - Verify application creates a new default configuration
   - Modify configuration file with invalid data
   - Verify application handles corrupt configuration gracefully

## Reporting Issues

When reporting issues, please include:

1. Steps to reproduce the issue
2. Expected behavior
3. Actual behavior
4. Error messages (if any)
5. Environment details (OS, Python version)