import requests
import json
import time
from urllib.parse import urljoin


class TestRailClient:
    """Client for interacting with the TestRail API."""

    def __init__(self, url, username, api_key):
        """
        Initialize the TestRail API client.

        Args:
            url (str): TestRail URL
            username (str): TestRail username
            api_key (str): TestRail API key
        """
        # Ensure URL doesn't have trailing slash but has the correct format
        self.url = url.rstrip('/')
        if not self.url.endswith('/index.php'):
            # TestRail API requires index.php in the path
            self.url = f"{self.url}/index.php"
            
        self.auth = (username, api_key)
        self.headers = {'Content-Type': 'application/json'}

    def _send_request(self, method, endpoint, data=None, params=None):
        """
        Send a request to the TestRail API.

        Args:
            method (str): HTTP method (GET, POST, etc.)
            endpoint (str): API endpoint
            data (dict, optional): Request data for POST requests
            params (dict, optional): Query parameters for GET requests

        Returns:
            dict: API response as JSON

        Raises:
            Exception: If the request fails
        """
        # Construct the full URL properly
        url = f"{self.url}?/api/v2/{endpoint}"
        
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    auth=self.auth,
                    headers=self.headers,
                    json=data,
                    params=params,
                    timeout=30  # Add timeout to prevent hanging
                )
                
                # Add request details to error message for debugging
                response.raise_for_status()
                
                try:
                    return response.json()
                except json.JSONDecodeError as je:
                    raise Exception(f"Invalid JSON response: {response.text[:200]}...")
                    
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                # Retry on connection errors or timeouts
                retry_count += 1
                if retry_count >= max_retries:
                    error_message = f"Failed after {max_retries} retries. URL: {url}\nError: {str(e)}"
                    raise Exception(error_message)
                
                # Wait before retrying (exponential backoff)
                time.sleep(1 * retry_count)
                continue
                
            except requests.exceptions.RequestException as e:
                error_message = f"Failed URL: {url}\n"
                
                if hasattr(e, 'response') and e.response is not None:
                    error_message += f"Status code: {e.response.status_code}\n"
                    if hasattr(e.response, 'content'):
                        content = e.response.content.decode('utf-8')
                        try:
                            error_data = json.loads(content)
                            error_message += f"Error: {error_data.get('error', content)}"
                        except json.JSONDecodeError:
                            error_message += f"Response: {content}"
                else:
                    error_message += f"Error: {str(e)}"
                    
                raise Exception(error_message)

    def get_projects(self, is_completed=None):
        """
        Get all projects from TestRail.

        Args:
            is_completed (bool, optional): Filter for completed projects

        Returns:
            list: List of projects
        """
        params = {}
        if is_completed is not None:
            params['is_completed'] = 1 if is_completed else 0
        
        return self._send_request('GET', 'get_projects', params=params)

    def get_project(self, project_id):
        """
        Get a specific project by ID.

        Args:
            project_id (int): Project ID

        Returns:
            dict: Project details
        """
        return self._send_request('GET', f'get_project/{project_id}')

    def get_suites(self, project_id):
        """
        Get all test suites for a project.

        Args:
            project_id (int): Project ID

        Returns:
            list: List of suites
        """
        return self._send_request('GET', f'get_suites/{project_id}')

    def get_suite(self, suite_id):
        """
        Get a specific test suite by ID.

        Args:
            suite_id (int): Suite ID

        Returns:
            dict: Suite details
        """
        return self._send_request('GET', f'get_suite/{suite_id}')

    def get_sections(self, project_id, suite_id=None):
        """
        Get all sections for a project and suite.

        Args:
            project_id (int): Project ID
            suite_id (int, optional): Suite ID

        Returns:
            list: List of sections
        """
        params = {}
        if suite_id is not None:
            params['suite_id'] = suite_id
        
        return self._send_request('GET', f'get_sections/{project_id}', params=params)

    def get_cases(self, project_id, suite_id=None, section_id=None):
        """
        Get all test cases for a project, optionally filtered by suite or section.

        Args:
            project_id (int): Project ID
            suite_id (int, optional): Suite ID
            section_id (int, optional): Section ID

        Returns:
            list: List of test cases
        """
        params = {}
        if suite_id is not None:
            params['suite_id'] = suite_id
        if section_id is not None:
            params['section_id'] = section_id
        
        return self._send_request('GET', f'get_cases/{project_id}', params=params)

    def get_case(self, case_id):
        """
        Get a specific test case by ID.

        Args:
            case_id (int): Case ID

        Returns:
            dict: Case details
        """
        return self._send_request('GET', f'get_case/{case_id}')

    def get_priorities(self):
        """
        Get all priorities from TestRail.

        Returns:
            list: List of priorities
        """
        return self._send_request('GET', 'get_priorities')

    def get_case_types(self):
        """
        Get all case types from TestRail.

        Returns:
            list: List of case types
        """
        return self._send_request('GET', 'get_case_types')
    
    def get_templates(self, project_id):
        """
        Get all templates for a project.

        Args:
            project_id (int): Project ID

        Returns:
            list: List of templates
        """
        return self._send_request('GET', f'get_templates/{project_id}')
    
    def get_milestones(self, project_id):
        """
        Get all milestones for a project.

        Args:
            project_id (int): Project ID

        Returns:
            dict: Response containing milestones array
        """
        return self._send_request('GET', f'get_milestones/{project_id}')