# Spec: PII Mock Data Generator

**Spec ID:** SDD-20260209-pii-mock-data-generator
**Created:** 2026-02-09
**Platform:** Microsoft Fabric + Azure (generic, adaptable to other platforms)
**Status:** Draft

## Overview

A reusable Claude Code skill (`/generate-mock-data`) and pattern for safely developing data pipelines against PII-containing sources that lack test environments. The solution extracts metadata (schema, relationships) from production sources, generates synthetic data with preserved referential integrity, and loads it into development Bronze layers.

## Problem Statement

**Current Challenge:**
- Sources like Alexis HR contain PII (names, emails, personal numbers, salaries)
- No test/sandbox environments available from vendors
- Compliance prohibits production PII in dev environments (ISO 27001 A.12.1.4, GDPR Art. 25)
- Data engineers need realistic schemas and relationships to develop pipelines

**Impact:**
- Cannot develop new data domains without violating compliance
- Delays in onboarding new sources
- Repetitive manual work for each new source

**Desired Outcome:**
- Generic, repeatable process for any PII source
- Metadata extraction → Template creation → Synthetic data generation → Dev loading
- Documented templates stored in project repos for reuse
- Hundreds of rows with preserved FK relationships

## Success Criteria

**Must Have:**
1. `/generate-mock-data` skill works for Alexis HR as reference implementation
2. Extracts metadata from REST API (entities, fields, types, relationships)
3. Generates metadata template stored in `projects/<project>/docs/templates/<source>/`
4. Creates synthetic data (hundreds of rows) with FK integrity
5. Loads mock data to dev Bronze layer tables
6. Process documented as reusable pattern in parent repo

**Should Have:**
- Support for SQL databases (JDBC) and SaaS platforms in addition to REST APIs
- Ability to reuse existing templates (skip extraction step)
- FK relationship auto-detection from API responses

**Won't Have (v1):**
- Automated refresh (one-time setup only)
- Statistical distribution matching (simple random generation acceptable)
- Integration with Terraform/CI-CD

## User Stories

### Story 1: First-Time Mock Data Generation

**As a** data engineer onboarding a new PII source
**I want to** generate mock data automatically from production metadata
**So that** I can develop Bronze/Silver/Gold pipelines in dev without compliance violations

**Acceptance Criteria:**
- Given Alexis HR API credentials in Key Vault
- When I run `/generate-mock-data alexis` and select "Extract metadata first"
- Then Claude extracts schema from `/employee`, `/compensation`, `/department`, `/office`, `/team`
- And saves metadata template to `projects/cloud2-azure-dataplatform/docs/templates/alexis/metadata.json`
- And generates 200 employees, 200 compensation records, 5 departments, 3 offices, 10 teams
- And preserves FK relationships (employee.departmentId → department.id)
- And loads data to `dev.bronze_alexis_*` tables in Fabric

### Story 2: Reusing Existing Template

**As a** data engineer adding a new domain with the same source
**I want to** reuse an existing metadata template
**So that** I don't need to re-extract metadata from production

**Acceptance Criteria:**
- Given existing template at `projects/<project>/docs/templates/alexis/metadata.json`
- When I run `/generate-mock-data alexis` and select "Use existing template"
- Then Claude loads the template instead of calling production API
- And generates fresh synthetic data based on the template
- And loads to dev Bronze layer

### Story 3: Generic Pattern Documentation

**As a** team lead
**I want** the pattern documented as a reusable template
**So that** any team member can onboard new PII sources independently

**Acceptance Criteria:**
- Documentation exists at `docs/patterns/pii-mock-data-generation.md`
- Covers REST API, SQL database, and SaaS platform metadata extraction
- Includes examples from Alexis HR reference implementation
- Links to `/generate-mock-data` skill for automation

## Technical Design

### Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                  PII MOCK DATA GENERATOR                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Phase 1: METADATA EXTRACTION                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Production Source (Alexis HR API)                        │  │
│  │    ↓                                                      │  │
│  │  Extract Schema (entities, fields, types, FK)            │  │
│  │    ↓                                                      │  │
│  │  Save Template: docs/templates/alexis/metadata.json      │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                     │
│  Phase 2: SYNTHETIC DATA GENERATION                             │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Load Template                                            │  │
│  │    ↓                                                      │  │
│  │  Generate Seed Data (independent entities first)         │  │
│  │    - Departments (5)                                     │  │
│  │    - Offices (3)                                         │  │
│  │    - Teams (10)                                          │  │
│  │    ↓                                                      │  │
│  │  Generate Dependent Data (with FKs)                      │  │
│  │    - Employees (200) → teamId, departmentId, officeId   │  │
│  │    - Compensation (200) → employeeId                    │  │
│  │    ↓                                                      │  │
│  │  Create Parquet/Delta files                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                           ↓                                     │
│  Phase 3: DEV LOADING                                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Load to Dev Bronze Tables                                │  │
│  │    - bronze_alexis_employees                             │  │
│  │    - bronze_alexis_compensation                          │  │
│  │    - bronze_alexis_departments                           │  │
│  │    - bronze_alexis_offices                               │  │
│  │    - bronze_alexis_teams                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Metadata Template Schema

```json
{
  "source": "alexis",
  "source_type": "rest_api",
  "base_url": "https://api.alexishr.com/v1",
  "extracted_at": "2026-02-09T10:00:00Z",
  "entities": [
    {
      "name": "employees",
      "api_endpoint": "/employee",
      "bronze_table": "bronze_alexis_employees",
      "row_count": 200,
      "fields": [
        {"name": "id", "type": "string", "pii": false, "primary_key": true},
        {"name": "email", "type": "string", "pii": true, "faker_method": "email"},
        {"name": "firstName", "type": "string", "pii": true, "faker_method": "first_name"},
        {"name": "lastName", "type": "string", "pii": true, "faker_method": "last_name"},
        {"name": "personalNumber", "type": "string", "pii": true, "faker_method": "ssn"},
        {"name": "teamId", "type": "string", "foreign_key": "teams.id"},
        {"name": "departmentId", "type": "string", "foreign_key": "departments.id"},
        {"name": "officeId", "type": "string", "foreign_key": "offices.id"}
      ]
    },
    {
      "name": "compensation",
      "api_endpoint": "/compensation",
      "bronze_table": "bronze_alexis_compensation",
      "row_count": 200,
      "fields": [
        {"name": "id", "type": "string", "pii": false, "primary_key": true},
        {"name": "employeeId", "type": "string", "foreign_key": "employees.id"},
        {"name": "salary", "type": "decimal", "pii": false, "faker_method": "random_int", "faker_args": {"min": 30000, "max": 150000}},
        {"name": "currency", "type": "string", "pii": false, "faker_method": "currency_code"},
        {"name": "effectiveDate", "type": "date", "pii": false, "faker_method": "date_this_year"}
      ]
    },
    {
      "name": "departments",
      "api_endpoint": "/department",
      "bronze_table": "bronze_alexis_departments",
      "row_count": 5,
      "fields": [
        {"name": "id", "type": "string", "pii": false, "primary_key": true},
        {"name": "name", "type": "string", "pii": false, "faker_method": "job"}
      ]
    },
    {
      "name": "offices",
      "api_endpoint": "/office",
      "bronze_table": "bronze_alexis_offices",
      "row_count": 3,
      "fields": [
        {"name": "id", "type": "string", "pii": false, "primary_key": true},
        {"name": "name", "type": "string", "pii": false, "faker_method": "city"},
        {"name": "country", "type": "string", "pii": false, "faker_method": "country_code"}
      ]
    },
    {
      "name": "teams",
      "api_endpoint": "/team",
      "bronze_table": "bronze_alexis_teams",
      "row_count": 10,
      "fields": [
        {"name": "id", "type": "string", "pii": false, "primary_key": true},
        {"name": "name", "type": "string", "pii": false, "faker_method": "bs"},
        {"name": "departmentId", "type": "string", "foreign_key": "departments.id"}
      ]
    }
  ],
  "relationships": [
    {"from": "employees.teamId", "to": "teams.id"},
    {"from": "employees.departmentId", "to": "departments.id"},
    {"from": "employees.officeId", "to": "offices.id"},
    {"from": "compensation.employeeId", "to": "employees.id"},
    {"from": "teams.departmentId", "to": "departments.id"}
  ]
}
```

