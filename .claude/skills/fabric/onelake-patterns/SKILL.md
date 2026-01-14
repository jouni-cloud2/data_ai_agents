---
name: onelake-patterns
description: OneLake storage patterns and optimization for Microsoft Fabric.
---

# OneLake Patterns Skill

## OneLake Overview

OneLake is Fabric's unified storage layer:
- Single data lake for entire organization
- Delta Lake format by default
- Built-in governance
- Cross-workspace access
- Automatic optimization

## Storage Structure

### Lakehouse Files Organization
```
lh_sales/
+-- Files/                    <- Unmanaged files area
|   +-- bronze/               <- Raw data
|   |   +-- salesforce/
|   |   |   +-- account/
|   |   |   |   +-- _delta_log/
|   |   |   |   +-- part-00000-*.parquet
|   |   |   +-- opportunity/
|   |   +-- sap/
|   +-- silver/               <- Cleaned data
|   |   +-- salesforce/
|   |   |   +-- account/
|   |   +-- sap/
|   +-- gold/                 <- Business data
|   |   +-- sales_mart/
|   |       +-- dim_customer/
|   |       +-- fact_sales/
|   +-- _checkpoints/         <- Streaming checkpoints
|   +-- _schemas/             <- Schema evolution
|   +-- _logs/                <- Processing logs
|
+-- Tables/                   <- Managed Delta tables
    +-- bronze_salesforce_account
    +-- silver_salesforce_account
    +-- gold_dim_customer
```

## Reading and Writing Patterns

### Read from Folder
```python
# Read Delta from folder path
df = spark.read.format("delta").load("Files/bronze/salesforce/account/")

# Read specific version
df = spark.read.format("delta") \
    .option("versionAsOf", 5) \
    .load("Files/bronze/salesforce/account/")

# Read as of timestamp
df = spark.read.format("delta") \
    .option("timestampAsOf", "2024-01-15 10:00:00") \
    .load("Files/bronze/salesforce/account/")
```

### Write to Folder
```python
# Write Delta to folder
df.write.format("delta") \
    .mode("append") \
    .save("Files/bronze/salesforce/account/")

# Write with partitioning
df.write.format("delta") \
    .mode("append") \
    .partitionBy("year", "month") \
    .save("Files/bronze/salesforce/account/")
```

### Create Managed Table
```python
# Create table pointing to folder
spark.sql("""
    CREATE TABLE IF NOT EXISTS bronze_salesforce_account
    USING DELTA
    LOCATION 'Files/bronze/salesforce/account/'
""")

# Or create and write in one step
df.write.format("delta") \
    .mode("overwrite") \
    .saveAsTable("bronze_salesforce_account")
```

## Delta Lake Operations

### Merge (Upsert)
```python
from delta.tables import DeltaTable

delta_table = DeltaTable.forPath(spark, "Files/silver/salesforce/account/")

delta_table.alias("target").merge(
    updates_df.alias("source"),
    "target.account_id = source.account_id"
).whenMatchedUpdate(
    set={
        "account_name": "source.account_name",
        "updated_at": "current_timestamp()"
    }
).whenNotMatchedInsert(
    values={
        "account_id": "source.account_id",
        "account_name": "source.account_name",
        "created_at": "current_timestamp()"
    }
).execute()
```

### Delete
```python
delta_table = DeltaTable.forPath(spark, "Files/silver/salesforce/account/")

# Delete specific records
delta_table.delete("is_deleted = true")

# Delete with condition
delta_table.delete(col("last_updated") < "2023-01-01")
```

### Update
```python
delta_table = DeltaTable.forPath(spark, "Files/silver/salesforce/account/")

delta_table.update(
    condition="status = 'pending'",
    set={"status": "'active'", "activated_at": "current_timestamp()"}
)
```

## Optimization Patterns

### Z-Ordering
```python
# Optimize with Z-ordering for common filter columns
spark.sql("""
    OPTIMIZE 'Files/silver/salesforce/account/'
    ZORDER BY (account_id, created_date)
""")

# Or using table name
spark.sql("""
    OPTIMIZE silver_salesforce_account
    ZORDER BY (account_id, created_date)
""")
```

**When to Z-Order:**
- Columns frequently used in WHERE clauses
- Columns used in JOIN conditions
- High cardinality columns
- Re-run after significant data changes

### Compaction
```python
# Auto-compaction (recommended)
spark.sql("""
    ALTER TABLE silver_salesforce_account
    SET TBLPROPERTIES (
        'delta.autoOptimize.optimizeWrite' = 'true',
        'delta.autoOptimize.autoCompact' = 'true'
    )
""")

# Manual compaction
spark.sql("OPTIMIZE 'Files/silver/salesforce/account/'")
```

