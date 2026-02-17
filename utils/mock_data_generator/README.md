# PII Mock Data Generator Utilities

Python utilities for extracting metadata from PII sources and generating synthetic data for development environments.

## Overview

This package provides tools for the [PII Mock Data Generation Pattern](../../docs/patterns/pii-mock-data-generation.md):

1. **Metadata Extraction** - Extract schema from REST APIs, SQL databases, or SaaS platforms
2. **Synthetic Data Generation** - Generate fake data preserving referential integrity
3. **Dev Loading** - Load to development Bronze tables

## Installation

```bash
# Install dependencies
pip install -r requirements.txt
```

Requirements:
- Python 3.8+
- `faker>=20.0.0`
- `requests>=2.31.0`

## Quick Start

### 1. Extract Metadata from REST API

```python
from mock_data_generator import RestApiExtractor, MetadataTemplate

# Initialize extractor
extractor = RestApiExtractor(
    base_url="https://api.alexishr.com/v1",
    api_token="your-api-token"
)

# Create template
template = MetadataTemplate(
    source="alexis",
    source_type="rest_api",
    base_url="https://api.alexishr.com/v1"
)

# Extract entities
employee_entity = extractor.extract_entity(
    endpoint="/employee",
    entity_name="employees",
    bronze_table="bronze_alexis_employees",
    row_count=200
)
template.add_entity(employee_entity)

# Add relationships
from mock_data_generator.metadata_extractor import Relationship
template.add_relationship(
    Relationship("employees.teamId", "teams.id")
)

# Save template
template.save("metadata_alexis.json")
```

### 2. Generate Synthetic Data

```python
from mock_data_generator import MetadataTemplate, SyntheticDataGenerator

# Load template
template = MetadataTemplate.load("metadata_alexis.json")

# Generate data
generator = SyntheticDataGenerator(template, seed=42)
data = generator.generate_all()

# Get summary
summary = generator.get_summary()
print(summary)
# Output: {'employees': 200, 'teams': 10, ...}

# Access entity data
employees = generator.get_entity_data("employees")
print(f"Generated {len(employees)} employees")
```

### 3. Export Data

```python
# Export as JSON
json_data = generator.export_to_json()

# Export as dictionary
data_dict = generator.export_to_dict()

# Save individual entities
import json
for entity_name, records in data_dict.items():
    with open(f"{entity_name}.json", 'w') as f:
        json.dump(records, f, indent=2, default=str)
```

## API Reference

### `RestApiExtractor`

Extract metadata from REST APIs.

**Constructor:**
```python
RestApiExtractor(base_url: str, api_token: str)
```

**Methods:**

#### `extract_entity()`
```python
extract_entity(
    endpoint: str,
    entity_name: str,
    bronze_table: str,
    row_count: int = 100,
    query_params: Optional[Dict[str, Any]] = None
) -> EntityMetadata
```

Extract metadata for a single API endpoint.

**Parameters:**
- `endpoint`: API path (e.g., "/employee")
- `entity_name`: Entity name (e.g., "employees")
- `bronze_table`: Target Bronze table name
- `row_count`: Desired row count for synthetic data
- `query_params`: Optional query parameters

**Returns:** `EntityMetadata` object

**Example:**
```python
entity = extractor.extract_entity(
    endpoint="/employee",
    entity_name="employees",
    bronze_table="bronze_alexis_employees",
    row_count=200,
    query_params={"limit": 1, "relations": "teamReference"}
)
```

---

### `MetadataTemplate`

Container for source metadata.

**Constructor:**
```python
MetadataTemplate(
    source: str,
    source_type: str,
    base_url: Optional[str] = None,
    database_name: Optional[str] = None
)
```

**Attributes:**
- `source`: Source name (e.g., "alexis")
- `source_type`: Type ("rest_api", "sql", "saas")
- `base_url`: API base URL (for REST APIs)
- `database_name`: Database name (for SQL)
- `entities`: List of `EntityMetadata`
- `relationships`: List of `Relationship`

