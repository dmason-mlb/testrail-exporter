Do you want to migrate tests from other tools? If you are able to export them to an Excel/CSV file, then you may import the tests to Jira using also using the instructions below.  Note that [Xray's Test Case importer](https://docs.getxray.app/display/XRAY/Importing+Manual+Tests+using+Test+Case+Importer) is the **recommended tool** for this purpose and not Jira's native CSV importer as detailed here.

If you need guidance on a specific use case, please [contact us.](https://docs.getxray.app/pages/viewpage.action?pageId=62270414)

## Import Tests

You can import Test definitions from external sources using CSV files, either by using [Xray's Test Case importer](https://docs.getxray.app/display/XRAY/Importing+Manual+Tests+using+Test+Case+Importer) (**recommended**) or Jira's native CSV importer plugin (see [Importing Data from CSV](https://confluence.atlassian.com/display/JIRA/Importing+Data+from+CSV)).

This page explaing the later procedure, which is more generic and supports importing of all Test types. **However**, for manual Tests you should use [Xray's Test Case importer](https://docs.getxray.app/display/XRAY/Importing+Manual+Tests+using+Test+Case+Importer).

To import issues using Jira's CSV importer, as an administrator, you have to:

1.  Log in to Jira as a user with the **Jira Administrators** [global permission](https://confluence.atlassian.com/adminjiraserver071/managing-global-permissions-802592439.html).
2.  Select **Administration > System > Import & Export > External System Import > Import**, and then specify the input CSV file.

![](https://docs.getxray.app/download/attachments/62270414/image2020-6-4_23-41-13.png?version=20&modificationDate=1731678260574&api=v2&effects=border-simple,shadow-kn)

 As a standard user, you can also import issues:

1.  Go to the top **Issues** menu.
2.  Select **Import Issues from CSV.** 

![](https://docs.getxray.app/download/attachments/62270414/image2017-10-2_16-48-38.png?version=20&modificationDate=1731678271239&api=v2&effects=border-simple,shadow-kn)

Mapping Test Steps Custom fields

Please note that when using Manual Test Steps Custom field of Type "Date Picker" or "DateTime Picker", Xray uses the format set in the "Look and Feel" of your Jira instance.

![](https://docs.getxray.app/download/attachments/62270414/image2020-6-4_23-20-15.png?version=20&modificationDate=1731678261500&api=v2)

The format provided in the CSV configuration only refers to Jira custom fields and will not be used by Xray.

 ![](https://docs.getxray.app/download/attachments/62270414/image2020-6-4_23-19-0.png?version=20&modificationDate=1731678262298&api=v2)

The Manual Test Step Custom fields must be configured  and enabled in the target project or else Xray won't be able to map the fields and won't import any manual test step custom field

Please be aware that if one of the Test Step Custom fields is defined as mandatory in the target project and that same Custom Field is empty (without any value) in the CSV, after the Test Case importer process, the Test will be created successfully but without any of the steps.

Aside from the native issue columns like _Summary_ and _Description_, you need to specify in the CSV file additional columns related to Xray Test issues. 

-   **Issue Type** \- <u>must</u> be present in your CSV and must contain the name of Xray Test issue type, which is, by default, "**Test**". Alternately, this column can contain the Test issue type ID.
-   **Test Type** \- <u>required</u> for each Xray Test Issue. This field can have the following values: Manual, Automated\[Cucumber\] or Automated\[Generic\]

There are some columns that you also need to specify, depending on the type of Test as described in the next sections.

Links to requirements

When importing Tests, you can specify the links to the requirements that each Test validates. For that purpose, the columns must be mapped as **Link "Tests"**.

If the Test covers multiple requirements, then multiple CSV columns must be used, each one being mapped in the same way.

![](https://docs.getxray.app/download/attachments/62270414/image2018-3-9_9-38-22.png?version=21&modificationDate=1731678295739&api=v2)

## Importing Manual Tests

Recommended

If you need to import Manual Tests, you should use [Xray's Test Case importer](https://docs.getxray.app/display/XRAY/Importing+Manual+Tests+using+Test+Case+Importer) instead since it supports a more user-friendly CSV file layout for describing Test steps.

Please be aware that it may be necessary to update **Jira Importers Plugin (JIM)** in order to map all custom fields.

If you are importing Tests from a CSV and you are linking your tests to an already existing requirement, you have to **Clear the Requirement Status Cache**. Please check [Importing Tests with (CSV)](https://docs.getxray.app/pages/viewpage.action?pageId=62270414) for more information.  

In order to import Manual Tests in a CSV file to Jira, you need to define the following columns:

-   "**Test Type**", ensuring its value is "Manual"
-   "**Manual Test Steps**"; this is the custom field in the JSON list format representing all your manual steps. Next follows an example of the "**Manual Test Steps**" custom field; due to CSV format, double quotes within this field have to be escaped whenever writing it into the CSV.

`[`

   `{`

      `"index":1,`

      `"fields":{`

         `"Action":"Step 1 action",`

         `"Data":"",`

         `"Expected Result":"Expected result",`

         `"Limit date":"06 Jun 2020"`

      `},`

      `"attachments":[`

         `{`

            `"fileName":"Xray Unit Testing.docx",`

            `"fileIcon":"word.gif",`

            `"mimeType":"application/vnd.openxmlformats-officedocument.wordprocessingml.document",`

            `"fileIconAlt":"Microsoft Word",`

            `"fileSize":"506 kB",`

            `"numericalFileSize":517880,`

            `"created":"2020-06-04T22:46:21+01:00",`

            `"createdDate":"Jun 4, 2020 10:46:21 PM",`

            `"author":"admin",`

            `"authorFullName":"john",`

            `"filePath":"valid/local/path/to/server/inside/jira/directory"`

         `}`

      `]`

   `},`

   `{`

      `"index":2,`

      `"fields":{`

         `"Action":"Step 2 action",`

         `"Data":"",`

         `"Expected Result":"Expected result",`

         `"Limit date":"07 Jun 2020"`

      `},`

      `"attachments":[`

      `]`

   `}`

`]`

This is a  very basic example containing two test cases, having 2 steps each.

`Summary; Assignee; Reporter; Issue Type; Description; Test Type; Manual Test Steps`

`"Basic Test issue"``; admin; admin; Test;` `"This is a basic Test issue"``;` `"Manual"``;` `"[{"``"index"``":1,"``"fields"``":{"``"action"``":"``"Step 1 action"``","``"data"``":"``""``","``"expected result"``":"``"Expected result"``"},"``"attachments"``":[]},{"``"index"``":2,"``"fields"``":{"``"Action"``":"``"Step 2 action"``","``"Data"``": "``""``", "``"Expected result"``":"``"Expected result"``"},"``"attachments"``":[]}]"`

`"Another basic Test issue"``; admin; admin; Test;` `"This is another basic Test issue"``;` `"Manual"``;` `"[{"``"index"``":1,"``"fields"``":{"``"action"``":"``"Step 1 action"``","``"data"``":"``""``","``"expected result"``":"``"Expected result"``"},"``"attachments"``":[]},{"``"index"``":2,"``"fields"``":{"``"Action"``":"``"Step 2 action"``","``"Data"``": "``""``", "``"Expected result"``":"``"Expected result"``"},"``"attachments"``":[]}]"`

This second example shows more complex/complete scenarios, detailing how to specify attachments, additional Xray step custom fields.

`Summary; Assignee; Reporter; Issue Type; Description; Test Type; Manual Test Steps`

`"Test issue 1"``; admin; admin;` `10000``;` `"This is a Test issue"``;` `"Manual"``;` `"[{"``"index"``":1,"``"fields"``":{"``"Action"``:``""``Step` `1` `action``""``,``""``Data``""``:``""``""``,``""``Expected Result``""``:``""``Expected result``""``},``""``attachments``""``:[{``""``fileName``""``:``""``Xray Unit Testing.docx``""``,``""``fileIcon``""``:``""``word.gif``""``,``""``mimeType``""``:``""``application/vnd.openxmlformats-officedocument.wordprocessingml.document``""``,``""``fileIconAlt``""``:``""``Microsoft Word``""``,``""``fileSize``""``:``""``506` `kB``""``,``""``numericalFileSize``""``:``517880``,``""``created``""``:``""``2020``-``06``-04T22:``46``:``21``+``01``:``00``""``,``""``createdDate``":"``"Jun 4, 2020 10:46:21 PM"``","``"author"``":"``"admin"``","``"authorFullName"``":"``"bruce wayne"``","``"filePath"``":"``"/jira/postgres/870/home/data/attachments/IMCSV/10000/IMCSV-1/xray_3883"``"}]},{"``"index"``":2,"``"fields"``":{"``"Action"``":"``"Step 2 action"``","``"Data"``":"``""``","``"Expected Result"``":"``"Expected result"``","``"Limit date"``":"``07` `Jun` `2020``""``},``""``attachments``""``:[]}]"`

`"Test issue 2"``; admin; admin;` `10000``;` `"This is a Test issue"``;` `"Manual"``;` `"[{"``"index"``":1,"``"fields"``":{"``"Action"``":"``"Step 1 action"``","``"Data"``":"``""``","``"Expected Result"``":"``"Expected result"``","``"Limit date"``":"``"06 Jun 2020"``"},"``"attachments"``":[]},{"``"index"``":2,"``"fields"``":{"``"Action"``":"``"Step 2 action"``","``Data``":"``""``","``"Expected Result"``":"``"Expected result"``","``"Limit date"``":"``"07 Jun 2020"``"},"``"attachments"``":[]}]"`

How to optimize this process

Some organizations already have Manual Test definitions in spreadsheets. These spreadsheets normally define all Tests to execute and within each Test, their steps. This is the main reason why  [Xray's Test Case importer](https://docs.getxray.app/display/XRAY/Importing+Manual+Tests+using+Test+Case+Importer) is a better alternative for importing Manual Tests.

Before Xray for Jira 2.1, you could use a [special converter tool](https://docs.getxray.app/pages/viewpage.action?pageId=62270414) (now **deprecated**) for converting these spreadsheet Test definitions, more specifically the Test Steps, into the JSON format above expected by Xray and Jira.

## Importing Cucumber Tests

For Cucumber Test issues, you need to define the following columns in your CSV:

-   **"Test Type**" is "Automated\[Cucumber\]"
-   **"Cucumber Test Type"** is either "Scenario" or "Scenario Outline"
-   **"Cucumber Scenario"** is the contents of a Cucumber Scenario.

## Importing Automated Generic Tests

For automated generic Test issues, you need to define the following columns in your CSV:

-   **"Test Type**" is "Automated\[Generic\]"
-   **"Generic Test Definition"** is the test definition.

## Import Pre-Conditions, Test Sets, Test Executions and Test Plans

Since Xray uses Jira issue types for its core entities, it's also possible to import other entities such as Pre-Condtions, Test Sets, Sub Test Executions, Test Executions and Test Plans.

In the following examples, the Issue Type can either be specified as a string with the name of the Issue Type or with the corresponding _id_ that can be found within "Issue Types" JIRA administration section.

## Pre-Conditions

You can specify the Tests by using the **Tests association with a Pre-Condition** mapping upon importing. Use the comma (",") delimiter to specify multiple tests.

`Summary; Assignee; Reporter; Issue Type; Type; Condition; Description; Tests associated with Pre Condition`

`"Standalone PreCondition"``; admin; admin;` `10``; Manual;` `"calculator must be turned on"``;` `"This is a PreConditon issue"``;`

`"PreCondition linked to 2 Tests"``; admin; admin;` `10``; Manual;` `"calculator must be scientific"``;` `"This is a PreConditon issue"``; CALC-``779``,CALC-``756`

`"PreCondition linked to 1 Test"``; admin; admin;` `10``; Manual;` `"calculator must be normal"``;` `"This is a PreConditon issue"``; CALC-``779`

![](https://docs.getxray.app/download/attachments/62270414/image2018-3-9_9-40-37.png?version=20&modificationDate=1731678291335&api=v2&effects=border-simple,shadow-kn)

## Test Sets

You can specify the Tests by using the **Tests associated with Test Set** mapping upon importing. Use the comma (",") delimiter to specify multiple tests.

`Summary; Assignee; Reporter; Issue Type; Description; Tests associated with Test Set`

`"Test Set without Tests"``; admin; admin;` `8``;` `"This is a Test Set issue"``;`

`"Test Set with 2 Tests"``; admin; admin;` `8``;` `"This is a Test Set issue"``; CALC-``908``,CALC-``887`

![](https://docs.getxray.app/download/attachments/62270414/image2018-3-9_9-41-5.png?version=20&modificationDate=1731678290498&api=v2&effects=border-simple,shadow-kn)

## Test Executions

You can specify the Tests by using the **Tests association with Test Execution** mapping upon importing. Use the comma (",") delimiter to specify multiple tests.

`Fix Version; Summary; Assignee; Reporter; Issue Type; Description; Test Environments; Tests associated with Test Execution`

`"3.0"``;` `"Test Execution without Tests"``; admin; admin;` `9``;` `"This is a Test Execution issue"``;;`

`"3.0"``;` `"Test Execution with 2 Tests"``; admin; admin;` `9``;` `"This is a Test Execution issue"``; Android; CALC-``908``,CALC-``887`

![](https://docs.getxray.app/download/attachments/62270414/image2018-3-9_9-41-36.png?version=20&modificationDate=1731678289685&api=v2&effects=border-simple,shadow-kn)

## Sub Test Executions

Sub Test Executions are sub-tasks of "requirements" (e.g. Story, Epic, other).  Thus, the parent issue key must be provided; Jira's CSV also requires that an <u>empty</u> column mapped to the "Issue Id" to be passed in this case.

You can specify the Tests by using the **Tests association with Test Execution** mapping upon importing. Use the comma (",") delimiter to specify multiple tests.

`Issue Id; Fix Version; Summary; Assignee; Reporter; Issue Type ; Parent issue (requirement); Description; Test Environments; Tests associated with Test Execution`

`;``"3.0"``;` `"Sub Test Execution with 1 Test"``; admin; admin;` `10101``; CALC-``2541``;` `"This is a very simple Sub Test Execution issue"``; Android; CALC-``908`

`;``"3.0"``;` `"Sub Test Execution with 2 Tests"``; admin; admin; Sub Test Execution; CALC-``2541``;` `"This is a Sub Test Execution issue"``; Android; CALC-``908``,CALC-``2542`

![](https://docs.getxray.app/download/attachments/62270414/image2018-5-2_10-41-36.png?version=20&modificationDate=1731678270235&api=v2&effects=border-simple,shadow-kn)

## Test Plans

You can specify the Tests by using the **Tests associated with Test Plan** mapping upon importing. Use the comma (",") delimiter to specify multiple tests.

`Fix Version; Summary; Assignee; Reporter; Issue Type; Description; Tests associated with Test Plan`

`"3.0"``;` `"Test Plan without Tests"``; admin; admin;` `10``;` `"This is a Test Plan issue"``;`

`"3.0"``;` `"Test Plan with 2 Tests"``; admin; admin;` `10``;` `"This is a Test Plan issue"``; CALC-``908``,CALC-``887`

## Copying Tests from one Jira server to another one

Sometimes, you may want to copy Tests specified in some other Jira server, such as a staging or testing environment.

If you need to "migrate" (i.e., copy) the Tests to another Jira server, you may follow the instructions above for exporting Tests to CSV and to import them from CSV.

The general procedure would be:

1.  In the source Jira server
    1.  filter out the relevant Test issues in the Issues search screen
    2.  make visible the columns you want to migrate (don't forget to include the Summary, Issue Type, Test Type, Manual Test Steps and other mandatory fields)
    3.  export visible fields to CSV
2.  In the destination JIRA server
    1.  import Tests from CSV using Jira's built-in CSV importer (don't forget to map all the mandatory fields)

<u>What you will be able to copy</u>:

-   Test-related fields (e.g., summary, labels, etc.)
-   Test Type (mandatory)
-   Manual Test Steps (mandatory for Manual tests)
-   attachments (step-level) if present in the target Jira server directories and mapped in the Manual Test Step Json

<u>What you won't be able to copy</u>:

-   related entities and links (because they won't exist in the destination Jira server)

Please note

This procedure allows you to migrate the essential Test specifications. If you need to migrate test runs and other information, then this procedure is not applicable. You may use the REST API, but it will require some work from your side since there is no direct way to migrate it.

Although Xray allows you to import execution-related information, Xray does not currently provide an out-of-the-box solution for migrating execution-related information along with the corresponding tests from other systems.

Please note

This approach requires some development effort from your side.

1.  **Migrate Tests specification**
    1.  From CSV using [Test Case Importer](https://docs.getxray.app/display/XRAY/Importing+Manual+Tests+using+Test+Case+Importer); supports attachments, but <u>you will miss the mapping information between original_id and the&nbsp;</u> <u>created_issue_key;</u> you will have to somehow manage it.
    2.  Programmatically, create the Test issues using Jira’s REST API (some examples are in [http://confluence.xpand-addons.com/display/XRAY/Tests+-+REST#Tests-REST-CreatingandEditingTests-JIRARESTAPI](http://confluence.xpand-addons.com/display/XRAY/Tests+-+REST#Tests-REST-CreatingandEditingTests-JIRARESTAPI) ); this will allow you to easily identify the mapping original\_id<=>created\_issue\_key, which can be used afterwards.

2\. **Migrate organization (optional, not really necessary)**

This depends on the legacy system organization. If it somehow groups tests, then use the Jira REST API to create the Test Set issues. After that, use Xray’s REST API to add the Tests. You must know the Tests issue keys in advance. On the other hand, in case you're using folders as means to organize Tests both in the original system and also in Xray, you may simply specify the folder as being mapped to the "Test Repository Path" Xray's custom field during the Test Case Importer's import process.

3\. **Import results**

a) Create Test Executions with their respective Tests

Use the Jira REST API can be used to create the Test Execution issue. After that, use Xray’s REST API (i.e., POST /rest/raven/1.0/api/testexec/{testExecKey}/test) to add the Tests. You must know the Tests issue keys in advance.

b) Import results for each Test Execution

-   -   Import just the overall test result, for each test run that is part of the test execution.
    -   Import detailed test run results, including per step information

                Each approach can be achieved using the REST API, and the <u>POST /rest/raven/1.0/import/execution</u> endpoint. You just need to know in advance the Test Execution key and also the issues keys for each Test that is part of the Test Execution.

## Configuring maximum allowed attachment size

The maximum allowed size for the Test Case Importer is the same as [Jira's](https://confluence.atlassian.com/adminjiraserver/configuring-file-attachments-938847851.html) for CSV imports.