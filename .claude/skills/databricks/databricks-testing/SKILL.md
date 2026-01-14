---
name: databricks-testing
description: Testing patterns for Databricks implementations.
---

# Databricks Testing Skill

## Test Categories

### 1. Unit Tests
Test individual functions and transformations locally.

### 2. Integration Tests
Test notebook execution and data flow.

### 3. Data Quality Tests
Validate data meets quality requirements.

### 4. Performance Tests
Ensure jobs meet SLA requirements.

## Unit Testing

### Setup with pytest
```python
# tests/conftest.py
import pytest
from pyspark.sql import SparkSession

@pytest.fixture(scope="session")
def spark():
    """Create local Spark session for testing."""
    return SparkSession.builder \
        .master("local[*]") \
        .appName("UnitTests") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()

@pytest.fixture
def sample_accounts(spark):
    """Create sample account data."""
    data = [
        ("ACC001", "Company A", "a@company.com", "active"),
        ("ACC002", "Company B", "b@company.com", "active"),
        ("ACC003", None, "invalid", "inactive"),
    ]
    return spark.createDataFrame(data, ["id", "name", "email", "status"])
```

### Test Transformations
```python
# tests/test_transformations.py
from src.transformations import transform_accounts
from pyspark.sql.functions import col

def test_transform_filters_inactive(spark, sample_accounts):
    """Test that inactive accounts are filtered."""
    result = transform_accounts(sample_accounts)

    assert result.filter(col("status") == "inactive").count() == 0
    assert result.count() == 2

def test_transform_hashes_email(spark, sample_accounts):
    """Test that email is hashed."""
    result = transform_accounts(sample_accounts)

    # Original email removed
    assert "email" not in result.columns
    # Hash column exists
    assert "email_hash" in result.columns
    # Hash is correct format
    assert result.filter(col("email_hash").rlike("^[a-f0-9]{64}$")).count() == result.count()

def test_transform_adds_metadata(spark, sample_accounts):
    """Test that metadata columns are added."""
    result = transform_accounts(sample_accounts)

    assert "_loaded_at" in result.columns
    assert "_source" in result.columns
```

### Test Delta Operations
```python
# tests/test_delta_operations.py
import tempfile
import shutil
from delta.tables import DeltaTable

def test_merge_upsert(spark, sample_accounts):
    """Test merge operation."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Initial load
        sample_accounts.write.format("delta").save(tmpdir)

        # Updates
        updates = spark.createDataFrame([
            ("ACC001", "Company A Updated", "a@company.com", "active"),
            ("ACC004", "Company D", "d@company.com", "active"),
        ], ["id", "name", "email", "status"])

        # Merge
        target = DeltaTable.forPath(spark, tmpdir)
        target.alias("target").merge(
            updates.alias("source"),
            "target.id = source.id"
        ).whenMatchedUpdateAll().whenNotMatchedInsertAll().execute()

        # Verify
        result = spark.read.format("delta").load(tmpdir)
        assert result.count() == 4  # 3 original + 1 new
        assert result.filter("id = 'ACC001' AND name = 'Company A Updated'").count() == 1
```

## Integration Testing

### Test Notebook Execution
```python
# tests/test_notebook_integration.py
import pytest
from databricks.sdk import WorkspaceClient

@pytest.fixture
def workspace_client():
    return WorkspaceClient()

def test_ingest_notebook_executes(workspace_client):
    """Test ingest notebook runs successfully."""
    result = workspace_client.jobs.run_now_and_wait(
        job_id=123,
        notebook_params={"run_date": "2024-01-15"}
    )

    assert result.state.result_state.value == "SUCCESS"

def test_etl_workflow_completes(workspace_client):
    """Test complete ETL workflow."""
    result = workspace_client.jobs.run_now_and_wait(
        job_id=456,
        timeout=timedelta(hours=2)
    )

    assert result.state.result_state.value == "SUCCESS"

    # Verify output tables
    accounts = spark.read.table("production.silver_salesforce.account")
    assert accounts.count() > 0
```

