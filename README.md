# TestRail Exporter

A Python GUI application to export test cases from TestRail for later importing into X-ray.

## Features

- Connect to TestRail instance with URL, username, and API key
- Browse projects, test suites, and sections
- Select test suites and sections to export
- Export test cases to JSON format
- Configurable export directory

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/your-username/testrail-exporter.git
   cd testrail-exporter
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

1. Run the application:
   ```
   python testrail-exporter/main.py
   ```

2. Configure TestRail connection:
   - Enter your TestRail URL (default: https://testrail.testeng.mlbinfra.net)
   - Enter your TestRail username
   - Enter your TestRail API key (can be generated in TestRail under My Settings > API Keys)
   - Configure export directory

3. Click "Test Connection" to verify your credentials

4. Click "Load Projects" to load projects from TestRail

5. Select a project from the dropdown

6. Check the suites and sections you want to export

7. Click "Export" to export the test cases to a JSON file

## Development

The project is structured as follows:

- `api/`: TestRail API client
- `gui/`: User interface components
- `models/`: Data models for TestRail entities
- `utils/`: Utility functions including export functionality

## Future Enhancements

- Export to CSV format compatible with X-ray
- Filter test cases by additional criteria
- Save/load export configurations
- Batch export multiple projects
- Progress tracking for large exports

## License

[MIT License](LICENSE)