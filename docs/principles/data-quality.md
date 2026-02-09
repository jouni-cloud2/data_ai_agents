# Data Quality

Principles and patterns for ensuring data quality in data platforms.

## Quality Dimensions

### Core Dimensions

| Dimension | Definition | Example Check |
|-----------|------------|---------------|
| **Accuracy** | Data correctly represents reality | Revenue matches source system |
| **Completeness** | Required data is present | No null values in mandatory fields |
| **Consistency** | Data agrees across systems | Customer count matches between reports |
| **Timeliness** | Data is current enough for use | Data refreshed within SLA |
| **Uniqueness** | No unintended duplicates | One record per primary key |
| **Validity** | Data conforms to rules | Dates are valid, codes are in allowed list |

### Dimension Priority by Layer

| Layer | Priority Dimensions |
|-------|-------------------|
| Bronze | Completeness (all records captured), Timeliness |
| Silver | Uniqueness, Validity, Accuracy |
| Gold | Accuracy, Consistency, Completeness |

## Quality Rules

### Rule Types

| Type | Description | Example |
|------|-------------|---------|
| **Schema** | Structure validation | Column exists, type is correct |
| **Null** | Presence validation | Required fields not null |
| **Uniqueness** | Duplicate detection | Primary key is unique |
| **Range** | Value boundaries | Amount > 0, date < today |
| **Pattern** | Format validation | Email matches regex |
| **Referential** | Foreign key validity | Customer_id exists in dim_customer |
| **Cross-field** | Multi-column logic | End_date > start_date |
| **Statistical** | Distribution checks | Mean within 2 std dev of historical |

### Rule Definition Template

```yaml
rule:
  name: customer_email_valid
  dimension: validity
  table: silver_customers
  column: email
  type: pattern
  check: "email RLIKE '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'"
  severity: warning  # error | warning | info
  action: quarantine  # quarantine | flag | reject
  threshold: 0.95  # 95% must pass
```

## Validation Patterns

### Bronze Layer Validation

Minimal validation - ensure data landed:

```python
# Count validation
source_count = get_api_record_count()
loaded_count = spark.table("bronze_source").count()
assert loaded_count >= source_count * 0.99, "Data loss detected"

# Schema validation
expected_cols = ["id", "name", "created_at"]
actual_cols = spark.table("bronze_source").columns
assert all(col in actual_cols for col in expected_cols)
```

### Silver Layer Validation

Business rules and data quality:

```python
from pyspark.sql.functions import col, when, count

df = spark.table("silver_customers")

# Null checks
null_checks = df.select([
    (count(when(col(c).isNull(), c)) / count("*")).alias(f"{c}_null_rate")
    for c in ["customer_id", "email", "created_at"]
])

# Uniqueness
duplicate_count = df.groupBy("customer_id").count().filter("count > 1").count()
assert duplicate_count == 0, f"Found {duplicate_count} duplicate customers"

# Validity
invalid_emails = df.filter(~col("email").rlike(r"^[\w.+-]+@[\w.-]+\.\w+$")).count()
assert invalid_emails / df.count() < 0.01, "Too many invalid emails"
```

### Gold Layer Validation

Cross-table consistency:

```python
# Referential integrity
orphan_facts = spark.sql("""
    SELECT COUNT(*)
    FROM fact_sales f
    LEFT JOIN dim_customer c ON f.customer_id = c.customer_id
    WHERE c.customer_id IS NULL
""").first()[0]
assert orphan_facts == 0, f"Found {orphan_facts} orphan records"

# Aggregate consistency
fact_total = spark.table("fact_sales").agg(sum("amount")).first()[0]
source_total = spark.table("silver_transactions").agg(sum("amount")).first()[0]
assert abs(fact_total - source_total) < 0.01, "Totals don't match"
```

## Quality Frameworks

### Great Expectations

```python
import great_expectations as gx

context = gx.get_context()
suite = context.add_expectation_suite("silver_customers_suite")

# Define expectations
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToNotBeNull(column="customer_id")
)
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeUnique(column="customer_id")
)
suite.add_expectation(
    gx.expectations.ExpectColumnValuesToMatchRegex(
        column="email",
        regex=r"^[\w.+-]+@[\w.-]+\.\w+$"
    )
)

# Run validation
results = context.run_checkpoint(checkpoint_name="silver_checkpoint")
```

