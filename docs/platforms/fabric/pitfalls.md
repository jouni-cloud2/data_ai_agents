# Fabric Pitfalls

Common mistakes and gotchas when working with Microsoft Fabric.

## Notebook Pitfalls

### Forgetting to Set Default Lakehouse

**Problem**: Notebook runs fail with "table not found" errors.

**Solution**: Always attach a lakehouse before running:
```python
# Check current lakehouse
from notebookutils import mssparkutils
print(mssparkutils.lakehouse.get("name"))

# Or ensure lakehouse is attached in notebook settings
```

### Hardcoding Workspace/Lakehouse IDs

**Problem**: Code breaks when moving between environments.

**Bad**:
```python
path = "abfss://12345@onelake.dfs.fabric.microsoft.com/67890/Tables/..."
```

**Good**:
```python
# Let Fabric resolve the path
df = spark.table("bronze_companies")

# Or use relative paths
df = spark.read.json("Files/landing/")
```

### Not Handling Schema Evolution

**Problem**: Pipeline fails when source adds new columns.

**Solution**: Enable schema merge:
```python
df.write.format("delta") \
    .option("mergeSchema", "true") \
    .mode("append") \
    .saveAsTable("bronze_table")
```

### Using `display()` in Production

**Problem**: `display()` loads data into memory, slowing pipelines.

**Bad**:
```python
display(df)  # Loads all data
```

**Good**:
```python
# For debugging only
if is_interactive:
    display(df.limit(10))

# For production, just count
print(f"Rows: {df.count()}")
```

## Table Pitfalls

### Small File Problem

**Problem**: Many small files degrade query performance.

**Cause**: Frequent small writes or high partition cardinality.

**Solution**:
```python
# Compact files regularly
spark.sql("OPTIMIZE large_table")

# Or during write
df.coalesce(10).write.format("delta").mode("append").saveAsTable("table")
```

### Over-Partitioning

**Problem**: Too many partitions create too many small files.

**Bad**:
```python
df.write.partitionBy("customer_id", "date", "hour").saveAsTable("table")
```

**Good**:
```python
# Partition by date only (unless high cardinality needed)
df.write.partitionBy("date").saveAsTable("table")

# Use Z-ORDER for additional columns
spark.sql("OPTIMIZE table ZORDER BY (customer_id)")
```

### Forgetting VACUUM

**Problem**: Old Delta versions consume storage indefinitely.

**Solution**:
```python
# Regular vacuum (weekly)
spark.sql("VACUUM table_name RETAIN 168 HOURS")  # 7 days

# Check retention setting
spark.sql("DESCRIBE DETAIL table_name").select("properties").show()
```

## Pipeline Pitfalls

### No Retry on Transient Failures

**Problem**: Pipelines fail on temporary network issues.

**Solution**: Configure retries:
```json
{
    "policy": {
        "retry": 3,
        "retryIntervalInSeconds": 30
    }
}
```

### Hardcoding Secrets

**Problem**: Secrets in pipeline JSON or notebook code.

**Bad**:
```json
{"Authorization": "Bearer abc123secret"}
```

**Good**:
```python
# Use Key Vault
api_key = mssparkutils.credentials.getSecret("keyvault", "secret-name")
```

### Not Setting Timeouts

**Problem**: Stuck activities run forever.

**Solution**:
```json
{
    "policy": {
        "timeout": "01:00:00"
    }
}
```

### Missing Dependency Conditions

**Problem**: Downstream activities run even when upstream fails.

**Solution**: Use proper dependency conditions:
```json
{
    "dependsOn": [
        {
            "activity": "Upstream",
            "dependencyConditions": ["Succeeded"]
        }
    ]
}
```

## Git Integration Pitfalls

### Missing `.platform` File for New Artifacts

**Problem**: New notebooks, lakehouses, or pipelines created in Git are silently ignored by Fabric Git integration.

**Cause**: Every Fabric artifact tracked in Git must include a `.platform` file alongside its content file. Without it, Fabric Git sync does not recognize the item exists.

**Symptom**: Artifact is visible in Git repo but never appears in Fabric workspace after sync.

**Bad** (notebook folder without `.platform`):
```
fabric/it/notebooks/
└── my_notebook.Notebook/
    └── notebook-content.py          ← Only content, no .platform
```

**Good**:
```
fabric/it/notebooks/
└── my_notebook.Notebook/
    ├── .platform                    ← Required!
    └── notebook-content.py
```