**Methods:**

#### `add_entity()`
```python
add_entity(entity: EntityMetadata)
```

Add an entity to the template.

#### `add_relationship()`
```python
add_relationship(relationship: Relationship)
```

Add a FK relationship.

**Example:**
```python
from mock_data_generator.metadata_extractor import Relationship
template.add_relationship(
    Relationship("employees.teamId", "teams.id")
)
```

#### `save()`
```python
save(file_path: str)
```

Save template to JSON file.

#### `load()` (classmethod)
```python
MetadataTemplate.load(file_path: str) -> MetadataTemplate
```

Load template from JSON file.

---

### `SyntheticDataGenerator`

Generate synthetic data from templates.

**Constructor:**
```python
SyntheticDataGenerator(template: MetadataTemplate, seed: Optional[int] = None)
```

**Parameters:**
- `template`: MetadataTemplate to generate from
- `seed`: Random seed for reproducibility

**Methods:**

#### `generate_all()`
```python
generate_all() -> Dict[str, List[Dict[str, Any]]]
```

Generate data for all entities in dependency order.

**Returns:** Dictionary mapping entity names to record lists

**Example:**
```python
generator = SyntheticDataGenerator(template, seed=42)
data = generator.generate_all()
```

#### `get_entity_data()`
```python
get_entity_data(entity_name: str) -> List[Dict[str, Any]]
```

Get generated data for a specific entity.

#### `get_summary()`
```python
get_summary() -> Dict[str, int]
```

Get summary of record counts per entity.

#### `export_to_json()`
```python
export_to_json() -> str
```

Export all data as JSON string.

#### `export_to_dict()`
```python
export_to_dict() -> Dict[str, List[Dict[str, Any]]]
```

Export all data as dictionary.

---

### Data Classes

#### `FieldMetadata`

```python
@dataclass
class FieldMetadata:
    name: str
    type: str
    pii: bool = False
    primary_key: bool = False
    foreign_key: Optional[str] = None
    faker_method: Optional[str] = None
    faker_args: Optional[Dict[str, Any]] = None
```

#### `EntityMetadata`

```python
@dataclass
class EntityMetadata:
    name: str
    api_endpoint: Optional[str] = None
    table_name: Optional[str] = None
    bronze_table: Optional[str] = None
    row_count: int = 100
    fields: List[FieldMetadata] = None
```

#### `Relationship`

```python
@dataclass
class Relationship:
    from_field: str  # e.g., "employees.teamId"
    to_field: str    # e.g., "teams.id"
```

---

## Faker Method Reference

Common Faker methods used in templates:

| Field Type | Faker Method | Example Output |
|------------|--------------|----------------|
| `id` / UUID | `uuid4` | `a1b2c3d4-e5f6-...` |
| `email` | `email` | `john@example.com` |
| `firstName` | `first_name` | `John` |
| `lastName` | `last_name` | `Doe` |
| `name` | `name` | `John Doe` |
| `phone` | `phone_number` | `+1-555-123-4567` |
| `ssn` / `personalNumber` | `ssn` | `123-45-6789` |
| `address` | `address` | `123 Main St` |
| `city` | `city` | `New York` |
| `country` | `country` | `United States` |
| `company` | `company` | `Acme Corp` |
| `job` | `job` | `Software Engineer` |
| `url` | `url` | `https://example.com` |
| `date` | `date` | `2026-02-09` |
| `datetime` | `date_time` | `2026-02-09 14:30:00` |
| Salary | `random_int(min=30000, max=150000)` | `75000` |
| Currency | `currency_code` | `USD` |
| Industry | `random_element(elements=["Tech", ...])` | `Tech` |

