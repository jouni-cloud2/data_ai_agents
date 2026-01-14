---
name: delta-live-tables
description: Building production DLT pipelines with expectations.
---

# Delta Live Tables Skill

## What is DLT?

Declarative framework for building reliable data pipelines:
- Automatic dependency management
- Built-in data quality (expectations)
- Automatic lineage tracking
- Unified batch and streaming
- Auto-scaling and optimization

## When to Use DLT

### Use DLT For:
- Production ETL pipelines
- Medallion architecture
- Data quality enforcement
- Streaming + batch unified
- Automatic lineage needs
- CDC processing

### Don't Use DLT For:
- Ad-hoc analysis
- ML training pipelines
- One-off transformations
- Complex orchestration

## Basic DLT Pipeline

```python
import dlt
from pyspark.sql.functions import *

# BRONZE - Raw ingestion
@dlt.table(
    name="bronze_salesforce_account",
    comment="Raw Salesforce accounts"
)
def bronze_account():
    return (
        spark.readStream
        .format("cloudFiles")
        .option("cloudFiles.format", "json")
        .option("cloudFiles.schemaLocation", "/checkpoints/schema/account")
        .load("/landing/salesforce/account/")
    )

# SILVER - Cleaned with expectations
@dlt.table(
    name="silver_salesforce_account",
    comment="Cleaned Salesforce accounts"
)
@dlt.expect("valid_id", "account_id IS NOT NULL")
@dlt.expect_or_drop("valid_name", "LENGTH(account_name) > 0")
def silver_account():
    return (
        dlt.read_stream("bronze_salesforce_account")
        .select(
            col("Id").alias("account_id"),
            col("Name").alias("account_name"),
            sha2(col("Email"), 256).alias("email_hash"),
            current_timestamp().alias("_loaded_at")
        )
    )

# GOLD - Business aggregations
@dlt.table(
    name="gold_account_summary",
    comment="Account summary for analytics"
)
def gold_summary():
    return (
        dlt.read("silver_salesforce_account")
        .groupBy("account_id")
        .agg(
            count("*").alias("record_count"),
            max("_loaded_at").alias("last_updated")
        )
    )
```

## Table Decorators

### @dlt.table
```python
@dlt.table(
    name="table_name",                      # Required
    comment="Description",                   # Optional
    spark_conf={"key": "value"},            # Optional Spark configs
    table_properties={"key": "value"},      # Optional Delta properties
    path="/path/to/table",                  # Optional external path
    partition_cols=["col1", "col2"],        # Optional partitioning
    schema="col1 STRING, col2 INT",         # Optional explicit schema
    temporary=False                          # Optional temp table
)
def my_table():
    return df
```

### @dlt.view
```python
# Views are not materialized
@dlt.view(
    name="view_name",
    comment="Description"
)
def my_view():
    return df
```

## Expectations (Data Quality)

### Types of Expectations

#### @dlt.expect() - Log violations
```python
@dlt.expect("valid_email", "email RLIKE '^[^@]+@[^@]+$'")
def my_table():
    # Invalid records are kept, violations logged
    return df
```

#### @dlt.expect_or_drop() - Drop violations
```python
@dlt.expect_or_drop("valid_id", "id IS NOT NULL")
def my_table():
    # Invalid records are dropped
    return df
```

#### @dlt.expect_or_fail() - Fail pipeline
```python
@dlt.expect_or_fail("critical_check", "critical_field IS NOT NULL")
def my_table():
    # Pipeline fails if any violations
    return df
```

### Multiple Expectations
```python
@dlt.table(name="silver_account")
@dlt.expect("valid_id", "account_id IS NOT NULL")
@dlt.expect("valid_name", "LENGTH(account_name) > 0")
@dlt.expect_or_drop("valid_email", "email RLIKE '^[^@]+@[^@]+'")
@dlt.expect_or_fail("no_duplicates", "COUNT(*) = COUNT(DISTINCT account_id)")
def silver_account():
    return dlt.read_stream("bronze_account")
```

### Expectations with Aggregations
```python
@dlt.expect_all({
    "valid_id": "id IS NOT NULL",
    "valid_name": "name IS NOT NULL",
    "positive_amount": "amount >= 0"
})
def my_table():
    return df

@dlt.expect_all_or_drop({
    "valid_id": "id IS NOT NULL",
    "valid_date": "date IS NOT NULL"
})
def my_table():
    return df
```

## Reading Data

### Read from DLT Table
```python
# Streaming read (for streaming tables)
df = dlt.read_stream("bronze_table")

# Batch read (for materialized views)
df = dlt.read("silver_table")
```

### Read from External Source
```python
# Cloud storage
df = spark.readStream.format("cloudFiles") \
    .option("cloudFiles.format", "json") \
    .load("/landing/data/")

# Kafka
df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "host:9092") \
    .option("subscribe", "topic") \
    .load()

# Delta table
df = spark.read.table("catalog.schema.table")
```

## CDC Processing

### Apply Changes (SCD Type 1)
```python
dlt.create_streaming_table("target_table")

dlt.apply_changes(
    target="target_table",
    source="cdc_source",
    keys=["id"],
    sequence_by="event_timestamp",
    apply_as_deletes=expr("operation = 'DELETE'"),
    except_column_list=["operation", "event_timestamp"]
)
```

