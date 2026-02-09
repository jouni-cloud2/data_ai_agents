# Medallion Architecture

A multi-layer data architecture pattern for lakehouse platforms.

## Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                        MEDALLION ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────┐      ┌──────────┐      ┌──────────┐                  │
│  │  BRONZE  │ ───► │  SILVER  │ ───► │   GOLD   │                  │
│  │  (Raw)   │      │ (Cleaned)│      │ (Business)│                  │
│  └──────────┘      └──────────┘      └──────────┘                  │
│       │                 │                 │                         │
│       ▼                 ▼                 ▼                         │
│   Raw ingest       Cleansed &        Business-ready                │
│   Append-only      Conformed         Aggregated                    │
│   Schema-on-read   Validated         Modeled                       │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

## Layer Definitions

### Bronze (Raw)

**Purpose**: Capture source data exactly as received.

| Aspect | Guideline |
|--------|-----------|
| **Schema** | Source schema, minimal transformation |
| **Data** | Append-only, immutable history |
| **Format** | Delta/Iceberg tables (Parquet underlying) |
| **Naming** | `bronze_{source}_{entity}` |
| **Retention** | Long-term (regulatory compliance) |

**Transformations Allowed:**
- Add ingestion metadata (`_ingested_at`, `_source_file`)
- Flatten nested JSON to columns
- Cast to appropriate types

**Transformations NOT Allowed:**
- Business logic
- Filtering/deduplication
- Joining with other sources

**Example:**
```python
# Bronze load - minimal transformation
df = spark.read.json(source_path)
df = df.withColumn("_ingested_at", current_timestamp())
df = df.withColumn("_source_file", input_file_name())
df.write.format("delta").mode("append").saveAsTable("bronze_hubspot_companies")
```

### Silver (Cleaned/Conformed)

**Purpose**: Clean, validate, and conform data for analysis.

| Aspect | Guideline |
|--------|-----------|
| **Schema** | Standardized, typed, documented |
| **Data** | Deduplicated, validated, current |
| **Format** | Delta/Iceberg tables |
| **Naming** | `silver_{entity}` (source-agnostic) |
| **Retention** | Medium-term |

**Transformations:**
- Deduplication (keep latest by key)
- Data type standardization
- Null handling
- PII hashing (see [Security & Privacy](security-privacy.md))
- Column renaming to standards
- Basic validation rules

**Example:**
```python
# Silver transform - clean and validate
df = spark.table("bronze_hubspot_companies")

# Deduplicate
df = df.dropDuplicates(["id"])

# Standardize
df = df.withColumn("company_name", trim(upper(col("name"))))
df = df.withColumn("updated_at", to_timestamp(col("updatedAt")))

# Hash PII
df = df.withColumn("email_hash", sha2(concat(col("email"), lit(SALT)), 256))
df = df.drop("email")

# Write with merge
df.write.format("delta").mode("overwrite").saveAsTable("silver_companies")
```

### Gold (Business/Consumption)

**Purpose**: Business-ready data optimized for consumption.

| Aspect | Guideline |
|--------|-----------|
| **Schema** | Dimensional model (star/snowflake) |
| **Data** | Aggregated, enriched, business terms |
| **Format** | Delta/Iceberg tables |
| **Naming** | `dim_{entity}`, `fact_{process}` |
| **Retention** | Based on business needs |

**Transformations:**
- Dimensional modeling (facts/dimensions)
- Business calculations
- Cross-source joins
- SCD Type 2 for dimensions
- Aggregations

**Example:**
```python
# Gold dimension - SCD Type 2
dim_customer = (
    silver_companies
    .join(silver_contacts, "company_id")
    .select(
        monotonically_increasing_id().alias("customer_sk"),
        col("company_id").alias("customer_id"),
        col("company_name"),
        col("industry"),
        current_timestamp().alias("valid_from"),
        lit(None).alias("valid_to"),
        lit(True).alias("is_current")
    )
)
```

## Cross-Layer Rules

### Data Flow
- Bronze → Silver: 1:1 or N:1 (consolidation)
- Silver → Gold: N:M (modeling, aggregation)
- Never skip layers (no Bronze → Gold directly)

### Schema Evolution
| Layer | Strategy |
|-------|----------|
| Bronze | Add columns freely, never delete |
| Silver | Managed schema evolution |
| Gold | Versioned with semantic versioning |

### Access Control
| Layer | Access |
|-------|--------|
| Bronze | Data Engineering only |
| Silver | Data Engineering + Analysts (read) |
| Gold | All business users |

## Naming Conventions

| Layer | Pattern | Example |
|-------|---------|---------|
| Bronze | `bronze_{source}_{entity}` | `bronze_hubspot_companies` |
| Silver | `silver_{entity}` | `silver_companies` |
| Gold Dimension | `dim_{entity}` | `dim_customer` |
| Gold Fact | `fact_{process}` | `fact_sales` |
| Gold Bridge | `bridge_{relationship}` | `bridge_customer_product` |

## Metadata Standards

Every table should have:

```python
# Table properties
{
    "layer": "bronze|silver|gold",
    "source_system": "hubspot|salesforce|...",
    "owner": "team/person",
    "classification": "public|internal|confidential|restricted",
    "refresh_frequency": "hourly|daily|weekly",
    "last_updated": "2026-02-09T10:00:00Z"
}
```

## When to Use Medallion

**Good Fit:**
- Multiple source systems
- Need for data lineage
- Regulatory/audit requirements
- Complex transformations
- Multiple consumer use cases

**Consider Alternatives:**
- Simple single-source analytics → Direct to Gold
- Real-time streaming → Lambda/Kappa architecture
- ML feature stores → Dedicated feature layer

## Platform Implementations

| Platform | Bronze | Silver | Gold | Reference |
|----------|--------|--------|------|-----------|
| **Fabric** | Lakehouse Tables | Lakehouse Tables | Lakehouse + Semantic Model | [Fabric Medallion](../platforms/fabric/) |
| **Databricks** | Delta Tables | Delta Tables | Delta Tables + Unity Catalog | [Databricks Medallion](../platforms/databricks/) |
| **Snowflake** | Raw Schema | Curated Schema | Presentation Schema | [Snowflake Medallion](../platforms/snowflake/) |

## References

- [Databricks Medallion Architecture](https://www.databricks.com/glossary/medallion-architecture)
- [Microsoft Fabric Medallion](https://learn.microsoft.com/fabric/onelake/onelake-medallion-lakehouse-architecture)
- [Delta Lake Best Practices](https://docs.delta.io/latest/best-practices.html)

---

*Last Updated: 2026-02-09*
