import requests
import json
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
        self.url = url.rstrip('/')
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
        url = urljoin(f"{self.url}/index.php?/api/v2/", endpoint)
        
        try:
            response = requests.request(
                method=method,
                url=url,
                auth=self.auth,
                headers=self.headers,
                json=data,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            if hasattr(e.response, 'content'):
                error_message = e.response.content.decode('utf-8')
                try:
                    error_data = json.loads(error_message)
                    error_message = error_data.get('error', error_message)
                except json.JSONDecodeError:
                    pass
                raise Exception(f"TestRail API error: {error_message}")
            else:
                raise Exception(f"TestRail API request failed: {str(e)}")

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