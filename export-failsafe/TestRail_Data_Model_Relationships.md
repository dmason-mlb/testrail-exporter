# TestRail Data Model and Field Relationships

This document provides a comprehensive mapping of the relationships between different data entities in the TestRail export, designed to inform the creation of a SQLite database schema.

## Data Hierarchy

```
Projects
├── Project Info
├── Suites (Multiple per Project)
│   ├── Suite Info
│   ├── Sections (Hierarchical)
│   └── Cases
├── Templates
├── Users
└── Milestones
```

## Global Data (Root Level)

### 1. Projects (`projects.json`)
- **Primary Key**: `id`
- **Fields**:
  - `id`: Unique project identifier
  - `name`: Project name
  - `announcement`: Optional project announcement
  - `show_announcement`: Boolean flag
  - `is_completed`: Project completion status
  - `completed_on`: Unix timestamp of completion
  - `suite_mode`: Suite organization mode (1=single suite, 2=single suite + baselines, 3=multiple suites)
  - `url`: TestRail URL for the project

### 2. Case Fields (`case_fields.json`)
- **Primary Key**: `id`
- **Fields**:
  - `id`: Unique field identifier
  - `is_active`: Whether field is currently active
  - `type_id`: Field type (5=checkbox, 6=dropdown, etc.)
  - `name`: Internal field name
  - `system_name`: System name (prefixed with "custom_")
  - `label`: Display label
  - `description`: Field description
  - `configs`: Array of configuration objects
    - `context.is_global`: Whether field is global
    - `context.project_ids`: Array of project IDs where field applies
    - `options`: Field-specific options
  - `display_order`: Display order in UI
  - `include_all`: Whether to include in all projects
  - `template_ids`: Array of template IDs where field is used

### 3. Case Types (`case_types.json`)
- **Primary Key**: `id`
- **Fields**:
  - `id`: Unique type identifier
  - `name`: Type name (e.g., "Regression", "Smoke", "Automated")
  - `is_default`: Whether this is the default type

### 4. Priorities (`priorities.json`)
- **Primary Key**: `id`
- **Fields**:
  - `id`: Unique priority identifier
  - `name`: Full priority name (e.g., "1 - High Priority")
  - `short_name`: Short name (e.g., "1 - High")
  - `is_default`: Whether this is the default priority
  - `priority`: Numeric priority value (higher = more important)

## Project-Level Data

### 5. Suites (`projects/{project_name}/suites.json`)
- **Primary Key**: `id`
- **Foreign Key**: `project_id` → Projects.id
- **Fields**:
  - `id`: Unique suite identifier
  - `name`: Suite name
  - `description`: Suite description
  - `project_id`: Parent project ID
  - `is_master`: Whether this is the master suite
  - `is_baseline`: Whether this is a baseline suite
  - `is_completed`: Suite completion status
  - `completed_on`: Unix timestamp of completion
  - `url`: TestRail URL for the suite

### 6. Templates (`projects/{project_name}/templates.json`)
- **Primary Key**: `id`
- **Foreign Key**: `project_id` (implicit from location)
- **Fields**:
  - `id`: Unique template identifier
  - `name`: Template name
  - `is_default`: Whether this is the default template

### 7. Users (`projects/{project_name}/users.json`)
- **Primary Key**: `id`
- **Fields**:
  - `id`: Unique user identifier
  - `name`: User's full name
  - `email`: User's email address
  - `is_active`: Whether user is active
  - `role_id`: User's role ID

### 8. Milestones (`projects/{project_name}/milestones.json`)
- **Primary Key**: `id`
- **Foreign Key**: `project_id` (implicit from location)
- **Fields**:
  - `id`: Unique milestone identifier
  - `name`: Milestone name
  - `description`: Milestone description
  - `due_on`: Due date (Unix timestamp)
  - `is_completed`: Completion status
  - `completed_on`: Completion date (Unix timestamp)

## Suite-Level Data

### 9. Sections (`projects/{project_name}/{suite_name}/sections.json`)
- **Primary Key**: `id`
- **Foreign Keys**:
  - `suite_id` → Suites.id
  - `parent_id` → Sections.id (self-referential for hierarchy)
