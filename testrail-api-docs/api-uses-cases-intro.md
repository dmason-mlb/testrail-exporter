# API Use Cases Introduction

The API use cases section is meant for TestRail users and third-party app developers who want to create an integration with TestRail. It describes how to use the TestRail API for multiple use cases to integrate your tools with TestRail, along with useful examples and technical implementation samples.

## Common Use Cases

Test cases and test results are often the most relevant entities when it comes to test management. Using the TestRail API, you can:

- Create test cases programmatically
- Export test cases to other systems
- Import test results from automated testing tools
- Export test results for reporting or analysis
- And much more

## Understanding TestRail Entities

Before implementing integrations, it's recommended to familiarize yourself with TestRail entities, customizability, and limitations. This section provides an overview of the data entities available in TestRail, as well as their relationships and particularities.

## TestRail Customizations

TestRail aims to be very flexible to support all kinds of testing workflows. To accommodate custom data required for these workflows, TestRail supports the following field customizations:

- **Case fields** - Add/remove or modify any data field in your cases
- **Case templates** - The template you use to write your test cases (i.e., separated steps)
- **Result fields** - Add/remove or modify any data field in your results
- **Result statuses** - Add/remove or modify the default statuses and their configurations

Note that customizations can be applied to all projects or on a project-by-project basis.

## Project Types and API Considerations

TestRail has multiple project types. When using the API, it's important to understand that for projects which are not single repository, you need to be aware of the separation between suite entities:

- Entities in one suite can't be associated with an entity in a different suite
- For API bulk operations, all entities must belong to the same suite
- You can't select test cases from two different test suites for one test run, as the test run itself is bound to one suite

## Test Case Organization

When it comes to test design, you can organize your test cases in sections and subsections:

- Sections and subsections are the same entity; the difference is that a subsection contains a parent section
- Test cases can make use of custom fields and different templates according to your configurations
- You must be aware of and account for these organizational structures in your integrations

This documentation is based on available information and may not represent the complete or most up-to-date documentation. For the most current information, please refer to the official TestRail documentation.
