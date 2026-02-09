# Fabric Notebook Standards

Standards and patterns for developing PySpark notebooks in Microsoft Fabric.

## Notebook Structure

### Standard Sections

```python
# %% [markdown]
# # {Notebook Title}
#
# **Purpose**: {One-line description}
# **Layer**: {Bronze/Silver/Gold}
# **Source**: {Source system or upstream table}
# **Target**: {Target table}
# **Schedule**: {Daily/Hourly/On-demand}

# %% Parameters
# Notebook parameters (for pipeline execution)
source_table = "bronze_hubspot_companies"
target_table = "silver_companies"
environment = "dev"

# %% Imports
from pyspark.sql.functions import col, lit, current_timestamp, when
from pyspark.sql.types import StructType, StringType, TimestampType
from delta.tables import DeltaTable
from notebookutils import mssparkutils

# %% Configuration
spark.conf.set("spark.sql.shuffle.partitions", "8")

# %% Secrets
API_KEY = mssparkutils.credentials.getSecret("kv-dataplatform", "api-key-name")

# %% Data Loading
df = spark.table(source_table)

# %% Transformations
# (transformation logic)

# %% Data Quality Checks
# (validation logic)

# %% Write Output
df.write.format("delta").mode("overwrite").saveAsTable(target_table)

# %% Logging
print(f"Wrote {df.count()} records to {target_table}")
```

## Naming Conventions

### Notebook Names

| Layer | Pattern | Example |
|-------|---------|---------|
| Bronze | `nb_bronze_load_{source}_{entity}` | `nb_bronze_load_hubspot_companies` |
| Silver | `nb_silver_transform_{entity}` | `nb_silver_transform_companies` |
| Gold | `nb_gold_{dim\|fact}_{entity}` | `nb_gold_dim_customer` |
| Utility | `nb_util_{purpose}` | `nb_util_data_quality` |

### Variable Names

```python
# DataFrames: df_{descriptive_name}
df_raw = spark.table("bronze_companies")
df_cleaned = df_raw.dropDuplicates()
df_enriched = df_cleaned.withColumn("processed_at", current_timestamp())

# Tables: Use snake_case matching table names
source_table = "bronze_hubspot_companies"
target_table = "silver_companies"

# Columns: Use snake_case
df = df.withColumnRenamed("firstName", "first_name")
```

## Common Patterns

### Bronze Load (API to Table)

```python
# %% Bronze Load Pattern
import requests
import json
from pyspark.sql.functions import current_timestamp, lit, input_file_name

def load_api_to_bronze(
    api_endpoint: str,
    api_key_secret: str,
    target_table: str,
    source_name: str
):
    """Load data from API to Bronze table."""

    # Get API key
    api_key = mssparkutils.credentials.getSecret("kv-dataplatform", api_key_secret)

    # Fetch data
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(api_endpoint, headers=headers)
    response.raise_for_status()
    data = response.json().get("results", [])

    if not data:
        print("No data returned from API")
        return 0

    # Create DataFrame
    df = spark.createDataFrame(data)

    # Add metadata
    df = (df
        .withColumn("_ingested_at", current_timestamp())
        .withColumn("_source_system", lit(source_name))
    )

    # Write to Bronze (append for history)
    df.write.format("delta").mode("append").saveAsTable(target_table)

    return df.count()

# Execute
count = load_api_to_bronze(
    api_endpoint="https://api.hubspot.com/crm/v3/objects/companies",
    api_key_secret="hubspot-api-key",
    target_table="bronze_hubspot_companies",
    source_name="hubspot"
)
print(f"Loaded {count} records")
```

### Silver Transform (Cleaning)

```python
# %% Silver Transform Pattern
from pyspark.sql.functions import col, trim, upper, sha2, concat, lit

# Load source
df = spark.table("bronze_hubspot_companies")

# Get latest records (deduplicate)
from pyspark.sql.window import Window

window = Window.partitionBy("id").orderBy(col("_ingested_at").desc())
df = df.withColumn("_rank", row_number().over(window))
df = df.filter("_rank = 1").drop("_rank")

# Clean and standardize
df = (df
    # Standardize names
    .withColumn("company_name", trim(upper(col("name"))))

    # Parse dates
    .withColumn("created_at", to_timestamp(col("createdAt")))

    # Handle nulls
    .withColumn("industry", coalesce(col("industry"), lit("Unknown")))
)

# Hash PII (if any)
PII_SALT = mssparkutils.credentials.getSecret("kv-dataplatform", "pii-salt")
df = df.withColumn(
    "contact_email_hash",
    sha2(concat(col("contact_email"), lit(PII_SALT)), 256)
).drop("contact_email")

# Write to Silver
df.write.format("delta").mode("overwrite").saveAsTable("silver_companies")
```

### Gold Dimension (SCD Type 2)

