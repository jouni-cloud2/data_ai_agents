# Generate Mock Data

Generate synthetic data for PII-containing sources without test environments.

**Usage:** `/generate-mock-data <source-name>`

**Example:** `/generate-mock-data alexis`

---

## What This Command Does

This command helps you safely develop data pipelines for sources with PII by:

1. **Option A: Extract metadata first**
   - Connects to production API/database (read-only)
   - Extracts schema metadata (entities, fields, types, relationships)
   - Saves metadata template to `projects/<project>/docs/templates/<source>/metadata.json`
   - Generates synthetic data based on template
   - Loads to dev Bronze tables

2. **Option B: Use existing template**
   - Loads previously saved metadata template
   - Generates fresh synthetic data
   - Loads to dev Bronze tables

---

## Prerequisites

- Source system documentation in `projects/<project>/docs/sources/<source>.md`
- For REST APIs: API credentials in Azure Key Vault
- For SQL: JDBC connection string in Key Vault
- Running in **dev environment only** (compliance requirement)

---

## Process

### Step 1: Detect Project and Source

You invoked: `/generate-mock-data {ARG}`

First, let me detect your project context and source:

1. Check current working directory for project
2. Look for source documentation at `projects/<project>/docs/sources/{ARG}.md`
3. Determine source type (REST API, SQL, SaaS platform)

**If source doc not found:**
- Prompt user to confirm source name
- Ask user to specify source type manually

### Step 2: Choose Workflow

Ask user:

```
Found source: {source_name} ({source_type})

Choose workflow:
1. Extract metadata first (calls production API to build template)
2. Use existing template (skip extraction)

Enter choice (1 or 2):
```

### Step 3A: Extract Metadata (If Choice 1)

For REST API sources:

1. **Get credentials:**
   - Ask for Key Vault name (default: detect from project)
   - Ask for API token secret name
   - Retrieve token from Key Vault

2. **Extract schema:**
   - For each endpoint in source doc:
     - Call API with limit=1 to get sample
     - Infer field types, detect PII fields, detect FKs
     - Ask user to confirm PII fields and FK relationships

3. **Configure row counts:**
   - Default row counts per entity
   - Ask if user wants to customize

4. **Save template:**
   - Save to `projects/<project>/docs/templates/{source}/metadata.json`
   - Show saved path

For SQL sources:

1. **Get connection:**
   - Ask for connection string or Key Vault secret
   - Ask for schema name

2. **Extract schema:**
   - Query INFORMATION_SCHEMA.COLUMNS
   - Query INFORMATION_SCHEMA.KEY_COLUMN_USAGE for FKs
   - Auto-detect PII by field name patterns

3. **Save template:**
   - Same as REST API

### Step 3B: Use Existing Template (If Choice 2)

1. **List available templates:**
   ```
   Available templates in projects/<project>/docs/templates/:
   - alexis/metadata.json (extracted 2026-02-09)
   - hubspot/metadata.json (extracted 2026-01-15)

   Select template (enter name or number):
   ```

2. **Load template:**
   - Read JSON file
   - Display summary (entities, row counts)

3. **Ask for confirmation:**
   ```
   Template: alexis
   Entities:
     - employees: 200 rows
     - compensation: 200 rows
     - departments: 5 rows
     - offices: 3 rows
     - teams: 10 rows

   Proceed with data generation? (yes/no)
   ```

### Step 4: Generate Synthetic Data

1. **Create generation script:**
   - Copy `utils/mock_data_generator/generate_mock_data_template.py`
   - Adapt for this source
   - Save to project: `projects/<project>/scripts/generate_mock_{source}.py`

2. **Execute generation:**
   - Use the Python utilities to generate data
   - Show progress for each entity
   - Display FK relationship preservation

3. **Save generated data:**
   - For Fabric: Write to dev Bronze Delta tables
   - For local: Save as JSON/Parquet files

### Step 5: Verification

1. **Data Quality Checks:**
   ```
   ✓ Generated 200 employees
   ✓ Generated 200 compensation records
   ✓ FK integrity: All compensation.employeeId exist in employees.id
   ✓ FK integrity: All employees.teamId exist in teams.id
   ✓ No duplicate primary keys
   ```

