import re
import xml.etree.ElementTree as ET
import pandas as pd
from .logger import ExportLogger


class XrayConversionError(Exception):
    """Custom exception for Xray conversion errors."""
    pass


column = ["Suite Name","Section Name","Issue ID","Test Type","Test Title", "Test Priority", "Preconditions","Action","Data","Result","Test Repo", "Labels"]
row = []

CLEANR = re.compile(r'<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
EMPTYSPACES = re.compile(r'\n|\r')
QUOTES = re.compile(r'\&quot\;')

def cleanTags(txt):
    if txt:
        cleanTxt = re.sub(QUOTES, '"', txt)
        cleanTxt = re.sub(CLEANR, '', cleanTxt)
    else:
        cleanTxt = ''

    return cleanTxt

def getPriorityValue(priorityName):
    priority = 4

    if priorityName == 'Critical':
        priority = 1
    elif priorityName == 'High':
        priority = 2
    elif priorityName == 'Medium':
        priority = 3
    elif priorityName == 'Low':
        priority = 4
    else:
        priority = 3
    return priority

def getTestType(type):
    return 'Manual'

ENDPOINT = re.compile(r'(\!\[\]\(index.php)(.*?)(\))')
def handleSteps(text, outputtestrailEndpoint):
    result = ''
    startTag = '![](index.php'
    text = cleanTags(text)
    if startTag in text:
        result=re.sub(ENDPOINT, r'[Link|'+outputtestrailEndpoint+'index.php'+r'\2]',text)
    else:
        result = text
    return result

def appendRows(suiteName='', sectionName='', issueID='', issueKey='', testType=None, testSummary=None, testPriority=None, preconditions=None, action=None, data=None, result=None, testRepo=None, labels=None, outputtestrailEndpoint=None):
    row.append({"Suite Name": suiteName if suiteName else '',
                "Section Name": sectionName if sectionName else '',
                "Issue ID": issueID,
                "Test Type": getTestType(testType),
                "Test Title": cleanTags(testSummary.text) if testSummary is not None else '',
                "Test Priority": getPriorityValue(testPriority.text) if testPriority is not None else '3',
                "Preconditions": handleSteps(preconditions.text, outputtestrailEndpoint) if preconditions is not None else '',
                "Action": handleSteps(action.text, outputtestrailEndpoint) if action is not None else '',
                "Data": handleSteps(data.text, outputtestrailEndpoint) if data is not None else '',
                "Result": handleSteps(result.text, outputtestrailEndpoint) if result is not None else '',
                "Test Repo": testRepo if testRepo else '',
                "Labels": testType if testType else ''})

def handleTestSections(root, issueID, outputfile, repoName, outputtestrailEndpoint, logger=None, suiteName=None, sectionPath=None):
    if root.tag == 'suite':
        testsections = root.findall('sections/section')
        # Get suite name if not already provided
        if suiteName is None:
            suite_name_elem = root.find('name')
            if suite_name_elem is not None and suite_name_elem.text:
                suiteName = suite_name_elem.text
    else:
        testsections = root.findall('section')

    baseRepoName = repoName
    baseSectionPath = sectionPath
    for testsection in testsections:
        sectionName = testsection.find('name').text
        testRepoDescription = testsection.find('description')

        # Build the section path (without suite name)
        if baseSectionPath is not None and sectionName is not None:
            currentSectionPath = baseSectionPath + '/' + sectionName
        else:
            currentSectionPath = sectionName

        # Build the test repo path (with suite name)
        if baseRepoName is not None and sectionName is not None:
            # Check if baseRepoName already starts with suiteName to avoid duplication
            if suiteName and not baseRepoName.startswith(suiteName + '/'):
                testRepoName = baseRepoName + '/' + sectionName
            else:
                testRepoName = baseRepoName + '/' + sectionName
        elif suiteName is not None and sectionName is not None:
            # This is a top-level section, prepend suite name
            testRepoName = suiteName + '/' + sectionName
        else:
            testRepoName = sectionName

        cases = testsection.findall('cases/case')
        if logger:
            logger.debug(f"Processing section '{testRepoName}' with {len(cases)} test cases")
            
        for testcase in cases:
            preconditionID = ''
            id = testcase.find('id')
            title = testcase.find('title')
            template = testcase.find('template')
            type_element = testcase.find('type')
            priority = testcase.find('priority')
            estimate = testcase.find('estimate')

            # Extract the test case type from the type element
            actual_test_type = ''
            if type_element is not None and type_element.text:
                actual_test_type = type_element.text.strip()
                if logger:
                    logger.debug(f"Found test case type: '{actual_test_type}'")
            
            custom = testcase.find('custom')
            preconds = None  # Initialize preconditions
            
            if custom is not None:
                
                # Extract preconditions
                preconds = custom.find('preconds')
                                   
                steps = custom.find('steps')
                steps_separated = custom.find('steps_separated')

                if steps is not None:
                    # Text field with steps
                    expected = custom.find('expected')
                    appendRows(suiteName=suiteName,sectionName=currentSectionPath,issueID=issueID,testType=actual_test_type,testSummary=title,testPriority=priority,preconditions=preconds,action=steps,result=expected, testRepo=testRepoName, outputtestrailEndpoint=outputtestrailEndpoint)
                    issueID = issueID+1  
                elif steps_separated is not None:
                    # Steps in different cells
                    first_step = True
                    hasSteps = False
                    for step in steps_separated:
                        index = step.find('index')
                        content = step.find('content')
                        expected = step.find('expected')
                        additional_info = step.find('additional_info')
                        hasSteps = True
                        if first_step:
                            appendRows(suiteName=suiteName,sectionName=currentSectionPath,issueID=issueID,testType=actual_test_type,testSummary=title,testPriority=priority,preconditions=preconds,action=content,result=expected,testRepo=testRepoName, data=additional_info, outputtestrailEndpoint=outputtestrailEndpoint)
                            first_step = False
                        else:
                            appendRows(suiteName=suiteName,sectionName=currentSectionPath,issueID=issueID,testType=actual_test_type, action=content,result=expected, data=additional_info, outputtestrailEndpoint=outputtestrailEndpoint)
                    if not hasSteps:
                        appendRows(suiteName=suiteName,sectionName=currentSectionPath,issueID=issueID,testType=actual_test_type,testSummary=title,testPriority=priority,preconditions=preconds, testRepo=testRepoName, data=additional_info, outputtestrailEndpoint=outputtestrailEndpoint)
                    issueID = issueID+1  
                else:
                    # No steps - just add the test case info
                    appendRows(suiteName=suiteName,sectionName=currentSectionPath,issueID=issueID,testType=actual_test_type,testSummary=title,testPriority=priority,preconditions=preconds,action=None,result=None, testRepo=testRepoName, outputtestrailEndpoint=outputtestrailEndpoint)
                    issueID = issueID+1
            else:
                #ignore all other types
                continue
        
        innerSection = testsection.find('sections')
        if innerSection is not None:
            issueID = handleTestSections(root=innerSection, issueID=issueID, outputfile=outputfile, repoName=testRepoName, outputtestrailEndpoint=outputtestrailEndpoint, logger=logger, suiteName=suiteName, sectionPath=currentSectionPath)

    return issueID


def parseTestrail2XrayDataWithColumns(inputfile, outputfile, outputtestrailEndpoint='', logger=None, selected_columns=None):
    """
    Parse TestRail XML export and convert to Xray CSV format with selected columns only.
    
    Args:
        inputfile: Path to input XML file
        outputfile: Path to output CSV file  
        outputtestrailEndpoint: Optional TestRail endpoint URL
        logger: Optional ExportLogger instance
        selected_columns: Optional list of column names to include
        
    Raises:
        XrayConversionError: If conversion fails
    """
    # Clear any existing row data
    global row
    row = []
    
    # If no columns selected, use all columns
    if not selected_columns:
        selected_columns = column
    
    try:
        if logger:
            logger.info(f"Parsing XML file: {inputfile}")
            logger.info(f"Selected columns: {selected_columns}")
            
        # Parsing XML file
        xmlParse = ET.parse(inputfile)
        root = xmlParse.getroot()
        issueID = 1

        if root.tag == 'suites':
            # Multiple suites export - process each suite
            if logger:
                logger.info(f"Processing multiple suites export ({len(root.findall('suite'))} suites)")
            for suite in root.findall('suite'):
                # Get suite name for multiple suites export
                suite_name_elem = suite.find('name')
                suite_name = suite_name_elem.text if suite_name_elem is not None and suite_name_elem.text else None
                issueID = handleTestSections(root=suite, issueID=issueID, outputfile=outputfile, repoName=None, outputtestrailEndpoint=outputtestrailEndpoint, logger=logger, suiteName=suite_name, sectionPath=None)
        else:
            # Single suite export - process directly
            if logger:
                logger.info("Processing single suite export")
            # For single suite, the suite name will be extracted in handleTestSections
            issueID = handleTestSections(root=root, issueID=issueID, outputfile=outputfile, repoName=None, outputtestrailEndpoint=outputtestrailEndpoint, logger=logger, suiteName=None, sectionPath=None)
        
        # Final CSV write after processing all suites
        if row:
            if logger:
                logger.info(f"Writing {len(row)} test cases to CSV: {outputfile}")
            
            # Create DataFrame with all columns first
            df = pd.DataFrame(row, columns=column)
            
            # Filter to only selected columns
            df_filtered = df[selected_columns]
            
            # Set index if Issue ID is in selected columns
            if "Issue ID" in selected_columns:
                df_filtered.set_index("Issue ID", inplace=True)
                
            df_filtered.to_csv(outputfile)
            if logger:
                logger.info("CSV file created successfully with selected columns")
        else:
            raise XrayConversionError("No test cases found in XML file")
            
    except ET.ParseError as e:
        error_msg = f"Failed to parse XML file: {str(e)}"
        if logger:
            logger.error(error_msg, exc_info=True)
        raise XrayConversionError(error_msg) from e
    except PermissionError as e:
        error_msg = f"Permission denied: Cannot write to {outputfile}"
        if logger:
            logger.error(error_msg, exc_info=True)
        raise XrayConversionError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error during Xray conversion: {str(e)}"
        if logger:
            logger.error(error_msg, exc_info=True)
        raise XrayConversionError(error_msg) from e

def parseTestrail2XrayData(inputfile, outputfile, outputtestrailEndpoint='', logger=None):
    """
    Parse TestRail XML export and convert to Xray CSV format.
    Handles both single suite exports and multiple suite exports wrapped in <suites> tag.
    
    Args:
        inputfile: Path to input XML file
        outputfile: Path to output CSV file  
        outputtestrailEndpoint: Optional TestRail endpoint URL
        logger: Optional ExportLogger instance
        
    Raises:
        XrayConversionError: If conversion fails
    """
    # Clear any existing row data
    global row
    row = []
    
    try:
        if logger:
            logger.info(f"Parsing XML file: {inputfile}")
            
        # Parsing XML file
        xmlParse = ET.parse(inputfile)
        root = xmlParse.getroot()
        issueID = 1

        if root.tag == 'suites':
            # Multiple suites export - process each suite
            if logger:
                logger.info(f"Processing multiple suites export ({len(root.findall('suite'))} suites)")
            for suite in root.findall('suite'):
                # Get suite name for multiple suites export
                suite_name_elem = suite.find('name')
                suite_name = suite_name_elem.text if suite_name_elem is not None and suite_name_elem.text else None
                issueID = handleTestSections(root=suite, issueID=issueID, outputfile=outputfile, repoName=None, outputtestrailEndpoint=outputtestrailEndpoint, logger=logger, suiteName=suite_name, sectionPath=None)
        else:
            # Single suite export - process directly
            if logger:
                logger.info("Processing single suite export")
            # For single suite, the suite name will be extracted in handleTestSections
            issueID = handleTestSections(root=root, issueID=issueID, outputfile=outputfile, repoName=None, outputtestrailEndpoint=outputtestrailEndpoint, logger=logger, suiteName=None, sectionPath=None)
        
        # Final CSV write after processing all suites
        if row:
            if logger:
                logger.info(f"Writing {len(row)} test cases to CSV: {outputfile}")
            df = pd.DataFrame(row, columns=column)  
            df.set_index("Issue ID", inplace=True)
            df.to_csv(outputfile)
            if logger:
                logger.info("CSV file created successfully")
        else:
            raise XrayConversionError("No test cases found in XML file")
            
    except ET.ParseError as e:
        error_msg = f"Failed to parse XML file: {str(e)}"
        if logger:
            logger.error(error_msg, exc_info=True)
        raise XrayConversionError(error_msg) from e
    except PermissionError as e:
        error_msg = f"Permission denied: Cannot write to {outputfile}"
        if logger:
            logger.error(error_msg, exc_info=True)
        raise XrayConversionError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error during Xray conversion: {str(e)}"
        if logger:
            logger.error(error_msg, exc_info=True)
        raise XrayConversionError(error_msg) from e

def convert_xml_to_xray_csv(xml_filepath, csv_filepath, testrail_endpoint='', logger=None):
    """
    Convert a TestRail XML export to Xray-compatible CSV format.
    
    Args:
        xml_filepath (str): Path to the XML file to convert
        csv_filepath (str): Path where the CSV file should be saved
        testrail_endpoint (str): Optional TestRail endpoint URL for link handling
        logger (ExportLogger): Optional logger instance
        
    Returns:
        bool: True if conversion was successful, False otherwise
    """
    try:
        parseTestrail2XrayData(xml_filepath, csv_filepath, testrail_endpoint, logger)
        return True
    except XrayConversionError:
        # Re-raise XrayConversionError as it already has a good error message
        raise
    except Exception as e:
        # Wrap any other unexpected errors
        error_msg = f"Error converting XML to Xray CSV: {str(e)}"
        if logger:
            logger.error(error_msg, exc_info=True)
        raise XrayConversionError(error_msg) from e

def convert_xml_to_xray_csv_with_columns(xml_filepath, csv_filepath, testrail_endpoint='', logger=None, selected_columns=None):
    """
    Convert a TestRail XML export to Xray-compatible CSV format with selected columns only.
    
    Args:
        xml_filepath (str): Path to the XML file to convert
        csv_filepath (str): Path where the CSV file should be saved
        testrail_endpoint (str): Optional TestRail endpoint URL for link handling
        logger (ExportLogger): Optional logger instance
        selected_columns (list): List of column names to include in the output
        
    Returns:
        bool: True if conversion was successful, False otherwise
    """
    try:
        parseTestrail2XrayDataWithColumns(xml_filepath, csv_filepath, testrail_endpoint, logger, selected_columns)
        return True
    except XrayConversionError:
        # Re-raise XrayConversionError as it already has a good error message
        raise
    except Exception as e:
        # Wrap any other unexpected errors
        error_msg = f"Error converting XML to Xray CSV: {str(e)}"
        if logger:
            logger.error(error_msg, exc_info=True)
        raise XrayConversionError(error_msg) from e