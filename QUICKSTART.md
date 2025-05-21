# TestRail Exporter Quick Start Guide

This guide will help you get started with the TestRail Exporter application quickly.

## Installation

1. **Prerequisites**:
   - Python 3.6 or higher
   - pip (Python package manager)

2. **Install the application**:
   ```bash
   git clone https://github.com/your-username/testrail-exporter.git
   cd testrail-exporter
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   # Standard method
   python testrail_exporter/main.py
   
   # If installed with pip install -e .
   testrail-exporter
   
   # For macOS users (recommended if you have Tcl/Tk issues)
   ./run_testrail_exporter.sh
   ```

## First Time Setup

1. **Configure TestRail Connection**:
   - The URL field defaults to `https://testrail.testeng.mlbinfra.net`
   - Enter your TestRail username
   - Enter your API key (found in TestRail under My Settings > API Keys)
   - Set your preferred export directory
   - Click "Test Connection" to verify
   - Click "Save Settings" to persist your settings

2. **Load Projects**:
   - Click "Load Projects" to retrieve available projects from TestRail
   - Select a project from the dropdown menu

## Exporting Test Cases

1. **Browse Suites and Sections**:
   - The treeview displays suites and their sections
   - Use the expand/collapse arrows to navigate
   - Suites with sections display an expand arrow

2. **Select Items to Export**:
   - Click on the checkboxes to select/deselect suites or sections
   - Click on suite/section names to highlight them for easier reading
   - Use "Check All" or "Uncheck All" for quick selection
   - Use "Expand All" or "Collapse All" for easier navigation

3. **Export**:
   - Click either "Export JSON" or "Export CSV" depending on your needs
   - Choose a location and filename in the save dialog
   - Watch the progress percentage indicator at the bottom of the window
   - Wait for the export to complete

## Understanding the Export Files

### JSON Format
The exported JSON file contains:
- Project information
- Test cases from selected suites/sections
- All standard and custom fields for each case

### CSV Format
The exported CSV file contains:
- One row per test case
- Columns for all standard and custom fields
- Suitable for importing into other tools or opening in Excel

## Troubleshooting

- **Connection issues**: Verify your URL, username, and API key
- **No projects shown**: Confirm you have access to projects in TestRail
- **Export errors**: Check your network connection and TestRail access

## Next Steps

- Map TestRail fields to X-ray fields for import
- Filter test cases by additional criteria
- Batch export multiple projects
- Customize CSV formats for specific tool imports