### Vacuum
```python
# Remove old files (default 7 days retention)
spark.sql("VACUUM 'Files/silver/salesforce/account/' RETAIN 168 HOURS")

# Dry run to see what will be deleted
spark.sql("VACUUM 'Files/silver/salesforce/account/' DRY RUN")

# Force vacuum (use with caution)
spark.conf.set("spark.databricks.delta.retentionDurationCheck.enabled", "false")
spark.sql("VACUUM 'Files/silver/salesforce/account/' RETAIN 0 HOURS")
```

### Statistics
```python
# Compute table statistics
spark.sql("ANALYZE TABLE silver_salesforce_account COMPUTE STATISTICS")

# Compute column statistics
spark.sql("""
    ANALYZE TABLE silver_salesforce_account
    COMPUTE STATISTICS FOR COLUMNS account_id, created_date
""")
```

## Partitioning Strategies

### Date-Based Partitioning
```python
# Write with year/month partitioning
df.withColumn("year", year(col("created_date"))) \
    .withColumn("month", month(col("created_date"))) \
    .write.format("delta") \
    .mode("append") \
    .partitionBy("year", "month") \
    .save("Files/bronze/salesforce/account/")
```

### Query Partitioned Data
```python
# Efficient - uses partition pruning
df = spark.read.format("delta") \
    .load("Files/bronze/salesforce/account/") \
    .filter("year = 2024 AND month = 1")

# Inefficient - scans all partitions
df = spark.read.format("delta") \
    .load("Files/bronze/salesforce/account/") \
    .filter("MONTH(created_date) = 1")  # Function prevents pruning
```

### Partition Guidelines
- Target: 1GB per partition file
- Maximum: 10,000 partitions per table
- Avoid: High cardinality partition columns
- Consider: Date hierarchy (year/month) vs single date

## Time Travel

### Query Historical Data
```python
# Read specific version
df = spark.read.format("delta") \
    .option("versionAsOf", 5) \
    .load("Files/silver/salesforce/account/")

# Read as of timestamp
df = spark.read.format("delta") \
    .option("timestampAsOf", "2024-01-15 10:00:00") \
    .load("Files/silver/salesforce/account/")
```

### View History
```python
# Get table history
history_df = spark.sql("DESCRIBE HISTORY 'Files/silver/salesforce/account/'")
history_df.show()

# Or with DeltaTable
delta_table = DeltaTable.forPath(spark, "Files/silver/salesforce/account/")
history_df = delta_table.history()
```

### Restore Previous Version
```python
# Restore to specific version
spark.sql("RESTORE 'Files/silver/salesforce/account/' TO VERSION AS OF 5")

# Restore to timestamp
spark.sql("""
    RESTORE 'Files/silver/salesforce/account/'
    TO TIMESTAMP AS OF '2024-01-15 10:00:00'
""")
```

## Cross-Workspace Access

### Shortcuts
```python
# Read from another workspace via shortcut
# Shortcut must be created in Fabric UI first
df = spark.read.format("delta") \
    .load("Files/shortcuts/other_workspace/bronze/table/")
```

### OneLake Path Format
```
abfss://<workspace>@onelake.dfs.fabric.microsoft.com/<lakehouse>/Files/<path>
```

## Streaming Patterns

### Auto Loader
```python
# Read streaming with schema inference
df = spark.readStream.format("cloudFiles") \
    .option("cloudFiles.format", "csv") \
    .option("cloudFiles.schemaLocation", "Files/_schemas/landing/") \
    .option("cloudFiles.inferColumnTypes", "true") \
    .load("Files/landing/")
```

### Write Streaming
```python
# Write streaming to Delta
df.writeStream \
    .format("delta") \
    .option("checkpointLocation", "Files/_checkpoints/account/") \
    .outputMode("append") \
    .start("Files/bronze/salesforce/account/")
```

### Trigger Options
```python
# Process all available data
.trigger(availableNow=True)

# Process every 5 minutes
.trigger(processingTime="5 minutes")

# Process once and stop
.trigger(once=True)
```

## Schema Evolution

### Enable Schema Evolution
```python
# Allow schema changes on write
df.write.format("delta") \
    .mode("append") \
    .option("mergeSchema", "true") \
    .save("Files/bronze/salesforce/account/")
```

### Schema Migration
```python
# Add new column
spark.sql("""
    ALTER TABLE bronze_salesforce_account
    ADD COLUMN new_field STRING
""")

# Change column type (if compatible)
spark.sql("""
    ALTER TABLE bronze_salesforce_account
    ALTER COLUMN amount TYPE DECIMAL(18,2)
""")
```

## Best Practices

- Use folder organization for medallion layers
- Create managed tables for SQL access
- Enable auto-optimization
- Z-order on frequently filtered columns
- Partition large tables by date
- Use time travel for recovery
- Vacuum regularly
- Monitor storage usage

## Anti-Patterns

- Don't create too many small files
- Don't over-partition tables
- Don't skip optimization
- Don't vacuum too aggressively
- Don't use SELECT * in production
