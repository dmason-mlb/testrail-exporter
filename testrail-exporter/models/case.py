class Case:
    """Represents a TestRail test case."""

    def __init__(self, case_data):
        """
        Initialize a Case instance from API data.
        
        Args:
            case_data (dict): Case data from TestRail API
        """
        self.id = case_data.get('id')
        self.title = case_data.get('title')
        self.section_id = case_data.get('section_id')
        self.suite_id = case_data.get('suite_id')
        self.priority_id = case_data.get('priority_id')
        self.template_id = case_data.get('template_id')
        self.type_id = case_data.get('type_id')
        self.milestone_id = case_data.get('milestone_id')
        self.refs = case_data.get('refs')
        
        # Extract custom fields
        self.custom_fields = {}
        for key, value in case_data.items():
            if key.startswith('custom_'):
                self.custom_fields[key] = value
                
    def __str__(self):
        return self.title
        
    def to_dict(self):
        """
        Convert the case to a dictionary for export.
        
        Returns:
            dict: Case as a dictionary
        """
        case_dict = {
            'id': self.id,
            'title': self.title,
            'section_id': self.section_id,
            'suite_id': self.suite_id,
            'priority_id': self.priority_id,
            'template_id': self.template_id,
            'type_id': self.type_id,
            'milestone_id': self.milestone_id,
            'refs': self.refs
        }
        
        # Add custom fields
        case_dict.update(self.custom_fields)
        
        return case_dict