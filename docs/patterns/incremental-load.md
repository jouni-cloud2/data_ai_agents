# Incremental Load Pattern

Load only new or changed data instead of full table refreshes.

## Problem

Full table loads are:
- Slow for large datasets
- Resource-intensive
- Wasteful when only a small portion changes

## Solution

Track changes using watermarks, CDC, or merge strategies.

```
┌─────────────────────────────────────────────────────────────────┐
│                  INCREMENTAL LOAD STRATEGIES                     │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  WATERMARK           CDC                    MERGE               │
│  ┌──────────┐       ┌──────────┐          ┌──────────┐         │
│  │ Track    │       │ Capture  │          │ Compare  │         │
│  │ max date │       │ changes  │          │ & merge  │         │
│  │ or ID    │       │ stream   │          │ all rows │         │
│  └──────────┘       └──────────┘          └──────────┘         │
│       │                  │                      │               │
│  Simple,            Real-time,            Complete,             │
│  common             complex               slower                │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Watermark-Based Loading

### Concept

Track the maximum value of a monotonically increasing column (timestamp or ID) and load only records beyond that value.

### Implementation

```python
from pyspark.sql.functions import col, max as spark_max, lit
from datetime import datetime

def get_watermark(table_name: str, watermark_column: str) -> str:
    """Get current watermark value from target table."""
    try:
        result = spark.table(table_name).agg(
            spark_max(col(watermark_column)).alias("max_value")
        ).first()
        return result["max_value"] if result else None
    except Exception:
        # Table doesn't exist yet
        return None

def load_incremental_by_watermark(
    source_table: str,
    target_table: str,
    watermark_column: str = "updated_at"
):
    """Load only records newer than watermark."""

    # Get current watermark
    watermark = get_watermark(target_table, watermark_column)

    # Load source data
    source_df = spark.table(source_table)

    # Filter to new records only
    if watermark:
        source_df = source_df.filter(col(watermark_column) > lit(watermark))
        print(f"Loading records where {watermark_column} > {watermark}")
    else:
        print("No watermark found, loading all records")

    # Check if there's new data
    if source_df.isEmpty():
        print("No new records to load")
        return

    # Append to target
    source_df.write.format("delta").mode("append").saveAsTable(target_table)

    # Log new watermark
    new_watermark = source_df.agg(spark_max(col(watermark_column))).first()[0]
    print(f"Loaded records up to {watermark_column} = {new_watermark}")
```

### Watermark Column Selection

| Column Type | Pros | Cons | Example |
|-------------|------|------|---------|
| **Timestamp** | Natural for time-series | Clock skew issues | `updated_at` |
| **Auto-increment ID** | Guaranteed unique | Doesn't track updates | `id` |
| **Version number** | Explicit versioning | Requires source support | `version` |

## Merge (Upsert) Pattern

### Concept

Compare source and target, then insert new records and update changed records.

### Delta Lake MERGE

```python
from delta.tables import DeltaTable

def merge_into_silver(
    source_df,
    target_table: str,
    key_columns: list,
    update_condition: str = None
):
    """Merge source data into target table."""

    # Check if target exists
    if not spark.catalog.tableExists(target_table):
        # First load - just write
        source_df.write.format("delta").saveAsTable(target_table)
        return

    # Get target Delta table
    target = DeltaTable.forName(spark, target_table)

    # Build merge key condition
    merge_condition = " AND ".join([
        f"target.{col} = source.{col}" for col in key_columns
    ])

    # Perform merge
    merge_builder = (
        target.alias("target")
        .merge(source_df.alias("source"), merge_condition)
    )

    # Update existing records (with optional condition)
    if update_condition:
        merge_builder = merge_builder.whenMatchedUpdate(
            condition=update_condition,
            set={col: f"source.{col}" for col in source_df.columns}
        )
    else:
        merge_builder = merge_builder.whenMatchedUpdateAll()

    # Insert new records
    merge_builder = merge_builder.whenNotMatchedInsertAll()

    # Execute
    merge_builder.execute()
```

### Merge with Change Detection

```python
def merge_with_change_detection(
    source_df,
    target_table: str,
    key_columns: list,
    compare_columns: list
):
    """Only update if values actually changed."""

    # Build change detection condition
    change_conditions = [
        f"target.{col} != source.{col} OR "
        f"(target.{col} IS NULL AND source.{col} IS NOT NULL) OR "
        f"(target.{col} IS NOT NULL AND source.{col} IS NULL)"
        for col in compare_columns
    ]
    has_changes = " OR ".join(change_conditions)

    target = DeltaTable.forName(spark, target_table)
    merge_condition = " AND ".join([
        f"target.{col} = source.{col}" for col in key_columns
    ])

    (
        target.alias("target")
        .merge(source_df.alias("source"), merge_condition)
        .whenMatchedUpdate(
            condition=has_changes,
            set={col: f"source.{col}" for col in source_df.columns}
        )
        .whenNotMatchedInsertAll()
        .execute()
    )
```

## Change Data Capture (CDC)

### Concept

Capture insert, update, and delete operations from source systems.

### CDC Event Schema

```python
# Standard CDC event structure
cdc_schema = StructType([
    StructField("operation", StringType()),  # INSERT, UPDATE, DELETE
    StructField("timestamp", TimestampType()),
    StructField("before", MapType(StringType(), StringType())),  # Previous values
    StructField("after", MapType(StringType(), StringType())),   # New values
])
```

### Processing CDC Events

```python
from pyspark.sql.functions import when, col

