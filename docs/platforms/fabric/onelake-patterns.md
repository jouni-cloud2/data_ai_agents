# OneLake Patterns

Storage patterns for Microsoft Fabric's OneLake.

## OneLake Overview

OneLake is Fabric's unified storage layer:
- Single data lake for entire organization
- Automatic Delta format for tables
- Built-in governance and security
- Shortcuts for data virtualization

## Storage Structure

### Lakehouse Organization

```
{lakehouse}/
├── Files/                        # Unstructured/semi-structured data
│   └── landing/                  # Raw file landing zone
│       └── {source}/
│           └── {entity}/
│               └── {date}/
│                   └── data_{timestamp}.json
│
└── Tables/                       # Delta tables (managed)
    ├── bronze_{source}_{entity}  # Raw data tables
    ├── silver_{entity}           # Cleaned tables
    ├── dim_{entity}              # Gold dimensions
    └── fact_{process}            # Gold facts
```

### File Naming

| Scenario | Pattern | Example |
|----------|---------|---------|
| API landing | `{entity}_{timestamp}.json` | `companies_20260209_120000.json` |
| Batch export | `{entity}_{date}.parquet` | `transactions_2026-02-09.parquet` |
| Incremental | `{entity}_{batch_id}.json` | `events_batch_1234.json` |

## OneLake Paths

### URL Formats

```python
# ABFS path (for Spark)
abfss://{workspace_id}@onelake.dfs.fabric.microsoft.com/{item_id}/Tables/{table}
abfss://{workspace_id}@onelake.dfs.fabric.microsoft.com/{item_id}/Files/{path}

# HTTP path (for REST API)
https://onelake.dfs.fabric.microsoft.com/{workspace_id}/{item_id}/Tables/{table}

# Shorthand in notebooks (within same lakehouse)
spark.table("table_name")
spark.read.format("delta").load("Tables/table_name")
spark.read.json("Files/landing/source/entity/")
```

### Path Construction

```python
from notebookutils import mssparkutils

# Get current lakehouse info
workspace_id = mssparkutils.lakehouse.get("workspaceId")
lakehouse_id = mssparkutils.lakehouse.get("id")

# Construct paths
tables_path = f"abfss://{workspace_id}@onelake.dfs.fabric.microsoft.com/{lakehouse_id}/Tables"
files_path = f"abfss://{workspace_id}@onelake.dfs.fabric.microsoft.com/{lakehouse_id}/Files"
```

## Working with Files

### Writing Files

```python
import json
from datetime import datetime

def write_json_to_files(data: list, folder_path: str, entity_name: str):
    """Write JSON data to Files folder."""

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = f"Files/{folder_path}/{entity_name}_{timestamp}.json"

    # Using Spark
    df = spark.createDataFrame(data)
    df.write.mode("overwrite").json(file_path)

    # Or using mssparkutils
    mssparkutils.fs.put(file_path, json.dumps(data), overwrite=True)

# Usage
write_json_to_files(api_data, "landing/hubspot/companies", "companies")
```

### Reading Files

```python
# Read all JSON files from folder
df = spark.read.json("Files/landing/hubspot/companies/")

# Read specific date partition
df = spark.read.json("Files/landing/hubspot/companies/2026-02-09/")

# Read with schema
from pyspark.sql.types import StructType, StructField, StringType

schema = StructType([
    StructField("id", StringType()),
    StructField("name", StringType())
])
df = spark.read.schema(schema).json("Files/landing/hubspot/companies/")
```

### Listing Files

```python
from notebookutils import mssparkutils

# List files in folder
files = mssparkutils.fs.ls("Files/landing/hubspot/companies/")
for file in files:
    print(f"{file.name} - {file.size} bytes")

# Check if file exists
exists = mssparkutils.fs.exists("Files/landing/hubspot/companies/data.json")
```

## Working with Tables

### Creating Tables

```python
# From DataFrame
df.write.format("delta").mode("overwrite").saveAsTable("bronze_companies")

# With partitioning
df.write.format("delta") \
    .partitionBy("ingestion_date") \
    .mode("overwrite") \
    .saveAsTable("bronze_companies")

# With options
df.write.format("delta") \
    .option("mergeSchema", "true") \
    .mode("append") \
    .saveAsTable("bronze_companies")
```

### Table Optimization

```python
# Optimize (compact small files)
spark.sql("OPTIMIZE bronze_companies")

# Z-Order (optimize for specific columns)
spark.sql("OPTIMIZE silver_companies ZORDER BY (customer_id)")

# Vacuum (remove old files)
spark.sql("VACUUM bronze_companies RETAIN 168 HOURS")  # 7 days
```

