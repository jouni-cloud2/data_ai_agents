---
name: fabric-architecture
description: Microsoft Fabric architecture patterns and best practices.
---

# Fabric Architecture Skill

## Overview

Microsoft Fabric = Unified SaaS analytics platform
- Data Factory (pipelines)
- Data Engineering (Spark, notebooks)
- OneLake (unified storage)
- Power BI (visualization)

## Key Concepts

### OneLake
- Single data lake for organization
- Delta Lake by default
- No separate storage account
- Hierarchical namespace

### Data Domains & Data Marts
**Data Domain**: Logical grouping by business area (Sales, Finance, HR, etc.)
- Owns Bronze and Silver layers
- Domain expertise and ownership
- One workspace per environment per domain

**Data Mart**: Consumer-facing presentation layer
- Gold layer optimized for reporting/BI/self-service analytics
- Can be domain-owned OR cross-domain
- Optimized for specific use cases

### Lakehouse vs Warehouse

**Use Lakehouse:**
- Data lake capabilities
- Unstructured/semi-structured data
- Spark transformations
- Medallion architecture (folders, not schemas)
- Cost optimization

**Use Warehouse:**
- Pure SQL workloads
- Traditional DW patterns
- T-SQL procedures
- Migrating from Synapse

**Recommendation**: Start with Lakehouse

## Architecture Pattern

```
Source -> Pipeline -> Bronze Folder -> Notebook -> Silver Folder -> Notebook -> Gold Folder -> Power BI
                   (Domain-owned)              (Domain-owned)    (Domain or Cross-domain)
```

**Cross-Domain Pattern:**
```
Domain A Silver -> Notebook -> Staging Folder -> Notebook -> Cross-Domain Gold -> Power BI
Domain B Silver ->                            /
Domain C Silver ->                           /
```

## Workspace Organization (Domain-Based)

### Fabric Tenant Structure
```
Fabric Tenant
|
+-- Sales_Dev (Workspace)
|   +-- lh_sales (Lakehouse)
|   |   +-- Files/
|   |   |   +-- bronze/
|   |   |   |   +-- salesforce/
|   |   |   |       +-- account/
|   |   |   |       +-- opportunity/
|   |   |   +-- silver/
|   |   |   |   +-- salesforce/
|   |   |   |       +-- account/
|   |   |   |       +-- opportunity/
|   |   |   +-- gold/
|   |   |       +-- sales_mart/
|   |   |           +-- dim_customer/
|   |   |           +-- fact_sales/
|   |   +-- Tables/ (Delta tables)
|   +-- pl_ingest_salesforce_daily
|   +-- nb_transform_bronze_to_silver
|
+-- Sales_Test (Workspace)
|   +-- [same structure as Dev]
|
+-- Sales_Prod (Workspace)
|   +-- [same structure as Dev]
|
+-- Finance_Dev (Workspace)
|   +-- lh_finance (Lakehouse)
|   |   +-- Files/
|   |   |   +-- bronze/
|   |   |   +-- silver/
|   |   |   +-- gold/
|   |   +-- Tables/
|   +-- [pipelines and notebooks]
|
+-- Finance_Test (Workspace)
|   +-- [same structure]
|
+-- Finance_Prod (Workspace)
|   +-- [same structure]
|
+-- Enterprise_Prod (Workspace - Cross-Domain)
    +-- lh_enterprise (Lakehouse)
    |   +-- Files/
    |   |   +-- staging/  <- Intermediate cross-domain work
    |   |   |   +-- sales_finance_integration/
    |   |   +-- gold/     <- Cross-domain data marts
    |   |       +-- enterprise_mart/
    |   |           +-- dim_unified_customer/
    |   |           +-- fact_enterprise_revenue/
    |   +-- Tables/
    +-- [cross-domain notebooks]
```

## Domain Ownership Model

### Domain-Owned Layers
**Bronze**: Domain owns ingestion from sources
- Example: Sales domain owns Salesforce ingestion
- Location: `Sales_Dev/lh_sales/Files/bronze/salesforce/`

