---
name: fabric-testing
description: Testing patterns for Microsoft Fabric implementations.
---

# Fabric Testing Skill

## Test Categories

### 1. Unit Tests
Test individual functions and transformations.

### 2. Integration Tests
Test pipeline execution end-to-end.

### 3. Data Quality Tests
Validate data meets quality requirements.

### 4. Performance Tests
Ensure pipelines meet SLA requirements.

## Unit Testing

### Test Setup
```python
# tests/conftest.py
import pytest
from pyspark.sql import SparkSession

@pytest.fixture(scope="session")
def spark():
    """Create Spark session for testing."""
    return SparkSession.builder \
        .master("local[*]") \
        .appName("FabricTests") \
        .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension") \
        .config("spark.sql.catalog.spark_catalog", "org.apache.spark.sql.delta.catalog.DeltaCatalog") \
        .getOrCreate()

@pytest.fixture
def sample_data(spark):
    """Create sample test data."""
    data = [
        ("1", "John Doe", "john@example.com", "2024-01-01"),
        ("2", "Jane Smith", "jane@example.com", "2024-01-02"),
        ("3", None, "invalid", "2024-01-03")
    ]
    return spark.createDataFrame(data, ["id", "name", "email", "date"])
```

### Test Transformations
```python
# tests/test_transformations.py
import pytest
from pyspark.sql.functions import col
from notebooks.transform_bronze_silver import transform_account

def test_transform_removes_nulls(spark, sample_data):
    """Test that null names are filtered out."""
    result = transform_account(sample_data)

    assert result.filter(col("name").isNull()).count() == 0

def test_transform_adds_metadata(spark, sample_data):
    """Test that metadata columns are added."""
    result = transform_account(sample_data)

    assert "_silver_loaded_at" in result.columns
    assert "_data_quality_score" in result.columns

def test_transform_masks_email(spark, sample_data):
    """Test that email is hashed."""
    result = transform_account(sample_data)

    # Original email should not exist
    assert "email" not in result.columns
    # Hashed email should exist
    assert "email_hash" in result.columns
    # Hash should be 64 characters (SHA256)
    assert result.filter(col("email_hash").rlike("^[a-f0-9]{64}$")).count() > 0
```

### Test Data Quality Functions
```python
# tests/test_quality.py
from notebooks.quality_checks import calculate_quality_score

def test_quality_score_calculation(spark, sample_data):
    """Test quality score calculation."""
    score = calculate_quality_score(sample_data, {
        "required_columns": ["id", "name"],
        "key_columns": ["id"]
    })

    assert 0 <= score["overall_score"] <= 1
    assert "completeness" in score["dimension_scores"]
    assert "uniqueness" in score["dimension_scores"]

def test_quality_detects_nulls(spark, sample_data):
    """Test that quality checks detect null values."""
    from notebooks.quality_checks import check_completeness

    results = check_completeness(sample_data, ["name"])

    assert results["name"]["null_count"] == 1
    assert results["name"]["completeness"] < 1.0
```

## Integration Testing

### Pipeline Execution Test
```python
# tests/test_pipeline_integration.py
import pytest
import time
from fabric_api import FabricClient

@pytest.fixture
def fabric_client():
    """Create Fabric API client."""
    return FabricClient()

def test_pipeline_executes_successfully(fabric_client):
    """Test that pipeline runs without errors."""
    # Trigger pipeline
    run_id = fabric_client.trigger_pipeline(
        workspace="Sales_Dev",
        pipeline="pl_ingest_salesforce_daily",
        parameters={"watermark": "2024-01-01"}
    )

    # Wait for completion
    status = fabric_client.wait_for_completion(run_id, timeout=1800)

    assert status == "Succeeded"

def test_pipeline_creates_expected_output(fabric_client, spark):
    """Test that pipeline creates expected data."""
    # Run pipeline
    run_id = fabric_client.trigger_pipeline(
        workspace="Sales_Dev",
        pipeline="pl_ingest_salesforce_daily"
    )
    fabric_client.wait_for_completion(run_id)

    # Verify output
    bronze_df = spark.read.table("bronze_salesforce_account")
    silver_df = spark.read.table("silver_salesforce_account")

    assert bronze_df.count() > 0
    assert silver_df.count() > 0
```

### End-to-End Test
```python
# tests/test_e2e.py
def test_full_etl_flow(fabric_client, spark):
    """Test complete Bronze -> Silver -> Gold flow."""
    # 1. Run ingestion
    run_id = fabric_client.trigger_pipeline(
        workspace="Sales_Dev",
        pipeline="pl_etl_salesforce_account"
    )
    status = fabric_client.wait_for_completion(run_id, timeout=3600)
    assert status == "Succeeded"

    # 2. Verify Bronze
    bronze_df = spark.read.format("delta").load("Files/bronze/salesforce/account/")
    assert bronze_df.count() > 0
    assert "_ingested_at" in bronze_df.columns

    # 3. Verify Silver
    silver_df = spark.read.format("delta").load("Files/silver/salesforce/account/")
    assert silver_df.count() > 0
    assert "email_hash" in silver_df.columns
    assert "email" not in silver_df.columns  # PII removed

    # 4. Verify Gold
    gold_df = spark.read.format("delta").load("Files/gold/sales_mart/dim_customer/")
    assert gold_df.count() > 0
    assert "customer_key" in gold_df.columns
```

## Data Quality Testing