```python
# %% Gold Dimension Pattern
from delta.tables import DeltaTable
from pyspark.sql.functions import md5, concat_ws

# Load Silver
df_source = spark.table("silver_companies")

# Add hash for change detection
scd_columns = ["company_name", "industry", "segment"]
df_source = df_source.withColumn(
    "_row_hash",
    md5(concat_ws("||", *[col(c) for c in scd_columns]))
)

# Check if target exists
target_table = "dim_customer"
if spark.catalog.tableExists(target_table):
    # Merge logic for SCD Type 2
    target = DeltaTable.forName(spark, target_table)

    # Expire changed records
    (target.alias("t")
        .merge(df_source.alias("s"), "t.customer_id = s.company_id AND t.is_current = true")
        .whenMatchedUpdate(
            condition="t._row_hash != s._row_hash",
            set={
                "valid_to": current_timestamp(),
                "is_current": lit(False)
            }
        )
        .execute()
    )

    # Insert new/changed records
    new_records = (df_source.alias("s")
        .join(
            spark.table(target_table).filter("is_current = true").alias("t"),
            col("s.company_id") == col("t.customer_id"),
            "left_anti"  # Records not in target
        )
        .union(
            # Changed records (need new version)
            df_source.alias("s").join(
                spark.table(target_table).filter("is_current = true").alias("t"),
                (col("s.company_id") == col("t.customer_id")) &
                (col("s._row_hash") != col("t._row_hash"))
            ).select("s.*")
        )
        .withColumn("valid_from", current_timestamp())
        .withColumn("valid_to", lit("9999-12-31").cast("timestamp"))
        .withColumn("is_current", lit(True))
    )

    new_records.write.format("delta").mode("append").saveAsTable(target_table)

else:
    # Initial load
    (df_source
        .withColumn("valid_from", current_timestamp())
        .withColumn("valid_to", lit("9999-12-31").cast("timestamp"))
        .withColumn("is_current", lit(True))
        .write.format("delta").saveAsTable(target_table)
    )
```

## Data Quality Checks

### Inline Validation

```python
# %% Data Quality Checks
from pyspark.sql.functions import count, when, col

def run_quality_checks(df, table_name: str):
    """Run data quality checks and return results."""

    checks = []

    # Null checks
    for column in ["customer_id", "customer_name"]:
        null_count = df.filter(col(column).isNull()).count()
        checks.append({
            "check": f"{column}_not_null",
            "passed": null_count == 0,
            "details": f"{null_count} null values"
        })

    # Uniqueness check
    total = df.count()
    distinct = df.select("customer_id").distinct().count()
    checks.append({
        "check": "customer_id_unique",
        "passed": total == distinct,
        "details": f"{total - distinct} duplicates"
    })

    # Print results
    for check in checks:
        status = "PASS" if check["passed"] else "FAIL"
        print(f"[{status}] {check['check']}: {check['details']}")

    # Fail if critical checks fail
    critical_failures = [c for c in checks if not c["passed"] and "null" in c["check"]]
    if critical_failures:
        raise ValueError(f"Critical quality checks failed: {critical_failures}")

    return checks

# Execute
run_quality_checks(df, "silver_companies")
```

## Secrets Management

### Key Vault Access

```python
from notebookutils import mssparkutils

# Get single secret
api_key = mssparkutils.credentials.getSecret("kv-dataplatform-dev", "hubspot-api-key")

# Environment-aware
environment = spark.conf.get("spark.env", "dev")
keyvault_name = f"kv-dataplatform-{environment}"
api_key = mssparkutils.credentials.getSecret(keyvault_name, "hubspot-api-key")
```

### Spark Configuration for Secrets

```python
# Set secret in Spark config (for library access)
spark.conf.set("spark.secret.pii_salt",
    mssparkutils.credentials.getSecret("kv-dataplatform", "pii-salt"))

# Read in transformation
SALT = spark.conf.get("spark.secret.pii_salt")
```

## Error Handling

### Try-Except Pattern

```python
import logging
from datetime import datetime

def safe_transform(source_table: str, target_table: str):
    """Transform with error handling."""

    start_time = datetime.now()

    try:
        # Load
        df = spark.table(source_table)

        # Transform
        df_transformed = transform_data(df)

        # Validate
        run_quality_checks(df_transformed, target_table)

        # Write
        df_transformed.write.format("delta").mode("overwrite").saveAsTable(target_table)

        duration = (datetime.now() - start_time).total_seconds()
        logging.info(f"Successfully wrote {df_transformed.count()} records in {duration}s")

    except Exception as e:
        logging.error(f"Transform failed: {e}")
        # Re-raise to fail the notebook (pipeline will catch)
        raise

safe_transform("bronze_companies", "silver_companies")
```

## Parameterization

### Pipeline Parameters

```python
# %% Parameters (set by pipeline)
# These are overwritten when called from a pipeline
source_table = "bronze_hubspot_companies"  # Default for interactive
target_table = "silver_companies"
environment = "dev"
run_date = "2026-02-09"
```

### Using Parameters

```python
# Environment-specific configuration
config = {
    "dev": {"keyvault": "kv-dataplatform-dev", "capacity": "F2"},
    "test": {"keyvault": "kv-dataplatform-test", "capacity": "F2"},
    "prod": {"keyvault": "kv-dataplatform-prod", "capacity": "F4"}
}

keyvault = config[environment]["keyvault"]
```

## Performance Tips

| Tip | Implementation |
|-----|----------------|
| **Limit shuffles** | `spark.conf.set("spark.sql.shuffle.partitions", "8")` |
| **Cache strategically** | `df.cache()` only for reused DataFrames |
| **Filter early** | Apply filters before joins |
| **Use Delta merge** | Instead of delete + insert |
| **Optimize file size** | `OPTIMIZE table_name` after large writes |

## References

- [Fabric Notebooks](https://learn.microsoft.com/fabric/data-engineering/how-to-use-notebook)
- [PySpark in Fabric](https://learn.microsoft.com/fabric/data-engineering/spark-compute)
- [Delta Lake on Fabric](https://learn.microsoft.com/fabric/data-engineering/delta-optimization-and-v-order)

---

*Last Updated: 2026-02-09*