def process_cdc_events(cdc_df, target_table: str, key_columns: list):
    """Apply CDC events to target table."""

    target = DeltaTable.forName(spark, target_table)
    merge_condition = " AND ".join([
        f"target.{col} = source.{col}" for col in key_columns
    ])

    # Extract data from 'after' column for inserts/updates
    source_df = cdc_df.select(
        col("operation"),
        *[col(f"after.{c}").alias(c) for c in key_columns],
        *[col(f"after.{c}").alias(c) for c in value_columns]
    )

    (
        target.alias("target")
        .merge(source_df.alias("source"), merge_condition)
        # Delete when operation is DELETE
        .whenMatchedDelete(condition="source.operation = 'DELETE'")
        # Update when operation is UPDATE
        .whenMatchedUpdateAll(condition="source.operation = 'UPDATE'")
        # Insert when operation is INSERT
        .whenNotMatchedInsertAll(condition="source.operation = 'INSERT'")
        .execute()
    )
```

## Soft Delete Pattern

### Problem

Hard deletes lose history and can cause referential integrity issues.

### Solution

Mark records as deleted instead of removing them.

```python
def soft_delete_merge(
    source_df,
    target_table: str,
    key_columns: list
):
    """Merge with soft delete for records not in source."""

    target = DeltaTable.forName(spark, target_table)
    merge_condition = " AND ".join([
        f"target.{col} = source.{col}" for col in key_columns
    ])

    # Add marker for records in source
    source_with_flag = source_df.withColumn("_in_source", lit(True))

    # Mark existing records not in source as deleted
    (
        target.alias("target")
        .merge(source_with_flag.alias("source"), merge_condition)
        .whenMatchedUpdate(set={
            **{col: f"source.{col}" for col in source_df.columns},
            "is_deleted": lit(False),
            "deleted_at": lit(None)
        })
        .whenNotMatchedInsertAll()
        .execute()
    )

    # Soft delete records not in source
    spark.sql(f"""
        UPDATE {target_table}
        SET is_deleted = true, deleted_at = current_timestamp()
        WHERE is_deleted = false
        AND ({merge_condition.replace('target.', '').replace('source.', '')})
        NOT IN (SELECT {', '.join(key_columns)} FROM source_df)
    """)
```

## Platform Variations

### Databricks Delta Live Tables

```python
import dlt
from pyspark.sql.functions import col

@dlt.table
def silver_customers():
    """Incremental update using Delta Live Tables."""
    return (
        dlt.read_stream("bronze_customers")
        .dropDuplicates(["customer_id"])
        .select("customer_id", "name", "email", "updated_at")
    )

# Apply changes using APPLY CHANGES
dlt.apply_changes(
    target="silver_customers",
    source="bronze_cdc_customers",
    keys=["customer_id"],
    sequence_by="updated_at",
    stored_as_scd_type=2
)
```

### Snowflake Streams

```sql
-- Create stream on source table
CREATE STREAM customer_changes ON TABLE raw_customers;

-- Process stream changes
MERGE INTO silver_customers AS target
USING (
    SELECT * FROM customer_changes
    WHERE METADATA$ACTION = 'INSERT'
       OR METADATA$ISUPDATE = TRUE
) AS source
ON target.customer_id = source.customer_id
WHEN MATCHED THEN UPDATE SET *
WHEN NOT MATCHED THEN INSERT *;

-- Handle deletes
DELETE FROM silver_customers
WHERE customer_id IN (
    SELECT customer_id FROM customer_changes
    WHERE METADATA$ACTION = 'DELETE'
);
```

### Azure Data Factory

```json
{
    "type": "Copy",
    "inputs": [{"referenceName": "SourceDataset"}],
    "outputs": [{"referenceName": "SinkDataset"}],
    "typeProperties": {
        "source": {
            "type": "SqlSource",
            "sqlReaderQuery": {
                "value": "SELECT * FROM source WHERE updated_at > '@{activity('GetWatermark').output.firstRow.max_updated_at}'",
                "type": "Expression"
            }
        },
        "sink": {
            "type": "ParquetSink",
            "writeBehavior": "insert"
        }
    }
}
```

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| **Trusting source timestamps** | Clocks may be inaccurate | Add ingestion timestamp as backup |
| **No idempotency** | Reruns create duplicates | Use merge instead of append |
| **Loading full then filtering** | Wastes resources | Push filter to source |
| **Ignoring deletes** | Stale data remains | Implement soft delete pattern |

## Monitoring

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| Records processed | New/updated records | Unusual volume |
| Merge duration | Time for merge operation | >2x average |
| Watermark lag | Time behind source | >SLA threshold |
| Duplicate rate | Records with same key | >0% |

## References

- [Delta Lake MERGE Documentation](https://docs.delta.io/latest/delta-update.html)
- [Databricks Incremental Processing](https://docs.databricks.com/en/structured-streaming/delta-lake.html)
- [Snowflake Streams](https://docs.snowflake.com/en/user-guide/streams-intro)

---

*Last Updated: 2026-02-09*
