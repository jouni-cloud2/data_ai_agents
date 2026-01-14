---
name: etl-patterns
description: Common ETL patterns - incremental load, SCD, upsert, CDC.
---

# ETL Patterns Skill

## Pattern 1: Full Load

```python
# Simple: overwrite everything
df.write.mode("overwrite").save(path)
```

**When to use:**
- Small reference tables
- Complete refresh required
- Source doesn't support incremental

**Considerations:**
- Higher resource usage
- Longer run times
- History lost without SCD

## Pattern 2: Incremental Load

```python
# Get last watermark
last_watermark = spark.sql("""
    SELECT MAX(_ingested_at) FROM bronze_table
""").collect()[0][0]

# Load only new
new_records = source_df.filter(
    col("modified_date") > last_watermark
)

# Append
new_records.write.mode("append").save(path)
```

**When to use:**
- Large tables
- Source has modified timestamp
- Need to reduce load time

**Considerations:**
- Requires watermark column
- Handle late-arriving data
- Track watermark state

## Pattern 3: SCD Type 1 (Overwrite)

```python
# Just update in place
delta_table.alias("target").merge(
    updates.alias("source"),
    "target.id = source.id"
).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()
```

**When to use:**
- No history needed
- Current state only
- Corrections/fixes

**Considerations:**
- History is lost
- Simpler to implement
- Lower storage

## Pattern 4: SCD Type 2 (History)

```python
from delta.tables import DeltaTable
from pyspark.sql.functions import *

delta_table = DeltaTable.forPath(spark, path)

# Step 1: Close existing records
delta_table.alias("target").merge(
    updates.alias("source"),
    "target.id = source.id AND target.is_current = true"
).whenMatchedUpdate(
    condition="target.hash != source.hash",  # Only if changed
    set={
        "is_current": lit(False),
        "valid_to": current_timestamp()
    }
).execute()

# Step 2: Insert new versions
updates_with_metadata = updates.withColumn("is_current", lit(True)) \
    .withColumn("valid_from", current_timestamp()) \
    .withColumn("valid_to", lit(None).cast("timestamp"))

updates_with_metadata.write.mode("append").save(path)
```

**When to use:**
- Need full history
- Audit requirements
- Point-in-time queries

**Considerations:**
- Higher storage
- More complex queries
- Need hash for change detection

## Pattern 5: Upsert (Merge)

```python
delta_table.alias("target").merge(
    updates.alias("source"),
    "target.id = source.id"
).whenMatchedUpdate(
    set={
        "value": "source.value",
        "updated_at": current_timestamp()
    }
).whenNotMatchedInsert(
    values={
        "id": "source.id",
        "value": "source.value",
        "created_at": current_timestamp(),
        "updated_at": current_timestamp()
    }
).execute()
```

**When to use:**
- Mixed insert/update workloads
- Master data management
- Dimension loading

**Considerations:**
- Requires unique key
- Transaction support
- Handle nulls carefully

## Pattern 6: CDC (Change Data Capture)

```python
# Process CDC records
cdc_df = source_df.filter(
    col("_change_type").isin("INSERT", "UPDATE", "DELETE")
)

# Handle each type
inserts = cdc_df.filter(col("_change_type") == "INSERT")
updates = cdc_df.filter(col("_change_type") == "UPDATE")
deletes = cdc_df.filter(col("_change_type") == "DELETE")

# Apply changes
delta_table.alias("target").merge(
    cdc_df.alias("source"),
    "target.id = source.id"
).whenMatchedUpdate(
    condition="source._change_type = 'UPDATE'",
    set={"*": "source.*"}
).whenMatchedDelete(
    condition="source._change_type = 'DELETE'"
).whenNotMatchedInsert(
    condition="source._change_type = 'INSERT'",
    values={"*": "source.*"}
).execute()
```

**When to use:**
- Real-time replication
- Event-driven architecture
- Low-latency requirements

**Considerations:**
- Requires CDC source
- Order matters
- Handle replay scenarios

## Pattern 7: Late-Arriving Dimensions

```python
# Check if dimension exists
dim_exists = spark.sql(f"""
    SELECT 1 FROM dim_table
    WHERE business_key = '{key}'
    LIMIT 1
""").count() > 0

if not dim_exists:
    # Insert with backdated valid_from
    new_dim = spark.createDataFrame([{
        "business_key": key,
        "attributes": "Unknown",
        "valid_from": fact_date,  # Backdate to fact
        "is_current": True
    }])
    new_dim.write.mode("append").save(dim_path)
```

**When to use:**
- Facts arrive before dimensions
- Unknown dimension members
- Data quality issues

**Considerations:**
- Create placeholder records
- Update when dimension arrives
- Track "unknown" counts

## Pattern 8: Deduplication

```python
from pyspark.sql.window import Window

# Define window for dedup
window = Window.partitionBy("id").orderBy(col("_ingested_at").desc())

# Keep latest record
deduped_df = df.withColumn("row_num", row_number().over(window)) \
    .filter(col("row_num") == 1) \
    .drop("row_num")
```

**When to use:**
- Duplicate source records
- Multiple deliveries
- Replay scenarios

**Considerations:**
- Choose dedup strategy
- Performance impact
- Track duplicate counts

## Pattern 9: Data Quality Validation

```python
from pyspark.sql.functions import *

# Define quality checks
quality_df = df.withColumn(
    "_quality_score",
    (
        when(col("id").isNotNull(), 1).otherwise(0) +
        when(col("name").isNotNull(), 1).otherwise(0) +
        when(col("email").rlike("^[^@]+@[^@]+$"), 1).otherwise(0)
    ) / 3.0
)

# Filter by quality threshold
good_records = quality_df.filter(col("_quality_score") >= 0.8)
bad_records = quality_df.filter(col("_quality_score") < 0.8)

# Log bad records for review
bad_records.write.mode("append").save("quarantine/")
```

**When to use:**
- Data quality SLAs
- Validation requirements
- Error handling

**Considerations:**
- Define quality rules
- Quarantine bad records
- Alert on quality drops

## Best Practices

- Always use watermark for incremental
- Always handle duplicates
- Always maintain is_current flag for SCD2
- Always add _loaded_at timestamp

## Anti-Patterns

- Never full load large tables repeatedly
- Never skip deduplication
- Never lose history with SCD Type 1 when needed
