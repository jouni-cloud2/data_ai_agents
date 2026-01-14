---
name: fabric-notebooks
description: Writing Fabric notebooks for data transformations.
---

# Fabric Notebooks Skill

## Notebook Structure

```python
# Cell 1: Configuration
# Parameters and imports

# Cell 2: Read Data
# Load from Bronze/Silver

# Cell 3: Transform
# Apply business logic

# Cell 4: Quality Checks
# Validate data

# Cell 5: Write Data
# Save to target layer

# Cell 6: Logging
# Record metrics
```

## Reading Data

### Read from Delta Table
```python
# Read registered table
df = spark.read.table("bronze_salesforce_account")

# Read from folder path
df = spark.read.format("delta").load("Files/bronze/salesforce/account/")

# Read with options
df = spark.read.format("delta") \
    .option("versionAsOf", 5) \
    .load("Files/bronze/salesforce/account/")
```

### Read from Files
```python
# CSV
df = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load("Files/landing/data.csv")

# JSON
df = spark.read.format("json") \
    .option("multiLine", "true") \
    .load("Files/landing/data.json")

# Parquet
df = spark.read.format("parquet") \
    .load("Files/landing/data.parquet")
```

### Read Streaming
```python
# Auto Loader pattern
df = spark.readStream.format("cloudFiles") \
    .option("cloudFiles.format", "csv") \
    .option("cloudFiles.schemaLocation", "Files/_schemas/landing") \
    .load("Files/landing/")
```

## Writing Data

### Write to Delta
```python
# Append mode
df.write.format("delta") \
    .mode("append") \
    .save("Files/silver/salesforce/account/")

# Overwrite mode
df.write.format("delta") \
    .mode("overwrite") \
    .save("Files/silver/salesforce/account/")

# Overwrite partition
df.write.format("delta") \
    .mode("overwrite") \
    .option("replaceWhere", "date = '2024-01-15'") \
    .save("Files/silver/salesforce/account/")
```

### Create Managed Table
```python
# Create table from DataFrame
df.write.format("delta") \
    .mode("overwrite") \
    .saveAsTable("silver_salesforce_account")

# Create table with SQL
spark.sql("""
    CREATE TABLE IF NOT EXISTS silver_salesforce_account
    USING DELTA
    LOCATION 'Files/silver/salesforce/account/'
""")
```

### Write Streaming
```python
df.writeStream \
    .format("delta") \
    .option("checkpointLocation", "Files/_checkpoints/account") \
    .outputMode("append") \
    .start("Files/silver/salesforce/account/")
```

## Transformations

### Basic Transformations
```python
from pyspark.sql.functions import *

# Select columns
df = df.select("id", "name", "email")

# Rename columns
df = df.withColumnRenamed("old_name", "new_name")

# Add columns
df = df.withColumn("processed_at", current_timestamp())

# Filter rows
df = df.filter(col("status") == "active")

# Drop columns
df = df.drop("unnecessary_column")

# Drop nulls
df = df.dropna(subset=["required_field"])

# Fill nulls
df = df.fillna({"optional_field": "default_value"})
```

### Type Conversions
```python
# Cast types
df = df.withColumn("amount", col("amount").cast("decimal(18,2)"))
df = df.withColumn("date", to_date(col("date_string"), "yyyy-MM-dd"))
df = df.withColumn("timestamp", to_timestamp(col("ts_string")))

# Parse JSON
df = df.withColumn("parsed", from_json(col("json_string"), schema))
```

### PII Masking
```python
# SHA256 hashing
df = df.withColumn("email_hash", sha2(col("email"), 256))
df = df.withColumn("phone_hash", sha2(col("phone"), 256))

# Partial masking
df = df.withColumn("masked_ssn",
    concat(lit("***-**-"), substring(col("ssn"), 8, 4)))

# Drop PII after masking
df = df.drop("email", "phone", "ssn")
```

### Deduplication
```python
from pyspark.sql.window import Window

# Simple dedup
df = df.dropDuplicates(["id"])

# Keep latest record
window = Window.partitionBy("id").orderBy(col("modified_date").desc())
df = df.withColumn("row_num", row_number().over(window)) \
    .filter(col("row_num") == 1) \
    .drop("row_num")
```

### Aggregations
```python
# Group by aggregation
summary = df.groupBy("category").agg(
    count("*").alias("count"),
    sum("amount").alias("total_amount"),
    avg("amount").alias("avg_amount"),
    max("date").alias("latest_date")
)

# Window functions
window = Window.partitionBy("customer_id").orderBy("date")
df = df.withColumn("running_total", sum("amount").over(window))
df = df.withColumn("row_number", row_number().over(window))
```

