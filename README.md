<div align="center">
  <img src="./final_icon.png" alt="TestRail Exporter Logo" width="128" height="128">
  
  # TestRail Exporter
  
  A Python GUI application to export test cases from TestRail for later importing into X-ray.
</div>

## Quick Installation (macOS)

Download the latest release and drag TestRail Exporter to your Applications folder:

![TestRail Exporter DMG Installer](./docs/images/dmg_installer.png)

1. Download the latest `.dmg` file from the [Releases](https://github.com/dmason-mlb/testrail-exporter/releases) page
2. Open the downloaded DMG file
3. Drag TestRail Exporter to your Applications folder
4. Launch TestRail Exporter from your Applications folder

## Features

- Connect to TestRail instance with URL, username, and API key
- Browse projects, test suites, and sections (single-project mode)
- Select entire projects for export (multi-project mode)
- Select specific test case fields to include in Xray CSV exports (column selection dialog)
- Export test cases to JSON, XML, or Xray-compatible CSV format (direct CSV export, no XML intermediate required)
- Multi-project export: export each selected project to its own file(s)
- Configurable export directory
- Persistent settings between sessions (window size, last project, export directory, credentials)
- Progress tracking during API operations with percentage completion and status messages
- Auto-loading of projects on startup when settings are configured
- Data caching for improved performance
- Toggle to control section loading for better performance
- Export logs saved in a dedicated logs directory within your export directory
- Custom checkable tree view for intuitive selection of suites, sections, or projects

## Environment Setup

### Prerequisites

- Python 3.6 or higher
- pip (Python package manager)
- Access to a TestRail instance with API permissions
- TestRail API key (generated in TestRail under My Settings > API Keys)
- Tkinter and Tcl/Tk 8.6.x (Python's GUI toolkit)

### Environment Variables (Optional)

The application can use the following environment variables for testing:

```bash
export TESTRAIL_URL="https://testrail.testeng.mlbinfra.net"
export TESTRAIL_USER="your_username"
export TESTRAIL_KEY="your_api_key"
```

Note: While environment variables can be used for testing, the application itself uses the settings configured in the GUI.

## Installation

1. Clone this repository:
   ```bash
   git clone https://github.com/your-username/testrail-exporter.git
   cd testrail-exporter
   ```

2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. For development installation:
   ```bash
   pip install -e .
   ```

> **Note for macOS users**: 
> If you're using pyenv or Homebrew Python on macOS, you might encounter Tcl/Tk compatibility issues.
> Please see [INSTALL_MACOS.md](INSTALL_MACOS.md) for detailed instructions on resolving these issues.

## Application Configuration

### TestRail Connection

The application requires the following configuration to connect to TestRail:

1. **TestRail URL**: The URL of your TestRail instance
   - Default: `https://testrail.testeng.mlbinfra.net`

2. **Username**: Your TestRail username

3. **API Key**: Your TestRail API key
   - Can be generated in TestRail under My Settings > API Keys

4. **Export Directory**: The directory where exported files will be saved
   - Default: `~/Documents`

### Configuration Testing

Use the "Test Connection" button to verify your credentials before loading projects.

## Usage

1. Run the application:
   ```bash
   python testrail_exporter/main.py
   # or, if installed:
   testrail-exporter
   ```

2. Configure TestRail connection:
   - Enter your TestRail URL, username, and API key
   - Set your export directory

3. Click "Test Connection" to verify your credentials

4. Click "Load Projects" to load projects from TestRail

5. **Single-project mode:**
   - Select a project from the dropdown
   - Browse and select suites and/or sections to export

6. **Multi-project mode:**
   - Toggle "Multi-Project Selection" ON
   - Select one or more projects from the list (suite/section selection is not available in this mode)

7. Choose export format:
   - Click "Export to XML" for TestRail-compatible XML
   - Click "Export to Xray CSV" for Xray-compatible CSV (a dialog will let you select columns)
   - Click "Export Both" to export both formats

8. Exported files are timestamped and saved in your export directory. Detailed logs are saved in a `logs` subdirectory.

## Export Formats

### JSON Format

The exported JSON file contains:

- Project information (id, name)
- Test cases with:
  - Standard fields (id, title, suite_name, section_name, etc.)
  - Human-readable names instead of IDs (suite_name, section_name, priority_name, type_name)
  - Custom fields (prefixed with `custom_`)

### Xray CSV Format

- Direct export to Xray-compatible CSV (no XML intermediate required)
- Column selection dialog allows you to choose which fields to include (some columns are mandatory)
- Each project is exported to its own CSV file in multi-project mode
- Handles test steps, expected results, and section hierarchy for Xray import
- Proper priority mapping (Critical=1, High=2, Medium=3, Low=4)
- Test type conversion (Manual, Exploratory, Automated→Generic)
- Section hierarchy reflected in Test Repo field
- Clean HTML tag removal from test content

### XML Format

The exported XML file contains TestRail-compatible XML structure:

- Hierarchical structure with suites, sections, and cases
- Test cases with complete metadata including custom fields
- Compatible with TestRail's XML import format
- Human-readable names for types, priorities, and other fields

## Troubleshooting

- If you encounter errors during export, check the log files in the `logs` subdirectory of your export directory for detailed information.
- Common issues:
  - **Connection Failures:** Verify your TestRail URL, username, and API key. Ensure your user has API access permissions.
  - **No Projects Shown:** Verify your user has access to projects in TestRail.
  - **Export Errors:** Check your network connection and write permissions to the export directory.
  - **Installation Issues:** If you encounter module not found errors, ensure the package name in imports uses underscores (`testrail_exporter`) not hyphens. For Tkinter/Tcl/Tk errors on macOS, refer to [INSTALL_MACOS.md](INSTALL_MACOS.md).

### Logging

- Export operations create detailed log files in a `logs` subdirectory within your export directory
- Log files are timestamped for easy identification
- Logs include all API operations, errors, and export progress
- Console output shows real-time status during operations

## Development

The project is structured as follows:

- `api/`: TestRail API client
- `gui/`: User interface components (Tkinter/CustomTkinter, custom widgets)
- `models/`: Data models for TestRail entities
- `utils/`: Utility functions including export functionality

## License

[MIT License](LICENSE)