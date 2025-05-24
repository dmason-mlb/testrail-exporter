#!/usr/bin/env python3
"""
TestRail Export Script
Systematically downloads TestRail data and saves it as JSON files
"""

import os
import sys
import json
import requests
import logging
import time
from typing import Dict, Any, Optional, List
from urllib.parse import quote

# Configuration
DEBUG_LIMIT_PROJECTS = int(os.environ.get('DEBUG_LIMIT_PROJECTS', '0'))  # 0 = no limit

# TestRail API configuration from environment variables
TESTRAIL_URL = os.environ.get('TESTRAIL_URL', '').rstrip('/')
TESTRAIL_USER = os.environ.get('TESTRAIL_USER')
TESTRAIL_KEY = os.environ.get('TESTRAIL_KEY')

# Verify environment variables are set
if not all([TESTRAIL_URL, TESTRAIL_USER, TESTRAIL_KEY]):
    print("Error: Missing required environment variables")
    print("Please set: TESTRAIL_URL, TESTRAIL_USER, TESTRAIL_KEY")
    sys.exit(1)

# Set up logging to file instead of console
log_file = os.path.join(os.path.dirname(__file__), 'testrail_export.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
    ]
)
logger = logging.getLogger(__name__)

class StatusDisplay:
    """Manages status display that updates in place"""
    
    def __init__(self):
        self.total_projects = 0
        self.current_project_idx = 0
        self.current_project_name = ""
        self.total_suites = 0
        self.current_suite_idx = 0
        self.current_suite_name = ""
        self._last_lines = 0
    
    def update_project(self, idx: int, total: int, name: str):
        """Update project status"""
        self.current_project_idx = idx
        self.total_projects = total
        self.current_project_name = name
        self._display()
    
    def update_suite(self, idx: int, total: int, name: str):
        """Update suite status"""
        self.current_suite_idx = idx
        self.total_suites = total
        self.current_suite_name = name
        self._display()
    
    def clear_suite(self):
        """Clear suite status when project has no suites"""
        self.current_suite_idx = 0
        self.total_suites = 0
        self.current_suite_name = ""
        self._display()
    
    def _display(self):
        """Display the status lines"""
        # Clear previous lines
        if self._last_lines > 0:
            # Move cursor up and clear lines
            for _ in range(self._last_lines):
                print('\033[1A\033[2K', end='')
        
        # Print status lines
        lines = []
        
        # Project line
        if self.total_projects > 0:
            lines.append(f"{self.current_project_idx}/{self.total_projects} ~ {self.current_project_name}")
        
        # Suite line
        if self.total_suites > 0:
            lines.append(f"{self.current_suite_idx}/{self.total_suites} ~ {self.current_suite_name}")
        elif self.current_project_idx > 0:
            # Show placeholder when project has no suites
            lines.append("No suites (single suite mode)")
        
        # Print lines
        for line in lines:
            print(line)
        
        self._last_lines = len(lines)
        
        # Flush output to ensure immediate display
        sys.stdout.flush()

# Create global status display instance
status_display = StatusDisplay()

