import re
import xml.etree.ElementTree as ET
import pandas as pd
from .logger import ExportLogger


class XrayConversionError(Exception):
    """Custom exception for Xray conversion errors."""
    pass


column = ["Issue ID","Issue Key","Test Type","Test Summary", "Test Priority", "Action","Data","Result","Test Repo", "Labels"]
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
    testType = 'Manual'
    validTypes = ['Manual', 'Exploratory', 'Automated']
    if type is not None and type in validTypes:
        if type == 'Automated':
            testType = 'Generic'
        else:
            testType = type

    return testType

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

def appendRows(issueID='', issueKey='', testType=None, testSummary=None, testPriority=None, action=None, data=None, result=None, testRepo=None, labels=None, outputtestrailEndpoint=None):
    row.append({"Issue ID": issueID,
                "Issue Key": '',
                "Test Type": getTestType(testType),
                "Test Summary": cleanTags(testSummary.text) if testSummary is not None else '',
                "Test Priority": getPriorityValue(testPriority.text) if testPriority is not None else '3',
                "Action": handleSteps(action.text, outputtestrailEndpoint) if action is not None else '',
                "Data": handleSteps(data.text, outputtestrailEndpoint) if data is not None else '',
                "Result": handleSteps(result.text, outputtestrailEndpoint) if result is not None else '',
                "Test Repo": testRepo if testRepo else '',
                "Labels": labels.text if labels is not None else ''})

def handleTestSections(root, issueID, outputfile, repoName, outputtestrailEndpoint, logger=None, suiteName=None):
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
    for testsection in testsections:
        testRepoName = testsection.find('name').text
        testRepoDescription = testsection.find('description')

        # Build the test repo path
        if baseRepoName is not None and testRepoName is not None:
            # Check if baseRepoName already starts with suiteName to avoid duplication
            if suiteName and not baseRepoName.startswith(suiteName + '/'):
                testRepoName = baseRepoName + '/' + testRepoName
            else:
                testRepoName = baseRepoName + '/' + testRepoName
        elif suiteName is not None and testRepoName is not None:
            # This is a top-level section, prepend suite name
            testRepoName = suiteName + '/' + testRepoName
        # else: testRepoName stays as is

        cases = testsection.findall('cases/case')
        if logger:
            logger.debug(f"Processing section '{testRepoName}' with {len(cases)} test cases")
            
        for testcase in cases:
            preconditionID = ''
            id = testcase.find('id')
            title = testcase.find('title')
            template = testcase.find('template')
            labels = testcase.find('type')
            priority = testcase.find('priority')
            estimate = testcase.find('estimate')

            custom = testcase.find('custom')
            if custom is not None:
                automation_type = custom.find('automation_type')
                type = automation_type.find('value').text.strip() if automation_type is not None else 'Manual'
                                   
                steps = custom.find('steps')
                steps_separated = custom.find('steps_separated')

                if steps is not None:
                    # Text field with steps
                    expected = custom.find('expected')
                    appendRows(issueID=issueID,testType=type,testSummary=title,testPriority=priority,action=steps,result=expected, testRepo=testRepoName, labels=labels, outputtestrailEndpoint=outputtestrailEndpoint)
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
                            appendRows(issueID=issueID,testType=type,testSummary=title,testPriority=priority,action=content,result=expected,testRepo=testRepoName, data=additional_info, labels=labels, outputtestrailEndpoint=outputtestrailEndpoint)
                            first_step = False
                        else:
                            appendRows(issueID=issueID,testType=type, action=content,result=expected, data=additional_info, outputtestrailEndpoint=outputtestrailEndpoint)
                    if not hasSteps:
                        appendRows(issueID=issueID,testType=type,testSummary=title,testPriority=priority, testRepo=testRepoName, data=additional_info, outputtestrailEndpoint=outputtestrailEndpoint)
                    issueID = issueID+1  
                elif type == 'Manual' or type == 'None':
                    appendRows(issueID=issueID,testType=type,testSummary=title,testPriority=priority,action=None,result=None, testRepo=testRepoName, labels=labels, outputtestrailEndpoint=outputtestrailEndpoint)
                    issueID = issueID+1
            else:
                #ignore all other types
                continue
        
        innerSection = testsection.find('sections')
        if innerSection is not None:
            issueID = handleTestSections(root=innerSection, issueID=issueID, outputfile=outputfile, repoName=testRepoName, outputtestrailEndpoint=outputtestrailEndpoint, logger=logger, suiteName=suiteName)

    return issueID


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
                issueID = handleTestSections(root=suite, issueID=issueID, outputfile=outputfile, repoName=None, outputtestrailEndpoint=outputtestrailEndpoint, logger=logger, suiteName=suite_name)
        else:
            # Single suite export - process directly
            if logger:
                logger.info("Processing single suite export")
            # For single suite, the suite name will be extracted in handleTestSections
            issueID = handleTestSections(root=root, issueID=issueID, outputfile=outputfile, repoName=None, outputtestrailEndpoint=outputtestrailEndpoint, logger=logger, suiteName=None)
        
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