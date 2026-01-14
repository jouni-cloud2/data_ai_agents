---
name: data-quality-validation
description: Data quality validation patterns and checks.
---

# Data Quality Validation Skill

## Quality Dimensions

### 1. Completeness
Are all required fields present?

```python
def check_completeness(df, required_columns):
    """Check for null values in required columns."""
    results = {}
    for col_name in required_columns:
        null_count = df.filter(col(col_name).isNull()).count()
        total_count = df.count()
        results[col_name] = {
            "null_count": null_count,
            "completeness": 1 - (null_count / total_count) if total_count > 0 else 0
        }
    return results
```

### 2. Uniqueness
Are primary keys unique?

```python
def check_uniqueness(df, key_columns):
    """Check for duplicate keys."""
    total = df.count()
    distinct = df.select(key_columns).distinct().count()
    duplicate_count = total - distinct

    return {
        "total_rows": total,
        "distinct_keys": distinct,
        "duplicates": duplicate_count,
        "uniqueness": distinct / total if total > 0 else 0
    }
```

### 3. Validity
Do values conform to expected formats?

```python
def check_validity(df, validations):
    """
    Check data validity against rules.

    validations = {
        "email": "^[^@]+@[^@]+\\.[^@]+$",
        "phone": "^\\+?[0-9]{10,15}$",
        "status": ["active", "inactive", "pending"]
    }
    """
    results = {}
    total = df.count()

    for col_name, rule in validations.items():
        if isinstance(rule, list):
            # Enum validation
            valid_count = df.filter(col(col_name).isin(rule)).count()
        else:
            # Regex validation
            valid_count = df.filter(col(col_name).rlike(rule)).count()

        results[col_name] = {
            "valid_count": valid_count,
            "invalid_count": total - valid_count,
            "validity": valid_count / total if total > 0 else 0
        }

    return results
```

### 4. Consistency
Are related fields logically consistent?

```python
def check_consistency(df, rules):
    """
    Check cross-field consistency.

    rules = [
        ("start_date <= end_date", col("start_date") <= col("end_date")),
        ("quantity >= 0", col("quantity") >= 0),
        ("total = price * quantity", col("total") == col("price") * col("quantity"))
    ]
    """
    results = {}
    total = df.count()

    for rule_name, condition in rules:
        valid_count = df.filter(condition).count()
        results[rule_name] = {
            "valid_count": valid_count,
            "invalid_count": total - valid_count,
            "consistency": valid_count / total if total > 0 else 0
        }

    return results
```

### 5. Timeliness
Is data arriving on time?

```python
def check_timeliness(df, timestamp_col, sla_hours=24):
    """Check if data is within SLA."""
    from datetime import datetime, timedelta

    sla_cutoff = datetime.now() - timedelta(hours=sla_hours)

    latest_record = df.agg({timestamp_col: "max"}).collect()[0][0]
    is_timely = latest_record >= sla_cutoff if latest_record else False

    return {
        "latest_record": latest_record,
        "sla_cutoff": sla_cutoff,
        "is_timely": is_timely,
        "hours_since_latest": (datetime.now() - latest_record).total_seconds() / 3600 if latest_record else None
    }
```

### 6. Accuracy
Does data match the source of truth?

```python
def check_accuracy(source_df, target_df, key_columns, compare_columns):
    """Compare source and target for accuracy."""
    joined = source_df.alias("source").join(
        target_df.alias("target"),
        key_columns,
        "full_outer"
    )

    mismatches = []
    for col_name in compare_columns:
        mismatch_count = joined.filter(
            col(f"source.{col_name}") != col(f"target.{col_name}")
        ).count()
        mismatches.append({
            "column": col_name,
            "mismatches": mismatch_count
        })

    return mismatches
```

## Quality Score Calculation

```python
def calculate_quality_score(df, config):
    """
    Calculate overall data quality score.

    config = {
        "required_columns": ["id", "name", "email"],
        "key_columns": ["id"],
        "validations": {"email": "^[^@]+@[^@]+$"},
        "consistency_rules": [("amount >= 0", col("amount") >= 0)],
        "weights": {
            "completeness": 0.3,
            "uniqueness": 0.2,
            "validity": 0.3,
            "consistency": 0.2
        }
    }
    """
    scores = {}

    # Completeness
    completeness_results = check_completeness(df, config["required_columns"])
    scores["completeness"] = sum(r["completeness"] for r in completeness_results.values()) / len(completeness_results)

    # Uniqueness
    uniqueness_results = check_uniqueness(df, config["key_columns"])
    scores["uniqueness"] = uniqueness_results["uniqueness"]

    # Validity
    validity_results = check_validity(df, config["validations"])
    scores["validity"] = sum(r["validity"] for r in validity_results.values()) / len(validity_results)

    # Consistency
    consistency_results = check_consistency(df, config["consistency_rules"])
    scores["consistency"] = sum(r["consistency"] for r in consistency_results.values()) / len(consistency_results)

    # Weighted total
    weights = config["weights"]
    total_score = sum(scores[k] * weights[k] for k in weights.keys())

    return {
        "dimension_scores": scores,
        "overall_score": total_score
    }
```

## Quality Checks by Layer

### Bronze Layer Checks
```python
bronze_checks = {
    "required_columns": ["_ingested_at", "_source_file"],
    "validations": {
        "_ingested_at": "IS NOT NULL"
    }
}
```

### Silver Layer Checks
```python
silver_checks = {
    "required_columns": ["id", "name", "_silver_loaded_at"],
    "key_columns": ["id"],
    "validations": {
        "id": "^[A-Z0-9]+$",
        "email_hash": "^[a-f0-9]{64}$"  # SHA256 format
    },
    "consistency_rules": [
        ("valid_dates", col("start_date") <= col("end_date"))
    ]
}
```

### Gold Layer Checks
```python
gold_checks = {
    "required_columns": ["customer_key", "customer_id"],
    "key_columns": ["customer_key"],
    "referential_integrity": [
        ("fact_sales.customer_key", "dim_customer.customer_key")
    ]
}
```

## DLT Expectations (Databricks)

```python
import dlt

@dlt.table(name="silver_account")
@dlt.expect("valid_id", "account_id IS NOT NULL")
@dlt.expect_or_drop("valid_email", "email RLIKE '^[^@]+@[^@]+$'")
@dlt.expect_or_fail("critical_field", "critical_field IS NOT NULL")
def silver():
    return dlt.read_stream("bronze_account")
```

## Quality Reporting

```python
def generate_quality_report(results, table_name):
    """Generate quality report markdown."""
    report = f"""
# Data Quality Report: {table_name}

**Date**: {datetime.now().isoformat()}
**Overall Score**: {results['overall_score']:.2%}

## Dimension Scores

| Dimension | Score |
|-----------|-------|
| Completeness | {results['dimension_scores']['completeness']:.2%} |
| Uniqueness | {results['dimension_scores']['uniqueness']:.2%} |
| Validity | {results['dimension_scores']['validity']:.2%} |
| Consistency | {results['dimension_scores']['consistency']:.2%} |

## Recommendations

"""
    # Add recommendations based on low scores
    for dim, score in results['dimension_scores'].items():
        if score < 0.95:
            report += f"- Investigate {dim} issues (score: {score:.2%})\n"

    return report
```

## Best Practices

- Run quality checks at every layer transition
- Store quality metrics for trending
- Alert on quality drops
- Quarantine failed records
- Document quality rules

## Anti-Patterns

- Don't skip quality checks for "clean" sources
- Don't use arbitrary thresholds
- Don't ignore quality trends
- Don't quarantine without review process