### Claude Code Skill: `/generate-mock-data`

**File:** `.claude/commands/generate-mock-data.md`

**Behavior:**
1. Prompt user: "Extract metadata first or use existing template?"
2. **If extract:**
   - Ask for source name and type (REST API, SQL, SaaS)
   - Ask for authentication details (Key Vault secret name)
   - Call production API/database to extract schema
   - Detect FK relationships from response structure
   - Save template to `projects/<project>/docs/templates/<source>/metadata.json`
3. **If existing template:**
   - List available templates in `projects/<project>/docs/templates/`
   - Load selected template
4. Generate synthetic data using Python Faker library
5. Create Fabric notebook for loading to Bronze
6. Execute notebook to load dev Bronze tables

### Data Generation Algorithm

**Topological Sort for FK Dependencies:**

1. Build dependency graph from relationships
2. Sort entities by dependency (independent first)
3. Generate data in order:
   - **Level 0** (no dependencies): Departments, Offices
   - **Level 1** (depends on Level 0): Teams
   - **Level 2** (depends on Level 0-1): Employees
   - **Level 3** (depends on Level 2): Compensation

**FK Assignment:**
- When generating dependent entity, randomly select existing parent ID
- Example: For each Employee, pick random Team.id from generated teams

**Python Implementation Sketch:**

```python
from faker import Faker
import pandas as pd
import uuid

fake = Faker()

# Level 0: Departments
departments = [
    {"id": str(uuid.uuid4()), "name": fake.job()}
    for _ in range(5)
]

# Level 1: Teams (FK to departments)
teams = [
    {
        "id": str(uuid.uuid4()),
        "name": fake.bs(),
        "departmentId": fake.random_element([d["id"] for d in departments])
    }
    for _ in range(10)
]

# Level 2: Employees (FK to teams, departments, offices)
employees = [
    {
        "id": str(uuid.uuid4()),
        "email": fake.email(),
        "firstName": fake.first_name(),
        "lastName": fake.last_name(),
        "personalNumber": fake.ssn(),
        "teamId": fake.random_element([t["id"] for t in teams]),
        "departmentId": fake.random_element([d["id"] for d in departments]),
        "officeId": fake.random_element([o["id"] for o in offices])
    }
    for _ in range(200)
]

# Level 3: Compensation (FK to employees)
compensation = [
    {
        "id": str(uuid.uuid4()),
        "employeeId": emp["id"],  # 1:1 relationship
        "salary": fake.random_int(30000, 150000),
        "currency": "EUR",
        "effectiveDate": fake.date_this_year()
    }
    for emp in employees
]
```

### Metadata Extraction Strategies

#### REST API (Alexis HR)

1. Make authenticated API call to each endpoint
2. Retrieve sample response (limit=1)
3. Infer schema from JSON structure:
   - Field names from keys
   - Types from value inspection (string, int, float, date)
   - Nested objects as potential FK relationships
4. Prompt user to confirm FK relationships and PII fields

#### SQL Database (JDBC)

1. Query `INFORMATION_SCHEMA.COLUMNS` for schema
2. Query `INFORMATION_SCHEMA.KEY_COLUMN_USAGE` for FK constraints
3. Auto-detect PII fields by name patterns (email, phone, ssn, name, salary)

#### SaaS Platform (Generic)

1. Use platform-specific metadata API if available (e.g., Salesforce Describe API)
2. Fallback to sample data inspection for REST APIs

## Implementation Plan

### Phase 1: Metadata Extraction for Alexis HR

**Deliverables:**
- Python script or notebook: `extract_metadata_alexis.py`
- Metadata template: `projects/cloud2-azure-dataplatform/docs/templates/alexis/metadata.json`

