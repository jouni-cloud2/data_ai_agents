# PII Mock Data Generation Pattern

A reusable pattern for safely developing data pipelines against PII-containing sources that lack test environments.

## Problem

**Challenge:**
- Production sources contain PII (names, emails, SSN, salaries)
- Vendors don't provide test/sandbox environments
- Compliance prohibits production PII in dev (ISO 27001, GDPR)
- Data engineers need realistic schemas and relationships

**Solution:**
- Extract metadata (schema, relationships) from production
- Generate synthetic data preserving referential integrity
- Load to dev Bronze layer for pipeline development

---

## Overview

```
┌─────────────────────────────────────────────────────────────┐
│              PII MOCK DATA GENERATION PATTERN                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Production (Read-Only)         Development (Full Access)   │
│  ┌──────────────────┐          ┌──────────────────┐        │
│  │ REST API / SQL   │          │ Mock Data Gen    │        │
│  │                  │          │                  │        │
│  │ Extract metadata │ ──────►  │ Generate         │        │
│  │ (schema only)    │          │ synthetic data   │        │
│  └──────────────────┘          │                  │        │
│                                │ Preserve FK      │        │
│                                │ integrity        │        │
│                                └────────┬─────────┘        │
│                                         │                  │
│                                         ▼                  │
│                                ┌──────────────────┐        │
│                                │ Dev Bronze       │        │
│                                │ Tables           │        │
│                                │                  │        │
│                                │ - employees      │        │
│                                │ - compensation   │        │
│                                │ - departments    │        │
│                                └──────────────────┘        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## When to Use This Pattern

Use this pattern when:

- ✅ Source contains PII or confidential data
- ✅ No test/sandbox environment available from vendor
- ✅ Need to develop Bronze → Silver → Gold pipelines
- ✅ Compliance requires dev/prod separation
- ✅ Source has stable schema

Don't use when:

- ❌ Vendor provides test environment (use that instead)
- ❌ Source has no PII (use production directly in dev)
- ❌ Schema changes frequently (manual sync overhead)

---

## Implementation Steps

### Step 1: Extract Metadata

Extract schema information from production source:

#### For REST APIs

```python
from utils.mock_data_generator import RestApiExtractor, MetadataTemplate

# Initialize extractor with API credentials
extractor = RestApiExtractor(
    base_url="https://api.example.com/v1",
    api_token="<from-key-vault>"
)

# Create template
template = MetadataTemplate(
    source="example",
    source_type="rest_api",
    base_url="https://api.example.com/v1"
)

# Extract each endpoint
entity = extractor.extract_entity(
    endpoint="/employees",
    entity_name="employees",
    bronze_table="bronze_example_employees",
    row_count=200,
    query_params={"limit": 1}  # Sample only
)
template.add_entity(entity)

# Save template
template.save("projects/<project>/docs/templates/example/metadata.json")
```

**What gets extracted:**
- Field names and types (string, int, date, etc.)
- PII detection (email, name, SSN patterns)
- Primary keys (id fields)
- Foreign key hints (nested objects, *Id fields)

**Compliance:**
- Only reads 1 sample record per endpoint
- No production data stored (schema only)
- Read-only API access

#### For SQL Databases

```python
from utils.mock_data_generator import SqlExtractor, MetadataTemplate

# Connect to database
extractor = SqlExtractor(
    connection_string="<jdbc-connection-string>"
)

# Extract table schema
entity = extractor.extract_entity(
    table_name="employees",
    bronze_table="bronze_example_employees"
)
template.add_entity(entity)

# Extract FK relationships automatically
relationships = extractor.extract_relationships()
for rel in relationships:
    template.add_relationship(rel)