### Schema Validation
```python
# tests/test_schema.py
def test_bronze_schema(spark):
    """Test Bronze table has expected schema."""
    df = spark.read.table("bronze_salesforce_account")

    expected_columns = {
        "account_id": "string",
        "account_name": "string",
        "_ingested_at": "timestamp",
        "_source_file": "string",
        "_pipeline_run_id": "string"
    }

    for col_name, col_type in expected_columns.items():
        assert col_name in df.columns
        actual_type = dict(df.dtypes)[col_name]
        assert actual_type == col_type, f"Column {col_name}: expected {col_type}, got {actual_type}"

def test_silver_schema(spark):
    """Test Silver table has expected schema."""
    df = spark.read.table("silver_salesforce_account")

    # Should not have PII columns
    assert "email" not in df.columns
    assert "phone" not in df.columns

    # Should have hashed columns
    assert "email_hash" in df.columns
    assert "phone_hash" in df.columns

    # Should have SCD2 columns
    assert "is_current" in df.columns
    assert "valid_from" in df.columns
    assert "valid_to" in df.columns
```

### Data Completeness Test
```python
# tests/test_completeness.py
def test_required_fields_not_null(spark):
    """Test that required fields are never null."""
    df = spark.read.table("silver_salesforce_account")

    required_fields = ["account_id", "account_name", "_silver_loaded_at"]

    for field in required_fields:
        null_count = df.filter(col(field).isNull()).count()
        assert null_count == 0, f"Found {null_count} nulls in {field}"
```

### Data Uniqueness Test
```python
# tests/test_uniqueness.py
def test_primary_key_unique(spark):
    """Test that primary keys are unique."""
    df = spark.read.table("silver_salesforce_account")

    # For current records
    current_df = df.filter(col("is_current") == True)
    total = current_df.count()
    distinct = current_df.select("account_id").distinct().count()

    assert total == distinct, f"Found {total - distinct} duplicate account_ids"
```

### Data Reconciliation Test
```python
# tests/test_reconciliation.py
def test_bronze_silver_reconciliation(spark):
    """Test that row counts match between layers."""
    bronze_count = spark.read.table("bronze_salesforce_account").count()
    silver_count = spark.read.table("silver_salesforce_account") \
        .filter(col("is_current") == True).count()

    # Allow small variance for quality filtering
    variance = abs(bronze_count - silver_count) / bronze_count
    assert variance < 0.05, f"Row count variance {variance:.2%} exceeds 5%"
```

## Performance Testing

### Query Performance
```python
# tests/test_performance.py
import time

def test_query_performance(spark):
    """Test that queries meet SLA."""
    start = time.time()

    result = spark.sql("""
        SELECT customer_id, SUM(amount) as total
        FROM gold_fact_sales
        WHERE sale_date >= '2024-01-01'
        GROUP BY customer_id
    """).collect()

    duration = time.time() - start

    assert duration < 30, f"Query took {duration:.2f}s, exceeds 30s SLA"

def test_pipeline_performance(fabric_client):
    """Test that pipeline meets duration SLA."""
    start = time.time()

    run_id = fabric_client.trigger_pipeline(
        workspace="Sales_Dev",
        pipeline="pl_etl_salesforce_account"
    )
    fabric_client.wait_for_completion(run_id)

    duration = time.time() - start

    # Pipeline should complete in under 30 minutes
    assert duration < 1800, f"Pipeline took {duration/60:.1f}min, exceeds 30min SLA"
```

## Test Fixtures

### Sample Data Generation
```python
# tests/fixtures/data_generators.py
from pyspark.sql.types import *
from datetime import datetime, timedelta
import random
import string

def generate_account_data(spark, num_records=100):
    """Generate sample account data for testing."""
    data = []
    for i in range(num_records):
        data.append({
            "account_id": f"ACC{i:06d}",
            "account_name": f"Company {i}",
            "email": f"contact{i}@company{i}.com",
            "phone": f"+1{random.randint(1000000000, 9999999999)}",
            "created_date": (datetime.now() - timedelta(days=random.randint(0, 365))).isoformat()
        })

    schema = StructType([
        StructField("account_id", StringType()),
        StructField("account_name", StringType()),
        StructField("email", StringType()),
        StructField("phone", StringType()),
        StructField("created_date", StringType())
    ])

    return spark.createDataFrame(data, schema)
```

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_transformations.py -v

# Run with coverage
pytest tests/ --cov=notebooks --cov-report=html

# Run integration tests only
pytest tests/ -v -m integration

# Run with parallel execution
pytest tests/ -v -n auto
```

## Test Report Template

```markdown
# Test Results: [Pipeline/Table Name]

**Date**: YYYY-MM-DD
**Environment**: Dev/Test/Prod

## Summary
- Total Tests: 25
- Passed: 24
- Failed: 1
- Duration: 5m 32s

## Unit Tests
| Test | Status | Duration |
|------|--------|----------|
| test_transform_removes_nulls | PASS | 0.5s |
| test_transform_adds_metadata | PASS | 0.3s |

## Integration Tests
| Test | Status | Duration |
|------|--------|----------|
| test_pipeline_executes | PASS | 45s |
| test_e2e_flow | FAIL | 120s |

## Data Quality
| Check | Status | Details |
|-------|--------|---------|
| Completeness | PASS | 99.5% |
| Uniqueness | PASS | 100% |
| Validity | PASS | 98.2% |

## Performance
| Metric | Value | SLA | Status |
|--------|-------|-----|--------|
| Pipeline Duration | 25min | 30min | PASS |
| Query Response | 8s | 30s | PASS |

## Failures
### test_e2e_flow
**Error**: AssertionError: Expected 1000 rows, got 998
**Cause**: 2 records failed quality checks
**Resolution**: Investigate source data
```

## Best Practices

- Write tests before implementation
- Use fixtures for reusable test data
- Test both happy path and edge cases
- Include performance tests
- Run tests in CI/CD pipeline
- Generate test reports

## Anti-Patterns

- Don't test in production
- Don't skip integration tests
- Don't ignore flaky tests
- Don't hardcode test data