### Joins
```python
# Inner join
result = df1.join(df2, df1.id == df2.id, "inner")

# Left join
result = df1.join(df2, "id", "left")

# Anti join (rows in df1 not in df2)
result = df1.join(df2, "id", "left_anti")

# Broadcast join (for small tables)
from pyspark.sql.functions import broadcast
result = df1.join(broadcast(small_df), "id")
```

## SCD Type 2 Implementation

```python
from delta.tables import DeltaTable

# Source data with changes
updates_df = spark.read.table("bronze_salesforce_account") \
    .withColumn("_hash", sha2(concat_ws("|", *["name", "address", "phone"]), 256))

# Target Delta table
target_path = "Files/silver/salesforce/account/"

if DeltaTable.isDeltaTable(spark, target_path):
    delta_table = DeltaTable.forPath(spark, target_path)

    # Close existing current records that have changes
    delta_table.alias("target").merge(
        updates_df.alias("source"),
        "target.account_id = source.account_id AND target.is_current = true"
    ).whenMatchedUpdate(
        condition="target._hash != source._hash",
        set={
            "is_current": lit(False),
            "valid_to": current_timestamp()
        }
    ).execute()

    # Insert new versions
    new_records = updates_df.withColumn("is_current", lit(True)) \
        .withColumn("valid_from", current_timestamp()) \
        .withColumn("valid_to", lit(None).cast("timestamp"))

    new_records.write.format("delta").mode("append").save(target_path)
else:
    # First load
    updates_df.withColumn("is_current", lit(True)) \
        .withColumn("valid_from", current_timestamp()) \
        .withColumn("valid_to", lit(None).cast("timestamp")) \
        .write.format("delta").save(target_path)
```

## Quality Checks

```python
def run_quality_checks(df, checks):
    """Run quality checks and return results."""
    results = []
    total_rows = df.count()

    for check_name, condition in checks.items():
        passed = df.filter(condition).count()
        results.append({
            "check": check_name,
            "passed": passed,
            "failed": total_rows - passed,
            "pass_rate": passed / total_rows if total_rows > 0 else 0
        })

    return results

# Define checks
checks = {
    "id_not_null": col("id").isNotNull(),
    "name_not_empty": length(col("name")) > 0,
    "valid_email": col("email").rlike("^[^@]+@[^@]+$"),
    "positive_amount": col("amount") >= 0
}

# Run checks
results = run_quality_checks(df, checks)

# Filter to good records
good_df = df.filter(
    col("id").isNotNull() &
    (length(col("name")) > 0)
)
```

## Parameters and Widgets

```python
# Define parameters (for pipeline integration)
# These become widgets in the notebook

# String parameter
run_date = spark.conf.get("spark.databricks.notebook.param.run_date", "2024-01-01")

# Or use notebook utils if available
# run_date = notebookutils.widgets.get("run_date")

# Use in queries
df = spark.sql(f"""
    SELECT * FROM bronze_table
    WHERE date = '{run_date}'
""")
```

## Logging and Metrics

```python
import json
from datetime import datetime

def log_metrics(metrics, table_name):
    """Log processing metrics."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "table": table_name,
        "metrics": metrics
    }

    # Write to log table
    log_df = spark.createDataFrame([log_entry])
    log_df.write.format("delta") \
        .mode("append") \
        .save("Files/_logs/processing_metrics/")

    print(json.dumps(log_entry, indent=2))

# Track metrics
metrics = {
    "input_rows": bronze_df.count(),
    "output_rows": silver_df.count(),
    "quality_score": 0.98,
    "duration_seconds": 45
}

log_metrics(metrics, "silver_salesforce_account")
```

## Error Handling

```python
from pyspark.sql.utils import AnalysisException

try:
    # Attempt transformation
    result_df = transform_data(source_df)
    result_df.write.format("delta").mode("append").save(target_path)

except AnalysisException as e:
    print(f"Schema error: {e}")
    # Handle schema issues
    raise

except Exception as e:
    print(f"Unexpected error: {e}")
    # Log error
    raise

finally:
    # Cleanup
    spark.catalog.clearCache()
```

## Best Practices

- Use cell organization for readability
- Add metadata columns (_loaded_at, _source_file)
- Implement quality checks before writing
- Log processing metrics
- Use parameterized notebooks
- Handle errors gracefully

## Anti-Patterns

- Don't use collect() on large datasets
- Don't skip quality validation
- Don't hardcode paths
- Don't forget to add metadata
