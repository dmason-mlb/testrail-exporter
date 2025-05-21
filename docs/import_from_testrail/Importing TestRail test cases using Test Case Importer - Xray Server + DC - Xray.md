Please note

The following examples are provided as-is, no warranties attached; use them carefully. Please feel free to adapt them to your needs. 

We don't provide support for these examples/scripts or making customisations on top of them. 

<u>For problems in the code samples, please raise a issue on the underlying GitHub repository (see info ahead); don't use Xray support for it.</u>

If you notice a typo/mistake on this tutorial or have a suggestion related with the tutorial itself, feel free to reach out [Xray support](https://jira.getxray.app/servicedesk/customer/portal/2 "https://jira.getxray.app/servicedesk/customer/portal/2") and share it with us.

What you'll learn

-   How to export test cases from TestRail
-   Use a script to convert the exported XML test cases to an Xray compatible CSV file
-   Import different test cases (with different fields and options)
-   Validate that the test cases were imported to Xray

Source-code for this tutorial

-   All examples are available in [GitHub](https://github.com/Xray-App/xray-code-snippets/tree/main/use_cases/import_from_qase/server)

This tutorial explains how to export test cases from TestRail and import them into Xray.

TestRail is a test management tool that runs independently with versions available for on-premises and in the cloud. In this tutorial, you will learn how to export the test cases from TestRail in an XML format, how to use a script (available in [GitHub](https://github.com/Xray-App/xray-code-snippets/tree/main/use_cases/import_from_qase/server)) to convert the XML file into a compatible CSV so that it can be imported into Xray using the [Test Case Importer](https://docs.getxray.app/display/XRAY/Importing+TestRail+test+cases+using+Test+Case+Importer).

In this tutorial, we will provide different examples of exporting and importing test cases from TestRail into Xray. 

## Features and Limitations

Below you can find a list of the support features and current limitations.

Migration from TestRail is limited the information we are able to export from the TestRail and how it can be mapped to Xray entities.

Most of the test case information will be migrated seamlessly, but please check the following table for more detail.

|  |  |
| --- | --- |
| 
-   Test and Test steps
-   Test Sections/SubSections

 | 

-   Test case attachments
-   Preconditions
-   Test Runs
-   Test Plans
-   Defects and Requirements

 |

## How it works

TestRail allows users to create different test projects. The user can specify and organize those tests into test sections. Each test project can have multiple test sections and subsections.

TestRail has a set of templates that we choose upon test case creation that will determine what information is present in the test. The default templates include the "Test Case (Text)" template that allows you to describe the test case in a text format; we also have a "Test Case (Steps)" that allows you to describe a test case in different steps with action, additional data and expected result. TestRail also has a Behaviour Driven Development template that enables the user to describe the test into different scenarios or an Exploratory test type that defines a mission and goals for the test.

In TestRail, to execute tests you need to associate them to a test run.

We have summarised a possible mapping between TestRail and Xray entities that we'll use in this tutorial.

|  |  |  |
| --- | --- | --- |
| Test Case | Test | 
TestRail does not support data sets or Gherkin definition, only manual/automated test steps.

In TestRail when you choose to export using XML format it will export everything. All steps are exported unless they are empty.

 |
| Test Section | Test Repository | 

The test sections and sub-sections of TestRail are mapped into Xray Test Repository.  



 |

Notice that for the Server version of Xray we only creating the Tests corresponding to the manual test cases in TestRail. Preconditions, if needed, must be created separately. 

___

## Prerequisites

___

In each example, we will show how we obtained the XML file from TestRail, how to use the scripts to convert the XML files into compatible CSV files, and finally, how to import the CSV files into Xray. All files are available in [GitHub](https://github.com/Xray-App/xray-code-snippets/tree/main/use_cases/import_from_qase/server).

We will showcase different possibilities when exporting test cases from TestRail, using a combination of fields and possibilities that should cover most usages.

All of the examples in this tutorial have a XML file exported from TestRail, a CSV file with the definition of the test cases to import, and a configuration file that will configure all associations and fields for the importation to be successful in Xray.

## Export to XML from TestRail and Import into Xray

In TestRail when you choose to export using XML format it will export everything, no option is given to choose to specify what we want to export. In this example we are focusing on that option.

To export from TestRail we are using the _Export to XML_ option in the Test Case upper menu entry.

We have to provide a name for the XML field that will be exported and click "_Export_".

![](https://docs.getxray.app/download/attachments/115556961/Screenshot%202023-08-16%20at%2014.30.09.png?version=7&modificationDate=1731684683247&api=v2)

Looking into more detail on what we have in TestRail, we can see that we have defined 3 sections:

-   Test Cases (with one sub-section)
    -   Regression
-   Exploratory Tests
-   Performance Tests

The file generated by TestRail has the following content:

To import into Xray, we created one script to convert this XML file into a CSV-compatible file to be imported in Xray.

The script will parse the XML file and create a CSV file that can be imported into Xray. To execute the script, use the following command:

`python3 testrail2Xray.py -i comic_estore.xml -o comic_estore.csv`

An optional parameter _(-e)_ is also available to complete the endpoints sent in the XML file. To just append the above command with the _\-e_ option and sent the complete endpoint of your TestRail instance. For example if my TestRail instance is "https://mytestrail.com/" the command will look like this:

`python3 testrail2Xray.py -i comic_estore.xml -o comic_estore.csv -e https:``//mytestrail``.com/`

The output file will only have the Manual Tests, for those all the test steps will be present.

To import it into Xray we use Test Case Importer feature of Xray with the recently created CSV file; you can use the configuration file provided with the _txt_ extension (_XrayCSVImporter-configuration.txt_).

![](https://docs.getxray.app/download/attachments/115556961/Screenshot%202023-08-17%20at%2010.48.21.png?version=7&modificationDate=1731684572266&api=v2&effects=border-simple,shadow-kn)

Once imported we can see that it has created two Tests with the properties defined in the CSV.

![](https://docs.getxray.app/download/attachments/115556961/Screenshot%202023-08-17%20at%2010.50.39.png?version=7&modificationDate=1731684567797&api=v2&effects=border-simple,shadow-kn)

### More Details

Let's look into some specificities of this approach and some test particularities.

#### Test Sections into Test Repository

In TestRail we can organize our tests into sections and subsections as we can see below:

![](https://docs.getxray.app/download/attachments/115556961/Screenshot%202023-08-17%20at%2011.38.11.png?version=7&modificationDate=1731684562960&api=v2&effects=border-simple,shadow-kn)

As we can see in the above picture we have several sections but only the ones with manual tests will be created in Xray. The sections we have in TestRail are:

-   one section called 'T_est Cases_' with 2 tests and a sub-section '_Regression_' with one test
-   one section called '_Exploratory Tests_' with one test
-   one section called '_Performance Tests'_ with one test

TestRail sections and sub-sections are exported into the XML file in the following form:

After running the script that converts the XML file into a CSV format we can see that it adds, in the _Test Repo field,_ the Test Repository name to be created, only for the manual tests, when uploading the file into Xray.

After importing into Xray we can see that new directories were created in the Test Repository:

![](https://docs.getxray.app/download/attachments/115556961/Screenshot%202023-08-17%20at%2011.43.16.png?version=7&modificationDate=1731684557847&api=v2&effects=border-simple,shadow-kn)

#### Manual Tests (With Steps separated and in Text) into Manual Test Case

The templates available by default in TestRail allow you to create Manual Test Cases with steps (using action, data and expected result) or using only a text field to describe the steps.

We have created one test case using the steps in a text field and one using the steps separated into fields, the XML output is the following:

After running the script that converts this XML into a CSV file we can see that, each Test is created and the steps filled with the information extracted from the XML.

The first Test corresponds to a Manual Test Case with the summary obtained from the CSV file, one step with Action and Expected Result and the added type (_Destructive_) as a Label.

Notice that we have added one image in the Expected Result in TestRail and the exported link is reconstructed using the _\-e_ option of the script. 

![](https://docs.getxray.app/download/attachments/115556961/Screenshot%202023-08-28%20at%2018.05.49.png?version=7&modificationDate=1731684537481&api=v2&effects=border-simple,shadow-kn)

The second Test has one line per each step. Notice that the format is kept for the table and styles added in TestRail.

![](https://docs.getxray.app/download/attachments/115556961/Screenshot%202023-08-17%20at%2011.49.33.png?version=7&modificationDate=1731684547310&api=v2&effects=border-simple,shadow-kn)![](https://docs.getxray.app/download/attachments/115556961/Screenshot%202023-08-28%20at%2018.09.20.png?version=7&modificationDate=1731684531500&api=v2&effects=border-simple,shadow-kn)

#### Other Tests

The script will convert all tests of type **Manual**, all the other types will be discarded and no output is created in the resulting CSV file.

The Type field (e.g., "Destructive", "Smoke", "UAT") in TestRail is converted into labels in the Test issues managed by Xray.

BDD Test Cases are not covered in this tutorial due to a limitation in TestRail.

___

## Tips

-   Use the CSV file provided to import the examples and the Test Case Importer configuration file associated with it in order to have the setup and mapping correct.
-   Make sure you are using the scripts available for the right version of Jira (Cloud or Server).