# Save template
template.save("projects/<project>/docs/templates/example/metadata.json")
```

**What gets extracted:**
- Column names, types, constraints from INFORMATION_SCHEMA
- Primary keys from KEY_COLUMN_USAGE
- Foreign keys from REFERENTIAL_CONSTRAINTS
- PII detection by name patterns

#### For SaaS Platforms

Use platform-specific metadata APIs:

| Platform | Metadata API |
|----------|--------------|
| **Salesforce** | Describe API (`/sobjects/<object>/describe`) |
| **Dynamics 365** | EntityDefinitions API |
| **ServiceNow** | Table API (`/api/now/table/sys_db_object`) |

Follow REST API pattern but use platform's metadata endpoint.

---

### Step 2: Review and Edit Template

The generated template is a JSON file you can manually edit:

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
        {
          "name": "id",
          "type": "string",
          "pii": false,
          "primary_key": true,
          "faker_method": "uuid4"
        },
        {
          "name": "email",
          "type": "string",
          "pii": true,
          "faker_method": "email"
        },
        {
          "name": "teamId",
          "type": "string",
          "foreign_key": "teams.id"
        }
      ]
    },
    {
      "name": "teams",
      "api_endpoint": "/team",
      "bronze_table": "bronze_alexis_teams",
      "row_count": 10,
      "fields": [
        {
          "name": "id",
          "type": "string",
          "primary_key": true,
          "faker_method": "uuid4"
        },
        {
          "name": "name",
          "type": "string",
          "faker_method": "bs"
        }
      ]
    }
  ],
  "relationships": [
    {"from": "employees.teamId", "to": "teams.id"}
  ]
}
```

**Common Edits:**
- Confirm FK relationships (auto-detection may miss some)
- Adjust row counts per entity
- Customize Faker methods for realistic data
- Mark additional PII fields

---

### Step 3: Generate Synthetic Data

Use the template to generate data:

```python
from utils.mock_data_generator import MetadataTemplate, SyntheticDataGenerator

# Load template
template = MetadataTemplate.load(
    "projects/<project>/docs/templates/example/metadata.json"
)

# Generate data
generator = SyntheticDataGenerator(template, seed=42)
data = generator.generate_all()

# Verify
summary = generator.get_summary()
print(summary)
# Output: {'teams': 10, 'employees': 200}
```

**How it works:**

1. **Topological Sort:**
   - Analyzes FK relationships
   - Sorts entities by dependency
   - Generates independent entities first (e.g., departments, teams)
   - Then dependent entities (e.g., employees → teamId)

