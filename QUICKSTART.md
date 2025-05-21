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
   python testrail-exporter/main.py
   ```

## First Time Setup

1. **Configure TestRail Connection**:
   - The URL field defaults to `https://testrail.testeng.mlbinfra.net`
   - Enter your TestRail username
   - Enter your API key (found in TestRail under My Settings > API Keys)
   - Set your preferred export directory
   - Click "Test Connection" to verify

2. **Load Projects**:
   - Click "Load Projects" to retrieve available projects from TestRail
   - Select a project from the dropdown menu

## Exporting Test Cases

1. **Browse Suites and Sections**:
   - The treeview displays suites and their sections
   - Use the expand/collapse arrows to navigate
   - Suites with sections display an expand arrow

2. **Select Items to Export**:
   - Check the boxes next to suites or sections you want to export
   - Use "Check All" or "Uncheck All" for quick selection
   - Use "Expand All" or "Collapse All" for easier navigation

3. **Export**:
   - Click the "Export" button
   - Choose a location and filename in the save dialog
   - Wait for the export to complete

## Understanding the Export File

The exported JSON file contains:
- Project information
- Test cases from selected suites/sections
- All standard and custom fields for each case

## Troubleshooting

- **Connection issues**: Verify your URL, username, and API key
- **No projects shown**: Confirm you have access to projects in TestRail
- **Export errors**: Check your network connection and TestRail access

## Next Steps

- Create CSV templates for X-ray import
- Set up regular export schedules
- Filter cases by criteria