2. **Show Bronze tables created:**
   ```
   Created dev Bronze tables:
   - bronze_alexis_employees (200 rows)
   - bronze_alexis_compensation (200 rows)
   - bronze_alexis_departments (5 rows)
   - bronze_alexis_offices (3 rows)
   - bronze_alexis_teams (10 rows)
   ```

3. **Next steps:**
   ```
   Mock data generation complete!

   Next steps:
   1. Review generated data in Bronze tables
   2. Develop Silver transformation notebooks
   3. Test your pipeline end-to-end with mock data

   Template saved: projects/<project>/docs/templates/{source}/metadata.json
   Generation script: projects/<project>/scripts/generate_mock_{source}.py

   To regenerate data later: /generate-mock-data {source}
   ```

---

## Implementation Details

### Source Type Detection

From source documentation file, look for:

| Pattern | Source Type |
|---------|-------------|
| `Base URL: https://api.` | REST API |
| `JDBC:` or `Connection String:` | SQL Database |
| `Salesforce`, `Snowflake`, etc. | SaaS Platform |

### REST API Extraction

```python
from utils.mock_data_generator import RestApiExtractor, MetadataTemplate

# Initialize extractor
extractor = RestApiExtractor(
    base_url="https://api.alexishr.com/v1",
    api_token=api_token
)

# Create template
template = MetadataTemplate(
    source="alexis",
    source_type="rest_api",
    base_url="https://api.alexishr.com/v1"
)

# Extract entities
for endpoint in ["/employee", "/compensation", "/department", "/office", "/team"]:
    entity = extractor.extract_entity(
        endpoint=endpoint,
        entity_name=endpoint.strip('/') + 's',
        bronze_table=f"bronze_alexis_{endpoint.strip('/')}s",
        row_count=200  # configurable
    )
    template.add_entity(entity)

# Save template
template.save("projects/<project>/docs/templates/alexis/metadata.json")
```

### Data Generation

```python
from utils.mock_data_generator import MetadataTemplate, SyntheticDataGenerator

# Load template
template = MetadataTemplate.load("path/to/metadata.json")

# Generate data
generator = SyntheticDataGenerator(template, seed=42)
data = generator.generate_all()

# Verify
summary = generator.get_summary()
print(summary)
```

### Bronze Loading (Fabric)

```python
from pyspark.sql.functions import current_timestamp, lit

for entity_name, records in data.items():
    # Create DataFrame
    df = spark.createDataFrame(records)

    # Add metadata
    df = df.withColumn("_ingested_at", current_timestamp())
    df = df.withColumn("_source_system", lit(f"{source}_mock"))

    # Write to Bronze
    bronze_table = f"bronze_{source}_{entity_name}"
    df.write.format("delta").mode("overwrite").saveAsTable(bronze_table)
```

---

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| API 401/403 | Invalid credentials | Verify Key Vault secret, check API key permissions |
| FK reference not found | Incorrect FK mapping | Manually edit template to fix relationships |
| Circular dependency | Circular FK | Break cycle in template (e.g., mark one FK as nullable) |
| Environment not 'dev' | Compliance check failed | Only run in dev environment |

### Compliance Safeguards

1. **Environment Check:**
   - Script validates `environment == 'dev'`
   - Fails with error if not dev

2. **No Production Data:**
   - Metadata extraction reads schema only (limit=1 sample)
   - No actual production data stored
   - Generated data is purely synthetic

3. **Audit Trail:**
   - Template includes `extracted_at` timestamp
   - Bronze tables have `_source_system` = `{source}_mock` tag

---

## Arguments

**Required:**
- `<source-name>`: Name of the source system (e.g., 'alexis', 'hubspot')

**Optional Flags** (future enhancement):
- `--extract`: Force metadata extraction
- `--template <path>`: Specify custom template path
- `--output <path>`: Specify custom output path

---

## Related Documentation

- [Spec: SDD-20260209-pii-mock-data-generator](../../docs/specs/SDD-20260209-pii-mock-data-generator/spec.md)
- [Pattern: PII Mock Data Generation](../../docs/patterns/pii-mock-data-generation.md)
- [Environment Separation](../../docs/principles/environment-separation.md)
- [Security & Privacy](../../docs/principles/security-privacy.md)

---

**Author:** Data AI Agents Team
**Last Updated:** 2026-02-09