### Table Maintenance

```python
# Check table history
spark.sql("DESCRIBE HISTORY bronze_companies").show()

# Time travel (read old version)
df_old = spark.read.format("delta") \
    .option("versionAsOf", 5) \
    .table("bronze_companies")

# Restore to previous version
spark.sql("RESTORE TABLE bronze_companies TO VERSION AS OF 5")
```

## Shortcuts

### What are Shortcuts?

Shortcuts create virtual links to data in other locations:
- Other lakehouses (same or different workspace)
- Azure Data Lake Storage Gen2
- Amazon S3
- Google Cloud Storage

### Creating Shortcuts (API)

```python
import requests

def create_onelake_shortcut(
    workspace_id: str,
    lakehouse_id: str,
    shortcut_name: str,
    source_workspace_id: str,
    source_lakehouse_id: str,
    source_path: str
):
    """Create shortcut to another OneLake location."""

    url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/items/{lakehouse_id}/shortcuts"

    payload = {
        "name": shortcut_name,
        "path": "Tables",  # or "Files"
        "target": {
            "oneLake": {
                "workspaceId": source_workspace_id,
                "itemId": source_lakehouse_id,
                "path": source_path
            }
        }
    }

    response = requests.post(url, json=payload, headers=get_auth_headers())
    return response.json()
```

### Shortcut Use Cases

| Use Case | Source | Target |
|----------|--------|--------|
| **Cross-domain analytics** | Domain Gold tables | Analytics workspace |
| **External data lake** | ADLS Gen2 | Fabric lakehouse |
| **Multi-cloud** | S3 bucket | Fabric lakehouse |

## Data Formats

### Supported Formats

| Format | Use Case | Read | Write |
|--------|----------|------|-------|
| **Delta** | Tables (default) | Yes | Yes |
| **Parquet** | Files | Yes | Yes |
| **JSON** | API landing | Yes | Yes |
| **CSV** | Legacy systems | Yes | Yes |
| **Avro** | Streaming | Yes | Yes |

### Format Conversion

```python
# JSON to Delta table
spark.read.json("Files/landing/source/").write.format("delta").saveAsTable("bronze_table")

# Parquet to Delta
spark.read.parquet("Files/exports/").write.format("delta").saveAsTable("silver_table")

# CSV with options
spark.read.option("header", "true").option("inferSchema", "true") \
    .csv("Files/imports/data.csv") \
    .write.format("delta").saveAsTable("bronze_csv_data")
```

## Access Control

### OneLake RBAC

| Level | Control |
|-------|---------|
| Workspace | Admin/Member/Contributor/Viewer roles |
| Lakehouse | Read/ReadWrite permissions |
| Table | Row-level security via SQL |

### Setting Permissions

```python
# Via Fabric REST API
def set_lakehouse_permissions(workspace_id: str, lakehouse_id: str, principal_id: str, role: str):
    """Set lakehouse permissions."""

    url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/items/{lakehouse_id}/permissions"

    payload = {
        "principal": {"id": principal_id, "type": "User"},
        "role": role  # "Read" or "ReadWrite"
    }

    response = requests.post(url, json=payload, headers=get_auth_headers())
    return response.json()
```

## Best Practices

| Practice | Rationale |
|----------|-----------|
| **Use Tables for structured data** | Automatic Delta optimization |
| **Use Files for landing** | Flexibility, schema-on-read |
| **Partition by date** | Query performance |
| **Regular OPTIMIZE** | Prevent small file problem |
| **VACUUM with retention** | Clean up old versions |
| **Shortcuts for cross-domain** | Avoid data duplication |

## Monitoring

### Storage Metrics

```python
# Check table size
spark.sql("DESCRIBE DETAIL bronze_companies").show()

# Check file count
files = mssparkutils.fs.ls("Tables/bronze_companies/")
print(f"File count: {len(files)}")

# Check partition sizes
spark.sql("""
    SELECT _ingestion_date, COUNT(*) as records
    FROM bronze_companies
    GROUP BY _ingestion_date
    ORDER BY _ingestion_date DESC
""").show()
```

## References

- [OneLake Overview](https://learn.microsoft.com/fabric/onelake/onelake-overview)
- [OneLake Shortcuts](https://learn.microsoft.com/fabric/onelake/onelake-shortcuts)
- [Delta Lake Optimization](https://learn.microsoft.com/fabric/data-engineering/delta-optimization-and-v-order)

---

*Last Updated: 2026-02-09*