### Test DLT Pipeline
```python
# tests/test_dlt_pipeline.py
def test_dlt_pipeline_succeeds(workspace_client):
    """Test DLT pipeline execution."""
    # Trigger pipeline
    update = workspace_client.pipelines.start_update(
        pipeline_id="pipeline-uuid",
        full_refresh=False
    )

    # Wait for completion
    import time
    while True:
        status = workspace_client.pipelines.get_update(
            pipeline_id="pipeline-uuid",
            update_id=update.update_id
        )
        if status.update.state.value in ["COMPLETED", "FAILED"]:
            break
        time.sleep(30)

    assert status.update.state.value == "COMPLETED"
```

## Data Quality Testing

### Schema Validation
```python
# tests/test_schema.py
def test_bronze_schema(spark):
    """Test Bronze table schema."""
    df = spark.read.table("production.bronze_salesforce.account")

    expected_schema = {
        "account_id": "string",
        "account_name": "string",
        "email": "string",
        "_ingested_at": "timestamp",
        "_source_file": "string"
    }

    actual_schema = {f.name: f.dataType.simpleString() for f in df.schema.fields}

    for col_name, col_type in expected_schema.items():
        assert col_name in actual_schema, f"Missing column: {col_name}"
        assert actual_schema[col_name] == col_type, \
            f"Type mismatch for {col_name}: expected {col_type}, got {actual_schema[col_name]}"

def test_silver_has_no_pii(spark):
    """Test Silver table has no PII columns."""
    df = spark.read.table("production.silver_salesforce.account")

    pii_columns = ["email", "phone", "ssn", "address"]
    for col in pii_columns:
        assert col not in df.columns, f"PII column {col} found in Silver"
```

### Data Completeness
```python
# tests/test_completeness.py
from pyspark.sql.functions import col

def test_required_fields_complete(spark):
    """Test required fields are not null."""
    df = spark.read.table("production.silver_salesforce.account")

    required = ["account_id", "account_name", "_loaded_at"]

    for field in required:
        null_count = df.filter(col(field).isNull()).count()
        assert null_count == 0, f"Found {null_count} nulls in {field}"

def test_data_freshness(spark):
    """Test data is up to date."""
    from datetime import datetime, timedelta

    df = spark.read.table("production.silver_salesforce.account")
    max_loaded = df.agg({"_loaded_at": "max"}).collect()[0][0]

    cutoff = datetime.now() - timedelta(hours=24)
    assert max_loaded > cutoff, f"Data is stale: last load {max_loaded}"
```

### Data Uniqueness
```python
# tests/test_uniqueness.py
def test_primary_key_unique(spark):
    """Test primary keys are unique."""
    df = spark.read.table("production.silver_salesforce.account") \
        .filter("is_current = true")

    total = df.count()
    distinct = df.select("account_id").distinct().count()

    assert total == distinct, f"Found {total - distinct} duplicates"
```

### Referential Integrity
```python
# tests/test_integrity.py
def test_fact_dimension_integrity(spark):
    """Test fact table references valid dimension keys."""
    fact = spark.read.table("production.gold_analytics.fact_sales")
    dim = spark.read.table("production.gold_analytics.dim_customer")

    # Get all customer keys from fact
    fact_keys = fact.select("customer_key").distinct()

    # Get all valid keys from dimension
    dim_keys = dim.select("customer_key").distinct()

    # Find orphans
    orphans = fact_keys.join(dim_keys, "customer_key", "left_anti")

    assert orphans.count() == 0, f"Found {orphans.count()} orphan customer_keys"
```

