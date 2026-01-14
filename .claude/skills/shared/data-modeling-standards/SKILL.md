---
name: data-modeling-standards
description: Medallion architecture patterns. Platform-agnostic principles.
---

# Data Modeling Standards Skill

## Medallion Architecture

```
Bronze (Raw) -> Silver (Cleaned) -> Gold (Business)
```

### Bronze Layer
**Purpose**: Raw data as-is

**Characteristics:**
- Immutable (append-only)
- Exact copy from source
- Minimal transformation

**Metadata Columns (REQUIRED):**
```sql
_ingested_at TIMESTAMP      -- When ingested
_source_file STRING         -- Source file/API
_pipeline_run_id STRING     -- Pipeline/workflow ID
```

**Naming:**
- Fabric: `bronze_<source>_<object>`
- Databricks: `bronze.<source>.<object>`

### Silver Layer
**Purpose**: Cleaned, validated

**Characteristics:**
- Strongly typed
- PII masked
- Quality validated
- SCD Type 2

**Metadata Columns:**
```sql
_silver_loaded_at TIMESTAMP
_data_quality_score FLOAT
```

**Naming:**
- Fabric: `silver_<source>_<object>`
- Databricks: `silver.<source>.<object>`

### Gold Layer
**Purpose**: Business-ready

**Characteristics:**
- Star schema
- Business KPIs
- Denormalized
- Optimized

**Naming:**
- Dimensions: `gold_dim_<entity>`
- Facts: `gold_fact_<process>`

## Universal Naming

### Tables
`{layer}_{source}_{object}`

### Columns
- Use `snake_case`
- Dates: `<name>_date` or `<name>_datetime`
- Booleans: `is_<condition>` or `has_<attribute>`
- Keys: `<table>_key` or `<entity>_id`

### Reserved Prefixes
- `_` for system/metadata only
- Never `_` for business columns

## SCD Type 2 (Universal)

```sql
CREATE TABLE [path] (
    -- Business key
    account_id STRING,

    -- Attributes
    account_name STRING,

    -- SCD Type 2
    is_current BOOLEAN,
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,

    -- Surrogate
    account_key BIGINT
)
```

## Templates

### Dimension Template
```sql
CREATE TABLE [path].dim_<entity> (
    -- Surrogate key
    <entity>_key BIGINT,

    -- Business key
    <entity>_id STRING,

    -- Attributes
    <entity>_name STRING,
    -- ... other attributes

    -- SCD Type 2
    is_current BOOLEAN,
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,

    -- Metadata
    _loaded_at TIMESTAMP
)
```

### Fact Template
```sql
CREATE TABLE [path].fact_<process> (
    -- Fact key
    <process>_id STRING,

    -- Foreign keys
    <entity1>_key BIGINT,
    <entity2>_key BIGINT,
    date_key INT,

    -- Measures
    quantity INT,
    amount DECIMAL(18,2),

    -- Metadata
    _loaded_at TIMESTAMP
)
```

### Date Dimension Template
```sql
CREATE TABLE [path].dim_date (
    date_key INT,
    full_date DATE,
    day_of_week INT,
    day_name STRING,
    day_of_month INT,
    day_of_year INT,
    week_of_year INT,
    month_number INT,
    month_name STRING,
    quarter INT,
    year INT,
    is_weekend BOOLEAN,
    is_holiday BOOLEAN,
    fiscal_year INT,
    fiscal_quarter INT
)
```

## Star Schema Best Practices

### Dimension Tables
- Use surrogate keys (BIGINT)
- Include business keys for lookups
- Support SCD Type 2 for history
- Denormalize for query performance

### Fact Tables
- Foreign keys to dimensions
- Grain should be clear
- Measures should be additive
- Include date keys for partitioning

### Relationships
- One-to-many from dimension to fact
- Dimension keys are integers
- Facts reference dimension keys

## Data Types

### Standard Mappings
| Source Type | Bronze | Silver | Gold |
|-------------|--------|--------|------|
| String | STRING | STRING | STRING |
| Integer | STRING | INT/BIGINT | INT/BIGINT |
| Decimal | STRING | DECIMAL | DECIMAL |
| Date | STRING | DATE | DATE |
| Timestamp | STRING | TIMESTAMP | TIMESTAMP |
| Boolean | STRING | BOOLEAN | BOOLEAN |

### Best Practices
- Bronze: Keep as STRING for flexibility
- Silver: Apply proper types
- Gold: Business-appropriate types

## Quality Gates

### Bronze -> Silver
- Not null validation
- Type conversion success
- Deduplication
- PII masking

### Silver -> Gold
- Business rule validation
- Referential integrity
- Calculation validation
- Completeness check