**Steps:**
1. Read Alexis API credentials from Key Vault
2. Call each endpoint with limit=1
3. Parse JSON schema
4. Detect FK relationships (e.g., `teamReference` in employee response)
5. Prompt for PII field confirmation
6. Save template

### Phase 2: Synthetic Data Generation

**Deliverables:**
- Fabric notebook: `nb_util_generate_mock_data_alexis.Notebook`
- Generated Parquet files in OneLake temp location

**Steps:**
1. Load metadata template
2. Implement topological sort for dependency order
3. Use Faker to generate data per entity
4. Write Parquet files to `Files/<source>_mock/`

### Phase 3: Dev Bronze Loading

**Deliverables:**
- Bronze loading notebook (reuses existing pattern from [notebook-standards.md](../../platforms/fabric/notebook-standards.md))

**Steps:**
1. Read Parquet files from `Files/<source>_mock/`
2. Add metadata columns (`_ingested_at`, `_source_system`)
3. Write to Bronze Delta tables

### Phase 4: Claude Code Skill

**Deliverables:**
- `.claude/commands/generate-mock-data.md`

**Steps:**
1. Implement interactive prompts (extract vs. existing template)
2. Orchestrate metadata extraction, data generation, loading
3. Handle errors gracefully

### Phase 5: Pattern Documentation

**Deliverables:**
- `docs/patterns/pii-mock-data-generation.md`
- Update to `docs/principles/environment-separation.md`

**Steps:**
1. Document the pattern generically (not Alexis-specific)
2. Provide examples for REST API, SQL, SaaS
3. Include troubleshooting section

## Testing Strategy

### Functional Testing

1. **Alexis HR End-to-End:**
   - Run `/generate-mock-data alexis` (extract mode)
   - Verify metadata.json correctness
   - Verify 200 employees, 200 compensation, 5 departments, 3 offices, 10 teams generated
   - Verify FK integrity (no orphaned records)
   - Verify Bronze tables created in dev

2. **Template Reuse:**
   - Run `/generate-mock-data alexis` (existing template mode)
   - Verify data generated without calling API

### Data Quality Checks

1. **FK Integrity:**
   - All employee.teamId values exist in teams.id
   - All compensation.employeeId values exist in employees.id

2. **Row Counts:**
   - Match template specifications

3. **PII Realism:**
   - Emails are valid format
   - Names are realistic (not "test123")

### Compliance Verification

1. **No Production Data:**
   - Verify no actual Alexis employee names/emails in generated data
   - Audit log shows no prod data accessed during dev loading

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| API schema changes break template | Medium | Low | Version templates, add schema validation |
| FK detection fails for complex relationships | High | Medium | Manual template editing as fallback |
| Generated data doesn't match production patterns | Low | High | Acceptable for v1 (simple random data) |
| Accidental production data exposure | High | Low | Code review, no production API calls during generation phase |

## Open Questions

1. Should we support SQL databases in v1 or defer to v2? **Decision: Include in pattern docs, implement for REST API only in v1**
2. How to handle circular FK dependencies? **Decision: Break cycles manually in template, document workaround**
3. Should template include sample data for validation? **Decision: No, just schema metadata**

## Non-Functional Requirements

- **Performance:** Metadata extraction < 2 minutes for 5 entities
- **Usability:** `/generate-mock-data` workflow completable in < 10 minutes
- **Maintainability:** Templates editable as JSON (no code changes needed)
- **Portability:** Pattern works for Databricks, Snowflake (adapt loading step)

## References

- [Environment Separation](../../principles/environment-separation.md)
- [Security & Privacy](../../principles/security-privacy.md)
- [Fabric Notebook Standards](../../platforms/fabric/notebook-standards.md)
- [Alexis HR Source Documentation](../../../projects/cloud2-azure-dataplatform/docs/sources/alexis.md)
- [Faker Documentation](https://faker.readthedocs.io/)

---

## Approval

**Status:** Draft - awaiting Gate #2 approval

**Approver:** [User]

**Approval Date:** [Pending]