class TestRailAPI:
    """TestRail API client"""
    
    def __init__(self, url: str, user: str, api_key: str):
        self.url = url
        self.user = user
        self.api_key = api_key
        self.session = requests.Session()
        self.session.auth = (user, api_key)
        self.session.headers.update({'Content-Type': 'application/json'})
    
    def _make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make API request and handle errors with rate limit retry logic"""
        url = f"{self.url}/index.php?/api/v2/{endpoint}"
        
        max_retries = 5
        retry_delay = 10  # seconds
        
        for attempt in range(max_retries):
            try:
                if method == 'GET':
                    response = self.session.get(url)
                elif method == 'POST':
                    response = self.session.post(url, data=json.dumps(data) if data else None)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                # Check for rate limit error
                if response.status_code == 429:
                    if attempt < max_retries - 1:
                        logger.warning(f"Rate limit hit for {endpoint}. Waiting {retry_delay} seconds before retry {attempt + 1}/{max_retries}...")
                        time.sleep(retry_delay)
                        continue
                    else:
                        logger.error(f"Rate limit hit for {endpoint}. Maximum retries ({max_retries}) exceeded.")
                        raise requests.exceptions.HTTPError(f"429 Rate Limit Error after {max_retries} attempts", response=response)
                
                response.raise_for_status()
                return response.json()
                
            except requests.exceptions.RequestException as e:
                # If it's not a 429 error or we've exhausted retries, raise the error
                if not (hasattr(e, 'response') and e.response and e.response.status_code == 429):
                    logger.error(f"API request failed: {endpoint} - {str(e)}")
                    if hasattr(e, 'response') and e.response is not None:
                        logger.error(f"Response: {e.response.text}")
                    raise
                elif attempt == max_retries - 1:
                    logger.error(f"API request failed after {max_retries} attempts: {endpoint} - {str(e)}")
                    raise
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects"""
        result = self._make_request('GET', 'get_projects')
        return result.get('projects', []) if isinstance(result, dict) else result
    
    def get_case_fields(self) -> List[Dict[str, Any]]:
        """Get all case fields"""
        return self._make_request('GET', 'get_case_fields')
    
    def get_case_types(self) -> List[Dict[str, Any]]:
        """Get all case types"""
        return self._make_request('GET', 'get_case_types')
    
    def get_priorities(self) -> List[Dict[str, Any]]:
        """Get all priorities"""
        return self._make_request('GET', 'get_priorities')
    
    def get_templates(self, project_id: int) -> List[Dict[str, Any]]:
        """Get templates for a project"""
        return self._make_request('GET', f'get_templates/{project_id}')
    
    def get_suites(self, project_id: int) -> List[Dict[str, Any]]:
        """Get suites for a project"""
        return self._make_request('GET', f'get_suites/{project_id}')
    
    def get_users(self, project_id: int) -> List[Dict[str, Any]]:
        """Get users for a project"""
        result = self._make_request('GET', f'get_users/{project_id}')
        return result.get('users', []) if isinstance(result, dict) else result
    
    def get_milestones(self, project_id: int) -> List[Dict[str, Any]]:
        """Get milestones for a project"""
        result = self._make_request('GET', f'get_milestones/{project_id}')
        return result.get('milestones', []) if isinstance(result, dict) else result
    
    def get_sections(self, project_id: int, suite_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get sections for a project/suite"""
        endpoint = f'get_sections/{project_id}'
        if suite_id:
            endpoint += f'&suite_id={suite_id}'
        result = self._make_request('GET', endpoint)
        return result.get('sections', []) if isinstance(result, dict) else result
    
    def get_cases(self, project_id: int, suite_id: Optional[int] = None, section_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get cases for a project/suite/section"""
        endpoint = f'get_cases/{project_id}'
        params = []
        if suite_id:
            params.append(f'suite_id={suite_id}')
        if section_id:
            params.append(f'section_id={section_id}')
        if params:
            endpoint += '&' + '&'.join(params)
        
        cases = []
        offset = 0
        limit = 250  # TestRail API limit
        
        while True:
            paginated_endpoint = f"{endpoint}&limit={limit}&offset={offset}"
            result = self._make_request('GET', paginated_endpoint)
            
            if isinstance(result, dict) and 'cases' in result:
                batch = result['cases']
                cases.extend(batch)
                
                # Check if there are more results
                if len(batch) < limit:
                    break
                offset += limit
            else:
                # Fallback for older API versions
                cases = result
                break
        
        return cases


def sanitize_filename(name: str) -> str:
    """Sanitize filename to be filesystem-safe"""
    # Replace problematic characters
    replacements = {
        '/': '_',
        '\\': '_',
        ':': '_',
        '*': '_',
        '?': '_',
        '"': '_',
        '<': '_',
        '>': '_',
        '|': '_',
        '\n': '_',
        '\r': '_',
        '\t': '_'
    }
    
    for char, replacement in replacements.items():
        name = name.replace(char, replacement)
    
    # Remove leading/trailing spaces and dots
    name = name.strip('. ')
    
    # Limit length
    if len(name) > 200:
        name = name[:200]
    
    return name or 'unnamed'


def save_json(data: Any, filepath: str) -> None:
    """Save data as JSON file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved: {filepath}")


def main():
    """Main export function"""
    print("Starting TestRail export...")
    print(f"TestRail URL: {TESTRAIL_URL}")
    print(f"Logging to: {log_file}")
    
    logger.info("Starting TestRail export...")
    logger.info(f"TestRail URL: {TESTRAIL_URL}")
    
    if DEBUG_LIMIT_PROJECTS > 0:
        print(f"DEBUG MODE: Limiting to {DEBUG_LIMIT_PROJECTS} projects")
        logger.info(f"DEBUG MODE: Limiting to {DEBUG_LIMIT_PROJECTS} projects")
    
    # Initialize API client
    api = TestRailAPI(TESTRAIL_URL, TESTRAIL_USER, TESTRAIL_KEY)
    
    # Create export directory
    export_dir = os.path.join(os.path.dirname(__file__), 'export')
    os.makedirs(export_dir, exist_ok=True)
    
    try:
        # 1. Get and save projects
        print("Fetching initial data...")
        logger.info("Fetching projects...")
        projects = api.get_projects()
        save_json(projects, os.path.join(export_dir, 'projects.json'))
        
        # Create projects directory
        projects_dir = os.path.join(export_dir, 'projects')
        os.makedirs(projects_dir, exist_ok=True)
        
        # 2. Get and save global data
        logger.info("Fetching case fields...")
        case_fields = api.get_case_fields()
        save_json(case_fields, os.path.join(export_dir, 'case_fields.json'))
        
        logger.info("Fetching case types...")
        case_types = api.get_case_types()
        save_json(case_types, os.path.join(export_dir, 'case_types.json'))
        
        logger.info("Fetching priorities...")
        priorities = api.get_priorities()
        save_json(priorities, os.path.join(export_dir, 'priorities.json'))
        
        # Process each project
        projects_to_process = projects[:DEBUG_LIMIT_PROJECTS] if DEBUG_LIMIT_PROJECTS > 0 else projects
        
        # Initialize status display
        print("\n")  # Add some space for status display
        
        for idx, project in enumerate(projects_to_process, 1):
            project_id = project['id']
            project_name = sanitize_filename(project['name'])
            
            # Update status display
            status_display.update_project(idx, len(projects_to_process), project['name'])
            
            logger.info(f"Processing project: {project['name']} (ID: {project_id})")
            
            # Create project directory
            project_dir = os.path.join(projects_dir, project_name)
            os.makedirs(project_dir, exist_ok=True)
            
            # Save project info
            save_json(project, os.path.join(project_dir, 'project_info.json'))
            
            try:
                # 3. Get templates for project
                logger.info(f"  Fetching templates for project {project_id}...")
                templates = api.get_templates(project_id)
                save_json(templates, os.path.join(project_dir, 'templates.json'))
            except Exception as e:
                logger.warning(f"  Failed to fetch templates: {str(e)}")
            
            try:
                # 4. Get suites for project
                logger.info(f"  Fetching suites for project {project_id}...")
                suites = api.get_suites(project_id)
                save_json(suites, os.path.join(project_dir, 'suites.json'))
                
                # 5. Get users for project
                logger.info(f"  Fetching users for project {project_id}...")
                users = api.get_users(project_id)
                save_json(users, os.path.join(project_dir, 'users.json'))
                
                # 6. Get milestones for project
                logger.info(f"  Fetching milestones for project {project_id}...")
                milestones = api.get_milestones(project_id)
                save_json(milestones, os.path.join(project_dir, 'milestones.json'))
                
                # Process each suite
                if suites:
                    for suite_idx, suite in enumerate(suites, 1):
                        suite_id = suite['id']
                        suite_name = sanitize_filename(suite['name'])
                        
                        # Update suite status
                        status_display.update_suite(suite_idx, len(suites), suite['name'])
                        
                        logger.info(f"    Processing suite: {suite['name']} (ID: {suite_id})")
                        
                        # Create suite directory
                        suite_dir = os.path.join(project_dir, suite_name)
                        os.makedirs(suite_dir, exist_ok=True)
                        
                        # Save suite info
                        save_json(suite, os.path.join(suite_dir, 'suite_info.json'))
                        
                        try:
                            # 7. Get sections for suite
                            logger.info(f"      Fetching sections for suite {suite_id}...")
                            sections = api.get_sections(project_id, suite_id)
                            save_json(sections, os.path.join(suite_dir, 'sections.json'))
                            
                            # 8. Get cases for suite
                            logger.info(f"      Fetching cases for suite {suite_id}...")
                            cases = api.get_cases(project_id, suite_id)
                            save_json(cases, os.path.join(suite_dir, 'cases.json'))
                            logger.info(f"      Found {len(cases)} cases in suite {suite_id}")
                            
                        except Exception as e:
                            logger.error(f"      Failed to fetch data for suite {suite_id}: {str(e)}")
                else:
                    # For single suite mode projects
                    logger.info(f"    Project has no suites (single suite mode)")
                    
                    # Clear suite status for single suite mode
                    status_display.clear_suite()
                    
                    try:
                        # Get sections for project
                        logger.info(f"    Fetching sections for project {project_id}...")
                        sections = api.get_sections(project_id)
                        save_json(sections, os.path.join(project_dir, 'sections.json'))
                        
                        # Get cases for project
                        logger.info(f"    Fetching cases for project {project_id}...")
                        cases = api.get_cases(project_id)
                        save_json(cases, os.path.join(project_dir, 'cases.json'))
                        logger.info(f"    Found {len(cases)} cases in project {project_id}")
                        
                    except Exception as e:
                        logger.error(f"    Failed to fetch data for project {project_id}: {str(e)}")
                        
            except Exception as e:
                logger.error(f"  Failed to process project {project_id}: {str(e)}")
                continue
        
        # Clear status display
        print("\n")  # Add some space after status display
        print("Export completed successfully!")
        print(f"Check {log_file} for detailed logs.")
        logger.info("Export completed successfully!")
        
    except Exception as e:
        # Clear status display on error
        print("\n")  # Add some space after status display
        print(f"Export failed: {str(e)}")
        print(f"Check {log_file} for detailed error information.")
        logger.error(f"Export failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()