### Apply Changes (SCD Type 2)
```python
dlt.create_streaming_table(
    name="target_table_history",
    table_properties={
        "pipelines.autoOptimize.zOrderCols": "id"
    }
)

dlt.apply_changes(
    target="target_table_history",
    source="cdc_source",
    keys=["id"],
    sequence_by="event_timestamp",
    stored_as_scd_type=2,
    except_column_list=["operation"]
)
```

## Streaming vs Batch

### Streaming Table
```python
@dlt.table(name="streaming_table")
def my_streaming():
    # Use readStream for continuous processing
    return spark.readStream.format("cloudFiles").load("/landing/")

# Or read from another streaming table
def downstream():
    return dlt.read_stream("streaming_table")
```

### Materialized View (Batch)
```python
@dlt.table(name="batch_table")
def my_batch():
    # Use read for batch processing
    return spark.read.table("catalog.schema.source")

# Or read from DLT table
def downstream():
    return dlt.read("streaming_table")  # Note: no _stream
```

## Pipeline Configuration

### Pipeline Settings
```json
{
  "name": "salesforce_dlt",
  "target": "production_dlt",
  "continuous": false,
  "development": false,
  "channel": "CURRENT",
  "photon": true,
  "libraries": [
    {
      "notebook": {
        "path": "/Repos/project/pipelines/salesforce_dlt"
      }
    }
  ],
  "configuration": {
    "source_path": "s3://bucket/landing/salesforce/",
    "quality_threshold": "0.95"
  },
  "clusters": [
    {
      "label": "default",
      "autoscale": {
        "min_workers": 1,
        "max_workers": 5,
        "mode": "ENHANCED"
      }
    }
  ]
}
```

### Access Configuration
```python
# In notebook
source_path = spark.conf.get("source_path")
threshold = float(spark.conf.get("quality_threshold", "0.9"))
```

## Event Log Queries

### Query Expectations Results
```sql
-- Expectation results
SELECT
    timestamp,
    details:flow_name::STRING as table_name,
    details:expectation_results as expectations
FROM event_log(TABLE(production_dlt.salesforce_dlt))
WHERE event_type = 'flow_progress'
AND details:expectation_results IS NOT NULL;
```

### Query Pipeline Metrics
```sql
-- Pipeline run metrics
SELECT
    timestamp,
    details:flow_name::STRING as table_name,
    details:metrics:num_output_rows::LONG as rows_written
FROM event_log(TABLE(production_dlt.salesforce_dlt))
WHERE event_type = 'flow_progress';
```

### Query Errors
```sql
-- Pipeline errors
SELECT
    timestamp,
    details:error as error_details
FROM event_log(TABLE(production_dlt.salesforce_dlt))
WHERE event_type = 'error';
```

## Common Patterns

### Medallion Architecture
```python
import dlt
from pyspark.sql.functions import *

# BRONZE
@dlt.table(name="bronze_orders")
def bronze():
    return spark.readStream.format("cloudFiles") \
        .option("cloudFiles.format", "json") \
        .load("/landing/orders/")

# SILVER
@dlt.table(name="silver_orders")
@dlt.expect_or_drop("valid_order", "order_id IS NOT NULL")
@dlt.expect_or_drop("valid_amount", "amount > 0")
def silver():
    return (
        dlt.read_stream("bronze_orders")
        .select(
            col("order_id"),
            col("customer_id"),
            col("amount").cast("decimal(18,2)"),
            to_date(col("order_date")).alias("order_date"),
            current_timestamp().alias("_processed_at")
        )
    )

# GOLD - Aggregation
@dlt.table(name="gold_daily_sales")
def gold():
    return (
        dlt.read("silver_orders")
        .groupBy("order_date")
        .agg(
            count("order_id").alias("order_count"),
            sum("amount").alias("total_amount")
        )
    )
```

### Multi-Source Join
```python
@dlt.table(name="enriched_orders")
def enriched():
    orders = dlt.read("silver_orders")
    customers = dlt.read("silver_customers")

    return orders.join(
        customers,
        orders.customer_id == customers.customer_id,
        "left"
    ).select(
        orders["*"],
        customers.customer_name,
        customers.segment
    )
```

### Slowly Changing Dimension
```python
dlt.create_streaming_table(
    name="dim_customer_history",
    comment="Customer dimension with history"
)

dlt.apply_changes(
    target="dim_customer_history",
    source="cdc_customers",
    keys=["customer_id"],
    sequence_by="updated_at",
    stored_as_scd_type=2
)

@dlt.table(name="dim_customer_current")
def current_customers():
    return (
        dlt.read("dim_customer_history")
        .filter("__END_AT IS NULL")
    )
```

## Best Practices

- Use expectations for data quality
- Use streaming for real-time needs
- Keep transformations simple
- Use meaningful table names
- Add comments to all tables
- Monitor event logs
- Use Photon for performance

## Anti-Patterns

- Don't use complex Python logic in DLT
- Don't skip expectations
- Don't mix streaming and batch incorrectly
- Don't ignore event log warnings
- Don't create circular dependencies