**`.platform` format** (notebook):
```json
{
  "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
  "metadata": {
    "type": "Notebook",
    "displayName": "my_notebook"
  },
  "config": {
    "version": "2.0",
    "logicalId": "<uuid4>"
  }
}
```

**Rule**: Always create `.platform` whenever you create a new Fabric artifact folder. Check with:
```bash
find fabric/ -name "*.Notebook" -type d | while read d; do
  [ -f "$d/.platform" ] || echo "MISSING .platform: $d"
done
```

### Sync Conflicts

**Problem**: UI changes conflict with Git changes.

**Solution**:
- Always pull before making UI changes
- Use single direction: Git → Fabric (not both)
- Establish team workflow

### Large Commits

**Problem**: Sync takes too long or fails.

**Solution**:
- Commit frequently
- Avoid large binary files
- Split large changes

### Not Using Branches

**Problem**: Dev changes accidentally go to production.

**Solution**:
```
main (prod) ← test ← dev ← feature/*
```

## Performance Pitfalls

### Reading Full Tables Unnecessarily

**Problem**: Slow queries that scan entire tables.

**Bad**:
```python
df = spark.table("large_table")
df = df.filter(col("date") == "2026-02-09")
```

**Good**:
```python
# Predicate pushdown with partition column
df = spark.table("large_table").filter(col("date") == "2026-02-09")

# Or use SQL with partition filter
df = spark.sql("SELECT * FROM large_table WHERE date = '2026-02-09'")
```

### Not Caching Reused DataFrames

**Problem**: Same data read multiple times.

**Bad**:
```python
df = spark.table("source")
count = df.count()
summary = df.groupBy("category").count()  # Reads again
```

**Good**:
```python
df = spark.table("source").cache()
count = df.count()
summary = df.groupBy("category").count()  # Uses cache
df.unpersist()  # Clean up
```

### Too Many Shuffle Partitions

**Problem**: Default 200 partitions is too many for small datasets.

**Solution**:
```python
# Set appropriate partition count
spark.conf.set("spark.sql.shuffle.partitions", 8)  # For small data
```

## Capacity Pitfalls

### Ignoring Capacity Limits

**Problem**: Jobs fail or throttle unexpectedly.

**Monitor**:
- Fabric capacity metrics in Admin portal
- Smoothed CU consumption

**Solution**:
- Schedule large jobs during off-peak hours
- Request capacity increase if needed

### Not Using Appropriate Capacity

**Problem**: Dev workloads on production capacity.

**Solution**:
- Assign workspaces to appropriate capacities
- Use smaller capacity for dev/test
- Consider serverless for burst workloads

## Security Pitfalls

### Overly Permissive Access

**Problem**: Everyone has admin access.

**Solution**:
```
Prod workspace: Admin = Platform team only
                Viewer = Business users
                No Member/Contributor
```

### Not Classifying Data

**Problem**: Sensitive data treated like public data.

**Solution**: Classify at ingestion, enforce in Silver/Gold:
```python
# Bronze: mark classification
df = df.withColumn("_data_classification", lit("confidential"))

# Silver: hash PII
df = df.withColumn("email_hash", sha2(col("email"), 256)).drop("email")
```

### Logging Secrets

**Problem**: Secrets appear in logs.

**Bad**:
```python
print(f"Using API key: {api_key}")
```

**Good**:
```python
print(f"Using API key: ***hidden***")
```

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "AnalysisException: Table not found" | Lakehouse not attached | Attach lakehouse in notebook settings |
| "403 Forbidden" | Missing permissions | Check workspace/lakehouse roles |
| "Concurrent update conflict" | Multiple writers to same table | Use Delta MERGE or serialization |
| "Container not found" | Workspace/lakehouse deleted | Verify IDs, check trash |
| "Rate limit exceeded" | Too many API calls | Implement rate limiting |

## Debugging Tips

```python
# Check current environment
print(f"Workspace: {mssparkutils.lakehouse.get('workspaceId')}")
print(f"Lakehouse: {mssparkutils.lakehouse.get('name')}")

# Check table location
spark.sql("DESCRIBE DETAIL table_name").show()

# Check Delta log
spark.sql("DESCRIBE HISTORY table_name LIMIT 10").show()

# Check Spark config
spark.sparkContext.getConf().getAll()
```

---

*Last Updated: 2026-02-09*