Full documentation: [Faker Providers](https://faker.readthedocs.io/en/master/providers.html)

---

## Examples

### Complete Example: Alexis HR

See [docs/specs/SDD-20260209-pii-mock-data-generator/examples/](../../docs/specs/SDD-20260209-pii-mock-data-generator/examples/)

**Files:**
- `alexis-metadata-template.json` - Example metadata template
- `generate_alexis_mock_data.py` - Example generation script

**Run:**
```bash
cd docs/specs/SDD-20260209-pii-mock-data-generator/examples
python generate_alexis_mock_data.py
```

**Output:**
```
ALEXIS HR MOCK DATA GENERATION
==================================================

Step 1: Loading metadata template...
  ✓ Loaded template for source: alexis
  ✓ Entities: 5
  ✓ Relationships: 5

Step 2: Generating synthetic data...
Generating 5 records for departments...
  ✓ Generated 5 records
Generating 3 records for offices...
  ✓ Generated 3 records
Generating 10 records for teams...
  ✓ Generated 10 records
Generating 200 records for employees...
  ✓ Generated 200 records
Generating 200 records for compensation...
  ✓ Generated 200 records

Step 3: Verifying data integrity...
  ✓ All teams.departmentId exist in departments.id
  ✓ All employees.teamId exist in teams.id
  ✓ All employees.departmentId exist in departments.id
  ✓ All employees.officeId exist in offices.id
  ✓ All compensation.employeeId exist in employees.id

Step 4: Saving data...
  ✓ Saved 5 records to ./output/departments.json
  ✓ Saved 3 records to ./output/offices.json
  ✓ Saved 10 records to ./output/teams.json
  ✓ Saved 200 records to ./output/employees.json
  ✓ Saved 200 records to ./output/compensation.json
```

---

## Fabric Integration

### Load to Bronze Tables

```python
from pyspark.sql.functions import current_timestamp, lit

# Assuming 'generator' has generated data
data = generator.export_to_dict()

for entity_name, records in data.items():
    # Create DataFrame
    df = spark.createDataFrame(records)

    # Add metadata columns
    df = df.withColumn("_ingested_at", current_timestamp())
    df = df.withColumn("_source_system", lit("alexis_mock"))
    df = df.withColumn("_environment", lit("dev"))

    # Write to Bronze
    bronze_table = f"bronze_alexis_{entity_name}"
    df.write.format("delta").mode("overwrite").saveAsTable(bronze_table)

    print(f"✓ Loaded {len(records)} records to {bronze_table}")
```

### Notebook Template

See [generate_mock_data_template.py](generate_mock_data_template.py) for a complete Fabric notebook template.

---

## Troubleshooting

### Import Errors

**Error:** `ModuleNotFoundError: No module named 'faker'`

**Solution:**
```bash
pip install -r requirements.txt
```

### API Authentication Failures

**Error:** `401 Unauthorized`

**Solution:**
- Verify API token is correct
- Check token has required permissions
- For Fabric, verify Key Vault access

### FK Violations

**Error:** `ValueError: Cannot generate FK for employees.teamId`

**Solution:**
- Ensure referenced entity exists in template
- Check relationships are correctly defined
- Verify dependency order (use topological sort)

### Circular Dependencies

**Error:** `ValueError: Circular dependency detected`

**Solution:**
- Review relationships in template
- Break circular dependencies by removing one FK
- Generate self-referencing FKs separately as update

---

## Testing

Run tests (if available):

```bash
python -m pytest tests/
```

Validate a template:

```python
from mock_data_generator import MetadataTemplate

template = MetadataTemplate.load("metadata.json")
print(f"Entities: {len(template.entities)}")
print(f"Relationships: {len(template.relationships)}")
```

---

## Related Documentation

- [PII Mock Data Generation Pattern](../../docs/patterns/pii-mock-data-generation.md)
- [Spec: SDD-20260209-pii-mock-data-generator](../../docs/specs/SDD-20260209-pii-mock-data-generator/spec.md)
- [Claude Code Skill: /generate-mock-data](../../.claude/commands/generate-mock-data.md)
- [Environment Separation](../../docs/principles/environment-separation.md)

---

## License

Part of the Data AI Agents toolkit.

## Contributing

This is a reference implementation. Adapt to your needs.

---

**Last Updated:** 2026-02-09
**Version:** 1.0.0
