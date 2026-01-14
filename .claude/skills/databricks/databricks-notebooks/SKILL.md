---
name: databricks-notebooks
description: Writing Databricks notebooks for data transformations.
---

# Databricks Notebooks Skill

## Notebook Structure

```python
# Cell 1: Configuration
# Widgets, imports, config

# Cell 2: Read Data
# Load from source tables

# Cell 3: Transform
# Apply business logic

# Cell 4: Quality Checks
# Validate data

# Cell 5: Write Data
# Save to target tables

# Cell 6: Exit
# Return values and cleanup
```

## Widgets (Parameters)

### Define Widgets
```python
# Text widget
dbutils.widgets.text("run_date", "", "Run Date")

# Dropdown widget
dbutils.widgets.dropdown("load_type", "incremental", ["full", "incremental"], "Load Type")

# Combobox widget
dbutils.widgets.combobox("table", "", ["accounts", "contacts"], "Table Name")

# Multiselect widget
dbutils.widgets.multiselect("columns", "all", ["id", "name", "email", "all"], "Columns")
```

### Get Widget Values
```python
run_date = dbutils.widgets.get("run_date")
load_type = dbutils.widgets.get("load_type")
table = dbutils.widgets.get("table")
```

### Remove Widgets
```python
dbutils.widgets.remove("widget_name")
dbutils.widgets.removeAll()
```

## Reading Data

### Read from Unity Catalog
```python
# Read table
df = spark.read.table("production.bronze_salesforce.account")

# Read with SQL
df = spark.sql("SELECT * FROM production.bronze_salesforce.account WHERE modified_date > '2024-01-01'")
```

### Read from Storage
```python
# Read Delta
df = spark.read.format("delta").load("s3://bucket/bronze/salesforce/account/")

# Read with version
df = spark.read.format("delta") \
    .option("versionAsOf", 5) \
    .load("s3://bucket/bronze/salesforce/account/")

# Read CSV
df = spark.read.format("csv") \
    .option("header", "true") \
    .option("inferSchema", "true") \
    .load("s3://bucket/landing/data.csv")
```

### Streaming Read
```python
# Auto Loader
df = spark.readStream.format("cloudFiles") \
    .option("cloudFiles.format", "json") \
    .option("cloudFiles.schemaLocation", "s3://bucket/_schemas/") \
    .load("s3://bucket/landing/")
```

## Writing Data

### Write to Unity Catalog
```python
# Append
df.write.mode("append").saveAsTable("production.silver_salesforce.account")

# Overwrite
df.write.mode("overwrite").saveAsTable("production.silver_salesforce.account")

# Overwrite partition
df.write.mode("overwrite") \
    .option("replaceWhere", "date = '2024-01-15'") \
    .saveAsTable("production.silver_salesforce.account")
```

### Write to Storage
```python
# Write Delta
df.write.format("delta") \
    .mode("append") \
    .save("s3://bucket/silver/salesforce/account/")

# Write with partitioning
df.write.format("delta") \
    .mode("append") \
    .partitionBy("year", "month") \
    .save("s3://bucket/silver/salesforce/account/")
```

### Streaming Write
```python
df.writeStream \
    .format("delta") \
    .option("checkpointLocation", "s3://bucket/_checkpoints/account/") \
    .outputMode("append") \
    .toTable("production.silver_salesforce.account")
```

## Transformations

### Basic Transformations
```python
from pyspark.sql.functions import *

# Select and rename
df = df.select(
    col("Id").alias("account_id"),
    col("Name").alias("account_name"),
    col("Email"),
    col("ModifiedDate").alias("modified_date")
)

# Add columns
df = df.withColumn("_loaded_at", current_timestamp())
df = df.withColumn("_source", lit("salesforce"))

# Filter
df = df.filter(col("status") == "active")
df = df.filter(col("amount") > 0)

# Drop columns
df = df.drop("unnecessary_column")
```

### Type Conversions
```python
# Cast types
df = df.withColumn("amount", col("amount").cast("decimal(18,2)"))
df = df.withColumn("date", to_date(col("date_string"), "yyyy-MM-dd"))
df = df.withColumn("timestamp", to_timestamp(col("ts_string")))

# Parse nested data
from pyspark.sql.types import StructType, StructField, StringType

address_schema = StructType([
    StructField("street", StringType()),
    StructField("city", StringType()),
    StructField("zip", StringType())
])

df = df.withColumn("address", from_json(col("address_json"), address_schema))
df = df.select("*", "address.*")
```