**Silver**: Domain owns cleaning and validation
- Example: Sales domain owns Salesforce transformations
- Location: `Sales_Dev/lh_sales/Files/silver/salesforce/`

**Gold (Domain)**: Domain-specific data marts
- Example: Sales domain owns sales-specific reports
- Location: `Sales_Dev/lh_sales/Files/gold/sales_mart/`
- Consumers: Sales team, sales dashboards

### Cross-Domain Layers
**Staging**: Intermediate work for cross-domain analysis
- Not consumer-facing
- Holds multi-step transformation outputs
- Location: `Enterprise_Prod/lh_enterprise/Files/staging/`
- Example: Joining Sales + Finance data before final mart

**Gold (Cross-Domain)**: Enterprise-wide data marts
- Combines multiple domains
- Consumer-facing for enterprise reporting
- Location: `Enterprise_Prod/lh_enterprise/Files/gold/enterprise_mart/`
- Example: Unified customer view (Sales + Finance + Support data)

## Lakehouse Folder Structure (No Schemas)

**IMPORTANT**: Fabric Lakehouses use **folders** for organization, NOT schemas like Databricks.

```
lh_sales/
+-- Files/
|   +-- bronze/              <- Raw data organized by source
|   |   +-- salesforce/
|   |   |   +-- account/
|   |   |   |   +-- [parquet/delta files]
|   |   |   +-- opportunity/
|   |   |       +-- [parquet/delta files]
|   |   +-- sap/
|   |       +-- customer/
|   |           +-- [parquet/delta files]
|   |
|   +-- silver/              <- Cleaned data organized by source
|   |   +-- salesforce/
|   |   |   +-- account/
|   |   |   |   +-- [delta files]
|   |   |   +-- opportunity/
|   |   |       +-- [delta files]
|   |   +-- sap/
|   |       +-- customer/
|   |           +-- [delta files]
|   |
|   +-- gold/                <- Business-ready data marts
|       +-- sales_mart/      <- Data mart name
|           +-- dim_customer/
|           |   +-- [delta files]
|           +-- fact_sales/
|               +-- [delta files]
|
+-- Tables/                  <- Delta tables (references Files/)
    +-- bronze_salesforce_account
    +-- silver_salesforce_account
    +-- gold_sales_mart_dim_customer
```

## Naming Conventions

### Workspaces
`{Domain}_{Environment}`
- Examples: Sales_Dev, Finance_Prod, Enterprise_Test

### Lakehouses
`lh_{domain}` or `lh_enterprise`
- Examples: lh_sales, lh_finance, lh_enterprise

### Folders
```
bronze/{source}/{object}/
silver/{source}/{object}/
gold/{mart_name}/{table}/
staging/{workflow_name}/{step}/
```

### Delta Tables
```
bronze_{source}_{object}
silver_{source}_{object}
gold_{mart}_{table}
```

Examples:
- `bronze_salesforce_account`
- `silver_salesforce_account`
- `gold_sales_mart_dim_customer`
- `gold_enterprise_mart_dim_unified_customer`

## Pipeline Activities

### Copy Activity
**When**: Simple data movement, built-in connectors

### Dataflow Gen2
**When**: Complex transformations, rate-limited APIs, Power Query

### Notebook
**When**: Complex Spark logic, business rules

## OneLake Optimization

```python
# Z-Ordering
spark.sql("OPTIMIZE table ZORDER BY (col1, col2)")

# Vacuum
spark.sql("VACUUM table RETAIN 168 HOURS")

# Statistics
spark.sql("ANALYZE TABLE table COMPUTE STATISTICS")
```

## Security

- Managed Identity for auth
- Azure Key Vault for secrets
- Workspace roles for access

## Monitoring

- Fabric monitoring workspace
- Pipeline run history
- Data Activator for alerts

## Best Practices

- Use OneLake
- Use Dataflow Gen2 for complex APIs
- Partition large tables
- Use managed identity
- Monitor CU consumption

## Anti-Patterns

- Don't use external storage
- Don't use SELECT *
- Don't skip optimization
