import json
import csv
import os
import xml.etree.ElementTree as ET
import xml.dom.minidom as minidom


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
    
    @staticmethod
    def export_to_xml(data, filepath):
        """
        Export test cases to a TestRail-compatible XML file.
        
        Args:
            data (dict): Data to export (must have a 'cases' key and project info)
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
            
            # Build complete suite hierarchy first, then populate with cases
            suites_dict = {}
            
            # Step 1: Build complete section hierarchy from suite data
            suites_data = data.get('suites', [])
            for suite in suites_data:
                suite_key = f"{suite.name}_{suite.id}" if suite.id else suite.name
                
                # Initialize suite structure
                suites_dict[suite_key] = {
                    'name': suite.name,
                    'id': suite.id,
                    'description': suite.description,
                    'sections': {}
                }
                
                # Add all sections from the suite (including those without test cases)
                if hasattr(suite, 'sections') and suite.sections:
                    for section in suite.sections:
                        suites_dict[suite_key]['sections'][section.id] = {
                            'id': section.id,
                            'name': section.name,
                            'parent_id': section.parent_id,
                            'depth': section.depth,
                            'cases': [],
                            'children': {}
                        }
            
            # Step 2: Populate test cases into the appropriate sections
            for case in cases:
                suite_name = case.get('suite_name', 'Unknown Suite')
                suite_id = case.get('suite_id')
                section_id = case.get('section_id')
                
                # Use a key that includes the suite ID if available
                suite_key = f"{suite_name}_{suite_id}" if suite_id else suite_name
                
                # Create suite entry if it doesn't exist (fallback for missing suite data)
                if suite_key not in suites_dict:
                    suites_dict[suite_key] = {
                        'name': suite_name,
                        'id': suite_id,
                        'description': '',  # No description available in fallback case
                        'sections': {}
                    }
                
                # Use a default section ID if none exists
                if section_id is None:
                    section_id = 'default'
                
                # Create section entry if it doesn't exist (fallback for missing section data)
                if section_id not in suites_dict[suite_key]['sections']:
                    section_name = case.get('section_name', 'Test Cases')
                    section_parent_id = case.get('section_parent_id')
                    section_depth = case.get('section_depth', 0)
                    
                    suites_dict[suite_key]['sections'][section_id] = {
                        'id': section_id,
                        'name': section_name,
                        'parent_id': section_parent_id,
                        'depth': section_depth,
                        'cases': [],
                        'children': {}
                    }
                
                # Add the test case to the section
                suites_dict[suite_key]['sections'][section_id]['cases'].append(case)
            
            # Build hierarchical section structure for each suite
            for suite_key, suite_info in suites_dict.items():
                sections = suite_info['sections']
                
                # Build parent-child relationships
                for section_id, section in sections.items():
                    parent_id = section['parent_id']
                    if parent_id and parent_id in sections:
                        sections[parent_id]['children'][section_id] = section
                
                # Store root sections (sections with no parent or parent not in the export)
                suite_info['root_sections'] = {
                    sid: section for sid, section in sections.items() 
                    if not section['parent_id'] or section['parent_id'] not in sections
                }
            
            # Create XML structure - handle multiple suites
            if len(suites_dict) == 1:
                # Single suite - use the original structure
                suite_key = list(suites_dict.keys())[0]
                suite_info = suites_dict[suite_key]
                root = ET.Element("suite")
                Exporter._add_suite_xml(root, suite_info, True)
            else:
                # Multiple suites - wrap in a container
                root = ET.Element("suites")
                for suite_key, suite_info in suites_dict.items():
                    suite_elem = ET.SubElement(root, "suite")
                    Exporter._add_suite_xml(suite_elem, suite_info, True)  # Always include suite metadata
            
            # Convert to pretty XML string using manual indentation
            def indent_xml(elem, level=0):
                i = "\n" + level * "\t"
                if len(elem):
                    if not elem.text or not elem.text.strip():
                        elem.text = i + "\t"
                    if not elem.tail or not elem.tail.strip():
                        elem.tail = i
                    for child in elem:
                        indent_xml(child, level+1)
                    if not child.tail or not child.tail.strip():
                        child.tail = i
                else:
                    if level and (not elem.tail or not elem.tail.strip()):
                        elem.tail = i
            
            indent_xml(root)
            pretty_xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding='unicode')
            
            # Fix ElementTree's weird behavior with 'name' tags getting truncated to 'n'
            pretty_xml = pretty_xml.replace("<n>", "<name>").replace("</n>", "</name>")
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(pretty_xml)
                
            return True
        except Exception as e:
            print(f"Error exporting to XML: {str(e)}")
            return False
    
    @staticmethod
    def _add_suite_xml(suite_elem, suite_info, add_metadata=True):
        """
        Add suite information to XML element with nested sections support.
        
        Args:
            suite_elem: XML element to add to
            suite_info: Dictionary with suite name, id, and root_sections
            add_metadata: Whether to add ID/name/description elements
        """
        if add_metadata:
            # Add suite metadata
            id_elem = ET.SubElement(suite_elem, "id")
            if suite_info['id']:
                id_elem.text = f"S{suite_info['id']}"
            else:
                id_elem.text = f"S{hash(suite_info['name']) % 1000000}"  # Fallback to hash
            
            name_elem = ET.SubElement(suite_elem, "name")
            name_elem.text = suite_info['name']
            
            desc_elem = ET.SubElement(suite_elem, "description")
            if suite_info.get('description'):
                desc_elem.text = suite_info['description']
        
        # Add root sections
        sections_elem = ET.SubElement(suite_elem, "sections")
        
        # Use root_sections from the hierarchical structure
        root_sections = suite_info.get('root_sections', {})
        for section_id, section in root_sections.items():
            Exporter._add_section_xml(sections_elem, section)
    
    @staticmethod
    def _add_section_xml(parent_elem, section):
        """
        Recursively add section and its nested children to XML.
        
        Args:
            parent_elem: Parent XML element to add section to
            section: Section dictionary with name, cases, and children
        """
        section_elem = ET.SubElement(parent_elem, "section")
        
        # Section name
        section_name_elem = ET.SubElement(section_elem, "name")
        section_name_elem.text = section['name']
        
        # Section description
        section_desc_elem = ET.SubElement(section_elem, "description")
        
        # Add nested sections if any
        if section['children']:
            nested_sections_elem = ET.SubElement(section_elem, "sections")
            for child_id, child_section in section['children'].items():
                Exporter._add_section_xml(nested_sections_elem, child_section)
        
        # Add cases if any
        if section['cases']:
            cases_elem = ET.SubElement(section_elem, "cases")
            
            for case in section['cases']:
                case_elem = ET.SubElement(cases_elem, "case")
                
                # Case ID
                id_elem = ET.SubElement(case_elem, "id")
                id_elem.text = f"C{case.get('id', '')}"
                
                # Case title
                title_elem = ET.SubElement(case_elem, "title")
                title_elem.text = case.get('title', '')
                
                # Template
                template_elem = ET.SubElement(case_elem, "template")
                template_name = case.get('template_name', 'Test Case')  # Default to "Test Case" if no template
                template_elem.text = template_name
                
                # Type
                type_elem = ET.SubElement(case_elem, "type")
                type_name = case.get('type_name', 'Functional')
                type_elem.text = type_name
                
                # Priority
                priority_elem = ET.SubElement(case_elem, "priority")
                priority_name = case.get('priority_name', 'Medium')
                priority_elem.text = priority_name
                
                # Estimate
                estimate_elem = ET.SubElement(case_elem, "estimate")
                estimate_value = case.get('estimate')
                if estimate_value:
                    estimate_elem.text = str(estimate_value)
                
                # Milestone
                milestone_elem = ET.SubElement(case_elem, "milestone")
                milestone_name = case.get('milestone_name')
                if milestone_name:
                    milestone_elem.text = milestone_name
                
                # References
                refs_elem = ET.SubElement(case_elem, "references")
                refs_value = case.get('refs')
                if refs_value:
                    refs_elem.text = str(refs_value)
                
                # Custom fields
                custom_elem = ET.SubElement(case_elem, "custom")
                
                # Add custom fields - only create elements when there's content
                for key, value in case.items():
                    if key.startswith('custom_'):
                        field_name = key.replace('custom_', '')
                        
                        # Handle specific custom fields based on TestRail naming
                        if field_name == 'preconds' and value:
                            preconds_elem = ET.SubElement(custom_elem, "preconds")
                            preconds_elem.text = str(value)
                        elif field_name == 'steps' and value:
                            steps_elem = ET.SubElement(custom_elem, "steps")
                            steps_elem.text = str(value)
                        elif field_name == 'expected' and value:
                            expected_elem = ET.SubElement(custom_elem, "expected")
                            expected_elem.text = str(value)
                        elif field_name == 'steps_separated' and value and isinstance(value, list) and len(value) > 0:
                            # Only create steps_separated if there are actual steps
                            steps_sep_elem = ET.SubElement(custom_elem, "steps_separated")
                            for i, step_data in enumerate(value, 1):
                                step_elem = ET.SubElement(steps_sep_elem, "step")
                                
                                index_elem = ET.SubElement(step_elem, "index")
                                index_elem.text = str(i)
                                
                                content_elem = ET.SubElement(step_elem, "content")
                                content_elem.text = str(step_data.get('content', '')) if isinstance(step_data, dict) else str(step_data)
                                
                                expected_elem = ET.SubElement(step_elem, "expected")
                                expected_elem.text = str(step_data.get('expected', '')) if isinstance(step_data, dict) else ""