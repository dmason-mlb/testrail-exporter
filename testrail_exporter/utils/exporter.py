import json
import csv
import os


class Exporter:
    """Class for exporting TestRail data to various formats."""

    @staticmethod
    def export_to_json(data, filepath):
        """
        Export data to a JSON file.
        
        Args:
            data (dict): Data to export
            filepath (str): Path to save the file
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting to JSON: {str(e)}")
            return False
    
    @staticmethod
    def export_to_csv(data, filepath):
        """
        Export test cases to a CSV file.
        
        Args:
            data (dict): Data to export (must have a 'cases' key)
            filepath (str): Path to save the file
            
        Returns:
            bool: True if export was successful, False otherwise
        """
        try:
            if 'cases' not in data:
                raise ValueError("Data must contain a 'cases' key")
                
            cases = data['cases']
            if not cases:
                raise ValueError("No cases to export")
                
            # Determine all possible fields from the first case
            first_case = cases[0]
            fields = list(first_case.keys())
            
            # Add any additional fields from other cases
            for case in cases[1:]:
                for field in case.keys():
                    if field not in fields:
                        fields.append(field)
            
            # Write to CSV
            with open(filepath, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()
                writer.writerows(cases)
                
            return True
        except Exception as e:
            print(f"Error exporting to CSV: {str(e)}")
            return False