2. **Data Generation:**
   - Uses [Faker library](https://faker.readthedocs.io/) for realistic fake data
   - Generates UUIDs for primary keys
   - Randomly assigns FKs from available parent records
   - Applies field-specific Faker methods (email, name, etc.)

3. **FK Integrity:**
   - All FK values guaranteed to exist in parent table
   - No orphaned records

---

### Step 4: Load to Dev Bronze

Load generated data to Bronze tables:

#### In Fabric Notebooks

```python
from pyspark.sql.functions import current_timestamp, lit

for entity_name, records in data.items():
    # Create DataFrame
    df = spark.createDataFrame(records)

    # Add metadata columns
    df = df.withColumn("_ingested_at", current_timestamp())
    df = df.withColumn("_source_system", lit(f"{source}_mock"))
    df = df.withColumn("_environment", lit("dev"))

    # Write to Bronze
    bronze_table = f"bronze_{source}_{entity_name}"
    df.write.format("delta").mode("overwrite").saveAsTable(bronze_table)

    print(f"✓ Loaded {len(records)} records to {bronze_table}")
```

#### Local/Spark

```python
import pandas as pd

for entity_name, records in data.items():
    df = pd.DataFrame(records)
    df.to_parquet(f"output/{entity_name}.parquet", index=False)
```

---

## Faker Method Reference

Common Faker methods for field types:

| Field Pattern | Faker Method | Example Output |
|---------------|--------------|----------------|
| `email` | `email()` | `john.doe@example.com` |
| `firstName` | `first_name()` | `John` |
| `lastName` | `last_name()` | `Doe` |
| `name` | `name()` | `John Doe` |
| `phone` | `phone_number()` | `+1-555-123-4567` |
| `address` | `address()` | `123 Main St, City` |
| `city` | `city()` | `New York` |
| `country` | `country()` | `United States` |
| `ssn` / `personalNumber` | `ssn()` | `123-45-6789` |
| `salary` | `random_int(min=30000, max=150000)` | `75000` |
| `company` | `company()` | `Acme Corp` |
| `job` / `title` | `job()` | `Software Engineer` |
| `url` | `url()` | `https://example.com` |
| `date` | `date()` | `2026-02-09` |
| `datetime` | `date_time()` | `2026-02-09 14:30:00` |
| `currency` | `currency_code()` | `USD` |
| `uuid` / `id` | `uuid4()` | `a1b2c3d4-...` |

Full reference: [Faker Documentation](https://faker.readthedocs.io/en/master/providers.html)

---

## Automation with `/generate-mock-data`

Use the Claude Code skill for guided workflow:

```bash
/generate-mock-data alexis
```

The skill will:
1. Detect project and source type
2. Ask: Extract metadata or use existing template?
3. If extract: Guide through API credentials and endpoint selection
4. If existing: List available templates
5. Generate synthetic data
6. Load to dev Bronze
7. Verify FK integrity and row counts

See [`.claude/commands/generate-mock-data.md`](../../.claude/commands/generate-mock-data.md) for details.

---

## Best Practices

### 1. Row Counts

Match production distribution patterns:

| Entity Type | Suggested Row Count |
|-------------|---------------------|
| **Fact tables** (transactions) | 500-1000 |
| **Dimension tables** (customers) | 100-200 |
| **Reference data** (departments) | 5-20 |

Higher counts improve testing but slow generation.

### 2. Relationships

**One-to-Many:**
```json
{
  "from": "employees.departmentId",
  "to": "departments.id"
}
```
Each employee assigned random department.

**Many-to-Many:**
Create junction table:
```json
{
  "name": "employee_skills",
  "fields": [
    {"name": "employeeId", "foreign_key": "employees.id"},
    {"name": "skillId", "foreign_key": "skills.id"}
  ]
}
```

**Circular Dependencies:**
Break cycle by making one FK nullable:
```json
{
  "name": "managerEmployeeId",
  "foreign_key": "employees.id",
  "nullable": true
}
```

### 3. PII Realism

Use appropriate Faker methods:

```json
{
  "name": "salary",
  "type": "int",
  "faker_method": "random_int",
  "faker_args": {"min": 30000, "max": 150000}
}
```

Better than generic `random_int()` for realistic testing.

### 4. Template Versioning

Version templates with source schema changes:

```
projects/<project>/docs/templates/
└── alexis/
    ├── metadata.json          # Current version
    ├── metadata_v1.json       # Previous version
    └── README.md              # Changelog
```

### 5. Compliance Tags

Tag mock data for auditing:

```python
df = df.withColumn("_source_system", lit("alexis_mock"))
df = df.withColumn("_is_synthetic", lit(True))
```

Prevents accidental use in production.

---

## Troubleshooting

### FK Reference Not Found

**Error:**
```
ValueError: Cannot generate FK for employees.teamId:
Entity teams has no primary keys generated yet
```

**Cause:** Incorrect dependency order

**Solution:** Check relationships in template:
```json
{
  "relationships": [
    {"from": "employees.teamId", "to": "teams.id"}
  ]
}
```

Ensure "teams" entity is generated before "employees".

### Circular Dependency

**Error:**
```
ValueError: Circular dependency detected in relationships
```

**Cause:** Entities reference each other (e.g., employee.managerId → employee.id)

**Solution:** Break cycle:
1. Remove problematic relationship from template
2. Generate data
3. Manually add self-referencing FKs as update

### PII Not Detected

**Issue:** Real-looking field names not flagged as PII

**Solution:** Manually edit template:
```json
{
  "name": "workEmail",
  "type": "string",
  "pii": true,        # ← Add this
  "faker_method": "email"
}
```

### Unrealistic Data

**Issue:** Generic Faker methods produce boring data

**Solution:** Customize Faker methods:
```json
{
  "name": "industry",
  "faker_method": "random_element",
  "faker_args": {
    "elements": ["Tech", "Finance", "Healthcare", "Retail"]
  }
}
```

---

## Platform-Specific Notes

### Microsoft Fabric

- Use OneLake paths for template storage
- Delta tables for Bronze loading
- Fabric notebooks for generation scripts
- Example: [`utils/mock_data_generator/generate_mock_data_template.py`](../../utils/mock_data_generator/generate_mock_data_template.py)

### Databricks

- Use Unity Catalog for Bronze tables
- DBFS for template storage
- Databricks notebooks (Python or Scala)
- Same utilities work with minor path adjustments

### Snowflake

- Use Snowpark for data generation
- Stages for template/data storage
- Python UDFs for Faker integration

---

## Reference Implementation

See Alexis HR example:

**Spec:** [docs/specs/SDD-20260209-pii-mock-data-generator/spec.md](../specs/SDD-20260209-pii-mock-data-generator/spec.md)

**Source Doc:** `projects/cloud2-azure-dataplatform/docs/sources/alexis.md`

**Template:** `projects/cloud2-azure-dataplatform/docs/templates/alexis/metadata.json` (after generation)

**Entities:**
- Employees (200 rows) - PII: email, firstName, lastName, personalNumber
- Compensation (200 rows) - Confidential: salary
- Departments (5 rows)
- Offices (3 rows)
- Teams (10 rows)

**Relationships:**
```
departments
  ↑
teams ──────────┐
  ↑             │
employees ──────┤
  ↑             │
compensation    │
                ↓
           (FK dependencies)
```

---

## Cross-Domain Shared Person Registry

When multiple domains need to join on person identity in dev/test (e.g. IT requesters = HR employees = Projects team members), use a **shared mock person registry** with stable IDs.

### Problem

Without a shared registry, each domain generates independent random persons — cross-domain joins are impossible. This prevents testing MDM, Lean MDM, and cross-domain analytics in dev.

### Solution: Shared `persons.json`

Create a fixed list of persons (e.g. 40–100) with **stable IDs** (never change). Each domain generator reads this list from its own lakehouse copy.

```
fabric/
├── mdm/                                # MDM domain owns the canonical list
│   └── notebooks/
│       └── util_generate_mock_persons  # Creates persons.json
│           → Files/mock/shared/persons.json
│
├── it/
│   └── notebooks/
│       └── util_generate_mock_data_it  # Reads persons.json, generates IT entities
│
└── projects/
    └── notebooks/
        └── util_generate_mock_data_projects  # Reads persons.json, generates Projects entities
```

### Person Registry Schema

```json
[
  {
    "id": "P001",
    "first_name": "Mikael",
    "last_name": "Virtanen",
    "email": "mikael.virtanen@company.fi",
    "phone": "+358 40 123 4567",
    "department": "Engineering"
  }
]
```

**ID rules:**
- Format: `P{NNN}` with zero-padding (P001, P002 ... P040)
- **Never change existing IDs** — cross-domain joins depend on stability
- Add new persons at the end only

### Domain Mapping Convention

| Domain | Entity | ID Type | Mapping |
|--------|--------|---------|---------|
| IT (Freshservice) | `requesters.id` | int | `int(P001[1:])` → `1` |
| IT (Freshservice) | `agents.id` | int | Same — agents = subset of persons |
| Projects (Koho) | `employees.id` | string | Verbatim `"P001"` |
| HR (Alexis) | `employees.id` | string | Verbatim `"P001"` (planned) |

### Reading in Fabric Notebooks

```python
import json
from notebookutils import mssparkutils

# Read shared registry from own lakehouse Files
persons_raw = mssparkutils.fs.head("Files/mock/shared/persons.json", 1024 * 1024)
PERSONS = json.loads(persons_raw)

# Use persons to generate domain entities
requesters = [
    {
        "id": int(p["id"][1:]),          # P001 → 1
        "first_name": p["first_name"],
        "last_name": p["last_name"],
        "email": p["email"],
        "department_id": dept_id         # FK to departments
    }
    for p in PERSONS
]
```

### Run Order

1. Run `util_generate_mock_persons` (MDM domain) **once** — creates `persons.json`
2. Copy `persons.json` to `Files/mock/shared/` in each domain lakehouse (or re-run util in each)
3. Run domain-specific generators — they read from their local `persons.json`

### When to Use This Pattern

- Multiple domains model the same real-world persons (employees, users, contacts)
- You need cross-domain joins in dev (IT ↔ HR ↔ Projects)
- Building a lean/light MDM layer for person identity

## Related Patterns

- [Environment Separation](../principles/environment-separation.md) - Dev/Test/Prod isolation
- [Security & Privacy](../principles/security-privacy.md) - PII handling
- [Medallion Architecture](../principles/medallion-architecture.md) - Bronze/Silver/Gold layers

---

## Tools and Utilities

| File | Purpose |
|------|---------|
| [`utils/mock_data_generator/metadata_extractor.py`](../../utils/mock_data_generator/metadata_extractor.py) | REST API and SQL metadata extraction |
| [`utils/mock_data_generator/data_generator.py`](../../utils/mock_data_generator/data_generator.py) | Synthetic data generation with FK integrity |
| [`utils/mock_data_generator/generate_mock_data_template.py`](../../utils/mock_data_generator/generate_mock_data_template.py) | Fabric notebook template |
| [`.claude/commands/generate-mock-data.md`](../../.claude/commands/generate-mock-data.md) | Interactive skill |

---

**Pattern Owner:** Data AI Agents Team
**Last Updated:** 2026-02-09
**Version:** 1.0
