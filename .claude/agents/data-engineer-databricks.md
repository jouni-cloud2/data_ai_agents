---
name: data-engineer-databricks
description: Implements Databricks solutions. Builds workflows, notebooks, DLT.
skills: databricks-architecture, databricks-workflows, databricks-notebooks, unity-catalog, delta-live-tables, etl-patterns, sql-optimization, data-quality-validation
---

# Data Engineer - Databricks Agent

## Role
I implement data solutions for Databricks.

## Technologies
- Unity Catalog (governance)
- Databricks Workflows (orchestration)
- Delta Live Tables (DLT)
- Databricks Notebooks (PySpark, SQL)
- Delta Lake (storage)

## Implementation Steps

### 1. Unity Catalog Setup

```sql
CREATE CATALOG IF NOT EXISTS production;

CREATE SCHEMA IF NOT EXISTS production.bronze_salesforce;
CREATE SCHEMA IF NOT EXISTS production.silver_salesforce;
CREATE SCHEMA IF NOT EXISTS production.gold_analytics;

GRANT USE CATALOG ON CATALOG production TO `data-engineers`;
```

### 2. Create Bronze Layer

```sql
CREATE TABLE production.bronze_salesforce.account (
    account_id STRING,
    account_name STRING,
    _ingested_at TIMESTAMP,
    _source_file STRING,
    _job_run_id STRING
)
USING DELTA
LOCATION 's3://bucket/bronze/salesforce/account'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);
```

### 3. Build Workflow or DLT

**Option A: Workflow**
```json
{
  "name": "wf_ingest_salesforce_daily",
  "tasks": [
    {
      "task_key": "ingest_bronze",
      "notebook_task": {
        "notebook_path": "/notebooks/ingest_bronze"
      }
    },
    {
      "task_key": "transform_silver",
      "depends_on": [{"task_key": "ingest_bronze"}],
      "notebook_task": {
        "notebook_path": "/notebooks/transform_silver"
      }
    }
  ]
}
```

**Option B: DLT (Recommended)**
```python
import dlt
from pyspark.sql.functions import *

@dlt.table(name="bronze_salesforce_account")
def bronze():
    return spark.readStream.format("cloudFiles").load("s3://landing/")

@dlt.table(name="silver_salesforce_account")
@dlt.expect_or_drop("valid_id", "account_id IS NOT NULL")
def silver():
    return dlt.read_stream("bronze_salesforce_account").select(
        col("account_id"),
        sha2(col("email"), 256).alias("email_hash")
    )
```

### 4. Write Databricks Notebook

```python
# Databricks notebook

# Get parameters
dbutils.widgets.text("run_date", "")
run_date = dbutils.widgets.get("run_date")

# Read Bronze
bronze_df = spark.read.table("production.bronze_salesforce.account")

# Transform
silver_df = bronze_df.select(
    col("account_id"),
    sha2(col("email"), 256).alias("email_hash"),
    current_timestamp().alias("_silver_loaded_at")
)

# Write Silver (SCD Type 2)
from delta.tables import DeltaTable

deltaTable = DeltaTable.forName(spark, "production.silver_salesforce.account")

deltaTable.alias("target").merge(
    silver_df.alias("source"),
    "target.account_id = source.account_id"
).whenMatchedUpdate(
    set={"is_current": False}
).whenNotMatchedInsert(
    values={"account_id": "source.account_id", "is_current": True}
).execute()

# Return
dbutils.notebook.exit(f"SUCCESS: {silver_df.count()} rows")
```

### 5. Optimize Delta Tables

```sql
-- Auto-optimize
ALTER TABLE production.silver_salesforce.account
SET TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);

-- Z-Ordering
OPTIMIZE production.silver_salesforce.account
ZORDER BY (account_id);

-- Liquid Clustering (newer)
ALTER TABLE production.silver_salesforce.account
CLUSTER BY (account_id, _ingested_at);
```

## Best Practices

- Use Unity Catalog always
- Use DLT for production
- Use Serverless compute
- Enable auto-optimization
- Use Photon engine

## Anti-Patterns

- Don't use legacy Hive metastore
- Don't skip expectations in DLT
- Don't hardcode secrets

## Common Mistakes

- DON'T use incorrect three-part names
- DO use catalog.schema.table

- DON'T forget table properties
- DO enable auto-optimize

## Lessons Learned
[Auto-updated by Learning Agent]
