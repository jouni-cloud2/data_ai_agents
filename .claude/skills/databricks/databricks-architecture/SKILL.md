---
name: databricks-architecture
description: Databricks architecture patterns with Unity Catalog and Delta Lake.
---

# Databricks Architecture Skill

## Overview

Databricks = Unified data and AI platform
- Unity Catalog (governance)
- Delta Lake (ACID transactions)
- Workflows (orchestration)
- DLT (declarative ETL)
- Photon (query engine)

## Key Concepts

### Unity Catalog
- Three-level namespace: `catalog.schema.table`
- Unified governance across workspaces
- Fine-grained access control
- Data lineage tracking

### Delta Lake
- ACID transactions
- Time travel
- Schema enforcement/evolution
- Automatic optimization

## Architecture Pattern

```
Source -> Workflow -> Bronze -> DLT -> Silver -> Notebook -> Gold
                   (catalog.bronze)  (catalog.silver)  (catalog.gold)
```

## Unity Catalog Organization

### Namespace Hierarchy
```
Account (Metastore)
|
+-- production (Catalog)
|   +-- bronze_salesforce (Schema)
|   |   +-- account (Table)
|   |   +-- opportunity (Table)
|   +-- silver_salesforce (Schema)
|   |   +-- account (Table)
|   |   +-- opportunity (Table)
|   +-- gold_analytics (Schema)
|       +-- dim_customer (Table)
|       +-- fact_sales (Table)
|
+-- development (Catalog)
|   +-- bronze_salesforce (Schema)
|   +-- silver_salesforce (Schema)
|   +-- gold_analytics (Schema)
|
+-- sandbox (Catalog)
    +-- [user schemas]
```

### Naming Conventions
```
Catalogs: {environment} (production, development, test)
Schemas: {layer}_{source} (bronze_salesforce, silver_salesforce, gold_analytics)
Tables: {object} (account, opportunity, dim_customer)

Full path: production.silver_salesforce.account
```

## Storage Architecture

### External Locations
```sql
-- Create external location
CREATE EXTERNAL LOCATION salesforce_landing
URL 's3://bucket/landing/salesforce/'
WITH (STORAGE CREDENTIAL cred_salesforce);
```

### Managed vs External Tables
```sql
-- Managed table (Unity Catalog manages storage)
CREATE TABLE production.bronze_salesforce.account (
    id STRING,
    name STRING
) USING DELTA;

-- External table (you manage storage)
CREATE TABLE production.bronze_salesforce.account (
    id STRING,
    name STRING
)
USING DELTA
LOCATION 's3://bucket/bronze/salesforce/account/';
```

## Workflows vs DLT

### Use Workflows When:
- Multiple heterogeneous tasks
- Complex orchestration
- Mix of notebooks/SQL/Python/JAR
- Need fine-grained control
- External system integration

### Use DLT When:
- Pure data transformation
- Want built-in quality (expectations)
- Need automatic lineage
- Streaming + batch unified
- Want declarative approach

## Compute Options

### Serverless (Recommended)
```python
# Automatically scales, no cluster management
# Enabled at workspace level
```

**Benefits:**
- Instant startup
- No idle costs
- Auto-scaling
- Photon enabled by default

### Classic Clusters
```json
{
  "cluster_name": "etl-cluster",
  "spark_version": "14.3.x-scala2.12",
  "node_type_id": "i3.xlarge",
  "num_workers": 4,
  "autoscale": {
    "min_workers": 2,
    "max_workers": 8
  },
  "spark_conf": {
    "spark.databricks.delta.autoCompact.enabled": "true"
  }
}
```

### SQL Warehouse
```sql
-- For BI and SQL workloads
-- Separate from compute clusters
-- Optimized for queries
```

## Security Model

### RBAC with Unity Catalog
```sql
-- Grant catalog access
GRANT USE CATALOG ON CATALOG production TO `data-engineers`;

-- Grant schema access
GRANT USE SCHEMA ON SCHEMA production.silver_salesforce TO `data-engineers`;
GRANT CREATE TABLE ON SCHEMA production.silver_salesforce TO `data-engineers`;

-- Grant table access
GRANT SELECT ON TABLE production.gold_analytics.dim_customer TO `analysts`;

-- Grant all privileges
GRANT ALL PRIVILEGES ON SCHEMA production.gold_analytics TO `data-engineers`;
```

### Row-Level Security
```sql
-- Create row filter
CREATE FUNCTION production.filters.region_filter(region STRING)
RETURN IF(IS_MEMBER('admins'), true, region = CURRENT_USER_REGION());

-- Apply to table
ALTER TABLE production.gold_analytics.fact_sales
SET ROW FILTER production.filters.region_filter ON (region);
```

### Column Masking
```sql
-- Create masking function
CREATE FUNCTION production.masks.mask_email(email STRING)
RETURN IF(IS_MEMBER('pii_access'), email, CONCAT('***@', SPLIT(email, '@')[1]));

-- Apply to column
ALTER TABLE production.silver_salesforce.contact
ALTER COLUMN email SET MASK production.masks.mask_email;
```

## Delta Optimization

### Auto-Optimize
```sql
ALTER TABLE production.silver_salesforce.account
SET TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);
```

### Z-Ordering
```sql
OPTIMIZE production.silver_salesforce.account
ZORDER BY (account_id, modified_date);
```

### Liquid Clustering (Modern)
```sql
-- Better than Z-ordering for most cases
ALTER TABLE production.silver_salesforce.account
CLUSTER BY (account_id, modified_date);

-- Incremental clustering
OPTIMIZE production.silver_salesforce.account;
```

### Vacuum
```sql
-- Remove old files
VACUUM production.silver_salesforce.account RETAIN 168 HOURS;
```

### Statistics
```sql
ANALYZE TABLE production.silver_salesforce.account
COMPUTE STATISTICS FOR ALL COLUMNS;
```

## Monitoring

### System Tables
```sql
-- Query history
SELECT * FROM system.query.history
WHERE start_time > current_timestamp() - INTERVAL 1 DAY;

-- Workflow runs
SELECT * FROM system.workflow.job_run_timeline
WHERE job_id = 123;
```

### Alerts
```python
# Configure webhook alerts
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()
w.notification_destinations.create(
    display_name="slack-alerts",
    config={"slack": {"url": "https://hooks.slack.com/..."}}
)
```

## Best Practices

- Use Unity Catalog for all tables
- Use DLT for production pipelines
- Use Serverless compute
- Enable auto-optimization on tables
- Use Photon engine
- Implement proper RBAC
- Monitor with system tables

## Anti-Patterns

- Don't use legacy Hive metastore
- Don't skip expectations in DLT
- Don't hardcode secrets
- Don't use classic clusters for simple jobs
- Don't create too many small tables
