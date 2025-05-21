class Project:
    """Represents a TestRail project."""

    def __init__(self, project_data):
        """
        Initialize a Project instance from API data.
        
        Args:
            project_data (dict): Project data from TestRail API
        """
        self.id = project_data.get('id')
        self.name = project_data.get('name')
        self.announcement = project_data.get('announcement')
        self.is_completed = project_data.get('is_completed')
        self.suite_mode = project_data.get('suite_mode')
        self.suites = []

    def __str__(self):
        return self.name

    def add_suite(self, suite):
        """
        Add a suite to this project.
        
        Args:
            suite: Suite instance
        """
        self.suites.append(suite)