### PII Masking
```python
# Hash PII
df = df.withColumn("email_hash", sha2(lower(col("email")), 256))
df = df.withColumn("phone_hash", sha2(col("phone"), 256))

# Partial masking
df = df.withColumn("masked_ssn",
    concat(lit("***-**-"), substring(col("ssn"), 8, 4)))

# Drop original PII
df = df.drop("email", "phone", "ssn")
```

### Deduplication
```python
from pyspark.sql.window import Window

# Simple dedup
df = df.dropDuplicates(["id"])

# Keep latest
window = Window.partitionBy("id").orderBy(col("modified_date").desc())
df = df.withColumn("row_num", row_number().over(window)) \
    .filter(col("row_num") == 1) \
    .drop("row_num")
```

### Aggregations
```python
# Group by
summary = df.groupBy("category").agg(
    count("*").alias("count"),
    sum("amount").alias("total"),
    avg("amount").alias("average")
)

# Window functions
window = Window.partitionBy("customer_id").orderBy("date")
df = df.withColumn("running_total", sum("amount").over(window))
df = df.withColumn("row_number", row_number().over(window))
```

### Joins
```python
# Inner join
result = accounts.join(contacts, accounts.id == contacts.account_id)

# Left join
result = accounts.join(contacts, "account_id", "left")

# Broadcast join (small table)
from pyspark.sql.functions import broadcast
result = large_df.join(broadcast(small_df), "key")
```

## Delta Operations

### Merge (Upsert)
```python
from delta.tables import DeltaTable

# Get target table
target = DeltaTable.forName(spark, "production.silver_salesforce.account")

# Merge
target.alias("target").merge(
    updates_df.alias("source"),
    "target.account_id = source.account_id"
).whenMatchedUpdate(
    set={
        "account_name": "source.account_name",
        "modified_date": "source.modified_date",
        "_loaded_at": "current_timestamp()"
    }
).whenNotMatchedInsert(
    values={
        "account_id": "source.account_id",
        "account_name": "source.account_name",
        "modified_date": "source.modified_date",
        "_loaded_at": "current_timestamp()"
    }
).execute()
```

### SCD Type 2
```python
# Close existing current records
target.alias("target").merge(
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

new_records.write.mode("append") \
    .saveAsTable("production.silver_salesforce.account")
```

## Quality Checks

```python
def run_quality_checks(df, table_name):
    """Run data quality checks and return results."""
    total = df.count()

    checks = {
        "total_rows": total,
        "null_ids": df.filter(col("id").isNull()).count(),
        "duplicates": total - df.select("id").distinct().count(),
        "null_required": df.filter(col("name").isNull()).count()
    }

    # Calculate pass rate
    issues = checks["null_ids"] + checks["duplicates"] + checks["null_required"]
    checks["quality_score"] = 1 - (issues / total) if total > 0 else 0

    # Log results
    print(f"Quality check for {table_name}:")
    for check, value in checks.items():
        print(f"  {check}: {value}")

    # Fail if quality below threshold
    if checks["quality_score"] < 0.95:
        raise ValueError(f"Quality score {checks['quality_score']:.2%} below 95% threshold")

    return checks
```

## Secrets

```python
# Get secret from scope
api_key = dbutils.secrets.get(scope="production", key="salesforce-api-key")
password = dbutils.secrets.get(scope="production", key="db-password")

# Use in connection
connection_string = f"jdbc:postgresql://host:5432/db?user=admin&password={password}"
```

## Notebook Exit

```python
# Exit with success
dbutils.notebook.exit("SUCCESS")

# Exit with value (for task output)
output = {"rows_processed": 1000, "output_table": "silver_salesforce_account"}
dbutils.notebook.exit(json.dumps(output))
```

## Run Child Notebooks

```python
# Run notebook and get result
result = dbutils.notebook.run(
    "/notebooks/process_table",
    timeout_seconds=3600,
    arguments={"table_name": "accounts"}
)

# Run multiple in parallel
from concurrent.futures import ThreadPoolExecutor

def run_notebook(table):
    return dbutils.notebook.run(
        "/notebooks/process_table",
        3600,
        {"table_name": table}
    )

tables = ["accounts", "contacts", "opportunities"]
with ThreadPoolExecutor(max_workers=3) as executor:
    results = list(executor.map(run_notebook, tables))
```

## Logging

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info(f"Starting processing for {table_name}")
logger.warning(f"Found {null_count} null values")
logger.error(f"Failed to process: {error}")
```

## Best Practices

- Use widgets for parameters
- Implement quality checks
- Use Delta merge for upserts
- Hash PII in Silver layer
- Log processing metrics
- Handle errors gracefully
- Exit with meaningful values

## Anti-Patterns

- Don't use collect() on large data
- Don't hardcode credentials
- Don't skip quality validation
- Don't forget exit statements
- Don't ignore widget defaults