- **Fields**:
  - `id`: Unique section identifier
  - `suite_id`: Parent suite ID
  - `name`: Section name
  - `description`: Section description
  - `parent_id`: Parent section ID (null for top-level sections)
  - `display_order`: Display order within parent
  - `depth`: Nesting depth (0 for top-level)

### 10. Cases (`projects/{project_name}/{suite_name}/cases.json`)
- **Primary Key**: `id`
- **Foreign Keys**:
  - `section_id` → Sections.id
  - `suite_id` → Suites.id
  - `template_id` → Templates.id
  - `type_id` → Case Types.id
  - `priority_id` → Priorities.id
  - `milestone_id` → Milestones.id (nullable)
  - `created_by` → Users.id
  - `updated_by` → Users.id
- **Fields**:
  - `id`: Unique case identifier
  - `title`: Case title
  - `section_id`: Parent section ID
  - `template_id`: Template used
  - `type_id`: Case type
  - `priority_id`: Case priority
  - `milestone_id`: Associated milestone (nullable)
  - `refs`: External references (comma-separated)
  - `created_by`: User ID who created the case
  - `created_on`: Creation timestamp
  - `updated_by`: User ID who last updated
  - `updated_on`: Last update timestamp
  - `estimate`: Time estimate (nullable)
  - `estimate_forecast`: Calculated forecast (nullable)
  - `suite_id`: Parent suite ID
  - `display_order`: Display order within section
  - Custom fields (prefixed with `custom_`)

## Key Relationships for Database Design

### 1. Project → Suite Relationship
- One-to-Many: A project can have multiple suites
- Suite Mode determines structure:
  - Mode 1: Single suite (no suite subdirectories)
  - Mode 3: Multiple suites (suite subdirectories)

### 2. Suite → Section Relationship
- One-to-Many: A suite contains multiple sections
- Sections can be hierarchical (parent_id self-reference)

### 3. Section → Case Relationship
- One-to-Many: A section contains multiple cases
- Cases reference their section via `section_id`

### 4. Case → Reference Relationships
- Case → User: `created_by` and `updated_by` reference Users
- Case → Type: `type_id` references Case Types
- Case → Priority: `priority_id` references Priorities
- Case → Milestone: `milestone_id` references Milestones (optional)
- Case → Template: `template_id` references Templates

### 5. Custom Fields Relationship
- Case Fields define available custom fields
- Cases contain actual custom field values
- Field applicability determined by:
  - `project_ids` in field config
  - `template_ids` in field definition

## Database Schema Recommendations

### Primary Tables
1. `projects` - All projects
2. `suites` - All test suites
3. `sections` - All sections (with hierarchy)
4. `cases` - All test cases
5. `case_types` - Global case types
6. `priorities` - Global priorities
7. `case_fields` - Custom field definitions
8. `templates` - Project templates
9. `users` - All users
10. `milestones` - Project milestones

### Junction Tables (for many-to-many relationships)
1. `case_field_projects` - Links case fields to projects
2. `case_field_templates` - Links case fields to templates

### Denormalization Opportunities
For better query performance, consider:
1. Adding `project_id` to cases table (currently only accessible via suite)
2. Adding `section_name` to cases table for quick access
3. Creating a flattened view combining cases with their section/suite/project info

### Index Recommendations
- Primary keys on all `id` fields
- Foreign key indexes on all reference fields
- Composite indexes on:
  - (project_id, suite_id) in sections
  - (suite_id, section_id) in cases
  - (project_id, is_completed) for project filtering

## Notes for Implementation

1. **File Path Parsing**: Project and suite names in the directory structure are sanitized versions of the actual names. The true names are in the JSON files.

2. **Single Suite Mode**: Projects with `suite_mode=1` store sections and cases directly under the project directory, not in a suite subdirectory.

3. **Custom Fields**: Custom fields are dynamic and vary by project/template. Store as JSON or create a separate key-value table.

4. **Timestamps**: All timestamps are Unix timestamps (seconds since epoch).

5. **Null Handling**: Many fields can be null (milestone_id, refs, estimates, etc.). Design schema accordingly.

6. **User References**: The export may contain user IDs that don't exist in the users.json if users have been deactivated.