### dbt Tests

```yaml
# models/schema.yml
models:
  - name: silver_customers
    columns:
      - name: customer_id
        tests:
          - not_null
          - unique
      - name: email
        tests:
          - not_null
          - email_format  # custom test
      - name: created_at
        tests:
          - not_null
          - dbt_utils.expression_is_true:
              expression: "created_at <= current_timestamp()"
```

### Platform-Native Tools

| Platform | Quality Tool | Reference |
|----------|-------------|-----------|
| **Fabric** | Data Quality rules in Purview | [Fabric DQ](https://learn.microsoft.com/fabric/governance/use-microsoft-purview-hub) |
| **Databricks** | Unity Catalog constraints, DLT expectations | [DLT Expectations](https://docs.databricks.com/en/delta-live-tables/expectations.html) |
| **Snowflake** | Constraints, custom UDFs | [Snowflake Constraints](https://docs.snowflake.com/en/sql-reference/constraints) |

## Quality Monitoring

### Key Metrics

| Metric | Formula | Target |
|--------|---------|--------|
| **Pass Rate** | Valid records / Total records | >99% for critical tables |
| **Null Rate** | Null values / Total values | <1% for required fields |
| **Duplicate Rate** | Duplicate keys / Total records | 0% for primary keys |
| **Freshness** | Current time - Last update | Within SLA |
| **Completeness** | Present records / Expected records | >99% |

### Monitoring Dashboard

Track these per table/domain:

```
┌─────────────────────────────────────────────────────────────┐
│                 DATA QUALITY DASHBOARD                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Overall Health:  ████████████████░░░░  85%                │
│                                                             │
│  By Dimension:                                              │
│  - Completeness:  ████████████████████  98%                │
│  - Uniqueness:    ████████████████████  100%               │
│  - Validity:      ██████████████░░░░░░  75%  ⚠️            │
│  - Timeliness:    ████████████████████  100%               │
│                                                             │
│  Recent Issues:                                             │
│  ⚠️ silver_orders: 500 invalid currency codes (5%)         │
│  ⚠️ gold_fact_sales: 2 orphan customer references          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Quality Remediation

### Handling Quality Issues

| Severity | Action | Example |
|----------|--------|---------|
| **Error** | Stop pipeline, alert, require fix | Primary key null |
| **Warning** | Log, flag record, continue | Invalid email format |
| **Info** | Log for analysis | Unusual value distribution |

### Quarantine Pattern

```python
# Separate good and bad records
df_valid = df.filter(quality_checks_passed)
df_quarantine = df.filter(~quality_checks_passed)

# Write valid data
df_valid.write.format("delta").mode("append").saveAsTable("silver_orders")

# Write quarantine for review
df_quarantine.write.format("delta").mode("append").saveAsTable("quarantine_orders")

# Alert if quarantine threshold exceeded
if df_quarantine.count() / df.count() > 0.05:
    send_alert("High quarantine rate for orders")
```

## Quality by Design

### Prevention over Detection

| Stage | Quality Activity |
|-------|-----------------|
| **Design** | Define quality rules in catalog before building |
| **Development** | Implement validation in pipeline code |
| **Testing** | Quality gates in CI/CD |
| **Production** | Continuous monitoring and alerting |

### Documentation Requirements

Include in catalog entries:

```markdown
## Data Quality

### Rules
| Rule | Dimension | Threshold | Severity |
|------|-----------|-----------|----------|
| customer_id not null | Completeness | 100% | Error |
| email valid format | Validity | 95% | Warning |
| amount > 0 | Validity | 100% | Error |

### Current Metrics
- Pass Rate: 99.2%
- Last Check: 2026-02-09 06:00 UTC
- Known Issues: None
```

## References

- [Data Quality Fundamentals](https://www.oreilly.com/library/view/data-quality-fundamentals/9781098112035/)
- [Great Expectations](https://greatexpectations.io/)
- [dbt Testing](https://docs.getdbt.com/docs/build/data-tests)
- [Monte Carlo Data Observability](https://www.montecarlodata.com/)

---

*Last Updated: 2026-02-09*
