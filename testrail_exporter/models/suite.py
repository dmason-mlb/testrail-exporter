class Suite:
    """Represents a TestRail test suite."""

    def __init__(self, suite_data):
        """
        Initialize a Suite instance from API data.
        
        Args:
            suite_data (dict): Suite data from TestRail API
        """
        self.id = suite_data.get('id')
        self.name = suite_data.get('name')
        self.description = suite_data.get('description')
        self.project_id = suite_data.get('project_id')
        self.is_master = suite_data.get('is_master')
        self.is_baseline = suite_data.get('is_baseline')
        self.is_completed = suite_data.get('is_completed')
        self.sections = []
        self.checked = False
        
    def __str__(self):
        return self.name
        
    def add_section(self, section):
        """
        Add a section to this suite.
        
        Args:
            section: Section instance
        """
        self.sections.append(section)
        
    def has_sections(self):
        """
        Check if this suite has any sections.
        
        Returns:
            bool: True if the suite has sections, False otherwise
        """
        return len(self.sections) > 0