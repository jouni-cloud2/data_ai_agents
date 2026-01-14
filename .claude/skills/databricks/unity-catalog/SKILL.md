---
name: unity-catalog
description: Unity Catalog governance patterns for Databricks.
---

# Unity Catalog Skill

## Overview

Unity Catalog provides unified governance for all data assets:
- Data discovery and lineage
- Fine-grained access control
- Audit logging
- Cross-workspace data sharing

## Namespace Hierarchy

```
Metastore (Account level)
|
+-- Catalog (Environment/Domain)
    |
    +-- Schema (Layer/Source)
        |
        +-- Table/View/Function
```

### Three-Part Names
```sql
-- Always use full path
SELECT * FROM catalog.schema.table

-- Examples
SELECT * FROM production.silver_salesforce.account
SELECT * FROM development.bronze_sap.customer
SELECT * FROM production.gold_analytics.dim_customer
```

## Catalog Management

### Create Catalog
```sql
-- Create catalog
CREATE CATALOG IF NOT EXISTS production;

-- Set default catalog
USE CATALOG production;

-- Describe catalog
DESCRIBE CATALOG production;

-- Drop catalog
DROP CATALOG development CASCADE;
```

### Catalog Properties
```sql
-- Add comment
ALTER CATALOG production SET COMMENT 'Production data catalog';

-- Add tags
ALTER CATALOG production SET TAGS ('environment' = 'prod', 'owner' = 'data-team');
```

## Schema Management

### Create Schema
```sql
-- Create schema in current catalog
CREATE SCHEMA IF NOT EXISTS bronze_salesforce;

-- Create schema in specific catalog
CREATE SCHEMA IF NOT EXISTS production.bronze_salesforce;

-- Create with location
CREATE SCHEMA production.bronze_salesforce
MANAGED LOCATION 's3://bucket/production/bronze/salesforce/';

-- Use schema
USE SCHEMA production.bronze_salesforce;
```

### Schema Properties
```sql
-- Add comment
ALTER SCHEMA production.bronze_salesforce
SET COMMENT 'Raw Salesforce data';

-- Add tags
ALTER SCHEMA production.bronze_salesforce
SET TAGS ('source' = 'salesforce', 'layer' = 'bronze');
```

## Table Management

### Managed Tables
```sql
-- Create managed table (Unity Catalog manages storage)
CREATE TABLE production.bronze_salesforce.account (
    account_id STRING NOT NULL,
    account_name STRING,
    email STRING,
    created_date DATE,
    _ingested_at TIMESTAMP,
    _source_file STRING
)
USING DELTA
COMMENT 'Raw Salesforce accounts'
TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);
```

### External Tables
```sql
-- Create external table (you manage storage)
CREATE TABLE production.bronze_salesforce.account (
    account_id STRING,
    account_name STRING
)
USING DELTA
LOCATION 's3://bucket/bronze/salesforce/account/'
COMMENT 'Raw Salesforce accounts';
```

### Table Properties
```sql
-- Add column comments
ALTER TABLE production.bronze_salesforce.account
ALTER COLUMN account_id COMMENT 'Salesforce Account ID';

-- Add tags
ALTER TABLE production.bronze_salesforce.account
SET TAGS ('pii' = 'true', 'retention' = '7years');

-- Add constraints
ALTER TABLE production.silver_salesforce.account
ADD CONSTRAINT pk_account PRIMARY KEY (account_id);
```

## Access Control

### Grant Privileges
```sql
-- Catalog level
GRANT USE CATALOG ON CATALOG production TO `data-engineers`;
GRANT CREATE SCHEMA ON CATALOG production TO `data-engineers`;

-- Schema level
GRANT USE SCHEMA ON SCHEMA production.bronze_salesforce TO `data-engineers`;
GRANT CREATE TABLE ON SCHEMA production.bronze_salesforce TO `data-engineers`;
GRANT ALL PRIVILEGES ON SCHEMA production.bronze_salesforce TO `data-engineers`;

-- Table level
GRANT SELECT ON TABLE production.gold_analytics.dim_customer TO `analysts`;
GRANT MODIFY ON TABLE production.silver_salesforce.account TO `etl-service`;
```

### Revoke Privileges
```sql
REVOKE SELECT ON TABLE production.silver_salesforce.account FROM `analysts`;
```

### Show Grants
```sql
-- Show grants on table
SHOW GRANTS ON TABLE production.silver_salesforce.account;

-- Show grants to principal
SHOW GRANTS TO `data-engineers`;
```

### Row-Level Security
```sql
-- Create row filter function
CREATE FUNCTION production.filters.region_filter(region STRING)
RETURN IF(IS_MEMBER('global-admins'), true, region = current_user_region());

-- Apply to table
ALTER TABLE production.gold_analytics.fact_sales
SET ROW FILTER production.filters.region_filter ON (region);

-- Remove filter
ALTER TABLE production.gold_analytics.fact_sales DROP ROW FILTER;
```