### DLT Expectations Testing
```python
# tests/test_expectations.py
def test_dlt_expectations_pass(spark):
    """Test DLT expectations are passing."""
    # Query event log
    events = spark.sql("""
        SELECT * FROM event_log(TABLE(production.dlt_salesforce))
        WHERE event_type = 'flow_progress'
        AND details:expectation_results IS NOT NULL
    """)

    for row in events.collect():
        results = row.details["expectation_results"]
        for exp in results:
            assert exp["passed"], f"Expectation failed: {exp['name']}"
```

## Performance Testing

### Query Performance
```python
# tests/test_performance.py
import time

def test_query_performance(spark):
    """Test query meets SLA."""
    start = time.time()

    result = spark.sql("""
        SELECT customer_id, SUM(amount) as total
        FROM production.gold_analytics.fact_sales
        WHERE sale_date >= '2024-01-01'
        GROUP BY customer_id
    """).collect()

    duration = time.time() - start

    assert duration < 30, f"Query took {duration:.2f}s, exceeds 30s SLA"

def test_job_performance(workspace_client):
    """Test job completes within SLA."""
    start = time.time()

    result = workspace_client.jobs.run_now_and_wait(
        job_id=123,
        timeout=timedelta(minutes=60)
    )

    duration = time.time() - start

    assert result.state.result_state.value == "SUCCESS"
    assert duration < 1800, f"Job took {duration/60:.1f}min, exceeds 30min SLA"
```

## Test Execution

### Run Locally
```bash
# Run all tests
pytest tests/ -v

# Run specific file
pytest tests/test_transformations.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html

# Run unit tests only (no integration)
pytest tests/ -v -m "not integration"
```

### Run in Databricks
```python
# %pip install pytest
# Execute in notebook

import pytest
import sys

# Run tests
result = pytest.main([
    "tests/",
    "-v",
    "--tb=short",
    f"--junitxml=/dbfs/test-results/results.xml"
])

# Exit with result code
if result != 0:
    dbutils.notebook.exit("TESTS FAILED")
```

### CI/CD Integration
```yaml
# .github/workflows/test.yml
name: Run Tests

on:
  pull_request:
    branches: [main]

jobs:
  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install pytest pyspark delta-spark
          pip install -e .

      - name: Run unit tests
        run: pytest tests/ -v --ignore=tests/test_integration.py

  integration-tests:
    runs-on: ubuntu-latest
    needs: unit-tests
    steps:
      - uses: actions/checkout@v3

      - name: Run integration tests
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
        run: pytest tests/test_integration.py -v
```

## Test Report Template

```markdown
# Test Results: [Component Name]

**Date**: YYYY-MM-DD
**Environment**: dev/staging/prod

## Summary
- Total Tests: 30
- Passed: 29
- Failed: 1
- Duration: 8m 15s

## Unit Tests
| Test | Status | Duration |
|------|--------|----------|
| test_transform_filters_inactive | PASS | 0.5s |
| test_transform_hashes_email | PASS | 0.4s |

## Integration Tests
| Test | Status | Duration |
|------|--------|----------|
| test_etl_workflow_completes | PASS | 180s |
| test_dlt_pipeline_succeeds | FAIL | 120s |

## Data Quality
| Check | Status | Value |
|-------|--------|-------|
| Completeness | PASS | 99.8% |
| Uniqueness | PASS | 100% |
| Freshness | PASS | 2h ago |

## Performance
| Metric | Value | SLA | Status |
|--------|-------|-----|--------|
| Job Duration | 25min | 30min | PASS |
| Query Time | 8s | 30s | PASS |

## Failures
### test_dlt_pipeline_succeeds
**Error**: Pipeline failed due to schema mismatch
**Root Cause**: Source added new column
**Resolution**: Update schema expectations
```

## Best Practices

- Write tests before code
- Use fixtures for reusable data
- Test both success and failure paths
- Include performance tests
- Run tests in CI/CD
- Generate test reports

## Anti-Patterns

- Don't test in production
- Don't skip integration tests
- Don't ignore flaky tests
- Don't hardcode test data
- Don't forget cleanup
