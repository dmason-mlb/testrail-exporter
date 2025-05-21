class Section:
    """Represents a TestRail section."""

    def __init__(self, section_data):
        """
        Initialize a Section instance from API data.
        
        Args:
            section_data (dict): Section data from TestRail API
        """
        self.id = section_data.get('id')
        self.name = section_data.get('name')
        self.description = section_data.get('description')
        self.suite_id = section_data.get('suite_id')
        self.parent_id = section_data.get('parent_id')
        self.depth = section_data.get('depth', 0)
        self.cases = []
        self.checked = False
        
    def __str__(self):
        return self.name
        
    def add_case(self, case):
        """
        Add a test case to this section.
        
        Args:
            case: Case instance
        """
        self.cases.append(case)