### Column Masking
```sql
-- Create masking function
CREATE FUNCTION production.masks.mask_email(email STRING)
RETURN CASE
    WHEN IS_MEMBER('pii-access') THEN email
    ELSE CONCAT('***@', SPLIT(email, '@')[1])
END;

-- Apply mask
ALTER TABLE production.silver_salesforce.contact
ALTER COLUMN email SET MASK production.masks.mask_email;

-- Remove mask
ALTER TABLE production.silver_salesforce.contact
ALTER COLUMN email DROP MASK;
```

## External Locations

### Create Storage Credential
```sql
-- Create credential for S3
CREATE STORAGE CREDENTIAL aws_credential
WITH (
    ACCESS_KEY_ID = '...',
    SECRET_ACCESS_KEY = '...'
);

-- Create credential with IAM role
CREATE STORAGE CREDENTIAL aws_role_credential
WITH (
    IAM_ROLE = 'arn:aws:iam::123456789:role/unity-catalog-role'
);
```

### Create External Location
```sql
-- Create external location
CREATE EXTERNAL LOCATION salesforce_landing
URL 's3://bucket/landing/salesforce/'
WITH (STORAGE CREDENTIAL aws_credential)
COMMENT 'Salesforce landing zone';

-- Grant access
GRANT READ FILES ON EXTERNAL LOCATION salesforce_landing TO `etl-service`;
GRANT WRITE FILES ON EXTERNAL LOCATION salesforce_landing TO `etl-service`;
```

## Data Lineage

### View Lineage
```python
# Using API
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

# Get table lineage
lineage = w.lineage.get_table_lineage(
    table_name="production.gold_analytics.dim_customer"
)

# Upstream tables
for upstream in lineage.upstream_tables:
    print(f"Upstream: {upstream.name}")

# Downstream tables
for downstream in lineage.downstream_tables:
    print(f"Downstream: {downstream.name}")
```

### Lineage Query
```sql
-- Query system tables for lineage
SELECT
    source_table_full_name,
    target_table_full_name,
    event_time
FROM system.access.table_lineage
WHERE target_table_full_name = 'production.gold_analytics.dim_customer';
```

## Data Discovery

### Search Data
```python
# Search tables
results = w.search.search_tables(
    query="customer",
    max_results=10
)

for table in results.tables:
    print(f"{table.full_name}: {table.comment}")
```

### Describe Objects
```sql
-- Describe table
DESCRIBE TABLE production.silver_salesforce.account;

-- Describe extended
DESCRIBE TABLE EXTENDED production.silver_salesforce.account;

-- Show tables
SHOW TABLES IN production.silver_salesforce;

-- Show columns
SHOW COLUMNS IN production.silver_salesforce.account;
```

## Audit Logging

### Query Audit Logs
```sql
-- Recent table access
SELECT
    event_time,
    action_name,
    user_identity.email,
    request_params.full_name_arg
FROM system.access.audit
WHERE action_name IN ('getTable', 'createTable', 'deleteTable')
AND event_time > current_timestamp() - INTERVAL 1 DAY
ORDER BY event_time DESC;

-- Data access patterns
SELECT
    request_params.full_name_arg as table_name,
    COUNT(*) as access_count,
    COUNT(DISTINCT user_identity.email) as unique_users
FROM system.access.audit
WHERE action_name = 'getTable'
AND event_time > current_timestamp() - INTERVAL 7 DAY
GROUP BY table_name
ORDER BY access_count DESC;
```

## Volumes (File Storage)

### Create Volume
```sql
-- Managed volume
CREATE VOLUME production.bronze_salesforce.landing;

-- External volume
CREATE EXTERNAL VOLUME production.bronze_salesforce.landing
LOCATION 's3://bucket/landing/salesforce/';
```

### Access Volume
```python
# Read from volume
df = spark.read.format("csv") \
    .load("/Volumes/production/bronze_salesforce/landing/data.csv")

# Write to volume
df.write.format("csv") \
    .save("/Volumes/production/bronze_salesforce/landing/output/")
```

## Best Practices

### Naming Conventions
```
Catalogs: {environment} (production, development, sandbox)
Schemas: {layer}_{source} (bronze_salesforce, silver_salesforce)
Tables: {object} (account, contact, opportunity)
```

### Organization Pattern
```
production (catalog)
+-- bronze_salesforce (schema)
|   +-- account (table)
|   +-- contact (table)
+-- silver_salesforce (schema)
|   +-- account (table)
|   +-- contact (table)
+-- gold_analytics (schema)
    +-- dim_customer (table)
    +-- fact_sales (table)
```

### Security Best Practices
- Use groups for access control
- Apply row filters for multi-tenant data
- Mask sensitive columns
- Use external locations for large data
- Audit access regularly

## Anti-Patterns

- Don't use two-part names (schema.table)
- Don't grant direct user access (use groups)
- Don't skip column comments
- Don't create catalogs per project
- Don't mix managed and external in same schema
