# SCD Type 2 Pattern

Slowly Changing Dimension Type 2 - Track historical changes to dimension attributes.

## Problem

Dimension attributes change over time, and you need to:
- Track the history of changes
- Know which value was active at any point in time
- Support both current and historical analysis

## Solution

Maintain multiple versions of each dimension record with validity periods.

```
┌─────────────────────────────────────────────────────────────────┐
│                    SCD TYPE 2 CONCEPT                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Customer "ACME Corp" changes industry from "Tech" to "Finance"│
│                                                                 │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │ SK │ ID   │ Name  │ Industry │ Valid From │ Valid To │ Curr ││
│  ├────┼──────┼───────┼──────────┼────────────┼──────────┼──────┤│
│  │ 1  │ C001 │ ACME  │ Tech     │ 2024-01-01 │ 2025-06-30│ N   ││
│  │ 2  │ C001 │ ACME  │ Finance  │ 2025-07-01 │ 9999-12-31│ Y   ││
│  └─────────────────────────────────────────────────────────────┘│
│                                                                 │
│  Facts from 2024 link to SK=1 (Tech)                           │
│  Facts from 2025 link to SK=2 (Finance)                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Schema Design

### Dimension Table Structure

```sql
CREATE TABLE dim_customer (
    -- Surrogate key (auto-generated)
    customer_sk BIGINT GENERATED ALWAYS AS IDENTITY,

    -- Natural/business key
    customer_id STRING NOT NULL,

    -- Dimension attributes (Type 2 - tracked)
    customer_name STRING,
    industry STRING,
    segment STRING,
    account_manager STRING,

    -- Type 1 attributes (overwritten, not tracked)
    email STRING,
    phone STRING,

    -- SCD Type 2 metadata
    valid_from TIMESTAMP NOT NULL,
    valid_to TIMESTAMP NOT NULL,
    is_current BOOLEAN NOT NULL,

    -- Audit columns
    created_at TIMESTAMP,
    updated_at TIMESTAMP,

    -- Hash for change detection
    row_hash STRING
);

-- Indexes
CREATE INDEX idx_customer_natural_key ON dim_customer (customer_id, is_current);
CREATE INDEX idx_customer_validity ON dim_customer (customer_id, valid_from, valid_to);
```

### End Date Convention

| Convention | Valid To (End) | Pros | Cons |
|------------|---------------|------|------|
| **High date** | `9999-12-31` | Simple queries | Magic value |
| **NULL** | `NULL` | Explicit | Complex WHERE |
| **is_current flag** | Any + flag | Clear | Redundant |

**Recommended:** Use high date `9999-12-31` with `is_current` flag for clarity.

## Implementation

### Full SCD Type 2 Logic

```python
from pyspark.sql.functions import (
    col, lit, current_timestamp, md5, concat_ws,
    when, coalesce, row_number
)
from pyspark.sql.window import Window
from delta.tables import DeltaTable

def apply_scd_type_2(
    source_df,
    target_table: str,
    natural_key: str,
    tracked_columns: list,
    type_1_columns: list = None
):
    """Apply SCD Type 2 changes to dimension table."""

    HIGH_DATE = "9999-12-31 23:59:59"
    type_1_columns = type_1_columns or []

    # Add row hash for change detection (tracked columns only)
    source_with_hash = source_df.withColumn(
        "row_hash",
        md5(concat_ws("||", *[col(c) for c in tracked_columns]))
    )

    # Check if target exists
    if not spark.catalog.tableExists(target_table):
        # Initial load
        initial_df = (
            source_with_hash
            .withColumn("valid_from", current_timestamp())
            .withColumn("valid_to", lit(HIGH_DATE).cast("timestamp"))
            .withColumn("is_current", lit(True))
            .withColumn("created_at", current_timestamp())
            .withColumn("updated_at", current_timestamp())
        )
        initial_df.write.format("delta").saveAsTable(target_table)
        return

    # Get current records from target
    target = DeltaTable.forName(spark, target_table)
    current_df = spark.table(target_table).filter("is_current = true")

    # Join source with current target
    joined = source_with_hash.alias("source").join(
        current_df.alias("target"),
        col(f"source.{natural_key}") == col(f"target.{natural_key}"),
        "full_outer"
    )

    # Identify changes
    changes = joined.withColumn(
        "change_type",
        when(col(f"target.{natural_key}").isNull(), "INSERT")
        .when(col(f"source.{natural_key}").isNull(), "DELETE")
        .when(col("source.row_hash") != col("target.row_hash"), "UPDATE")
        .otherwise("NO_CHANGE")
    )

    # Process new records (INSERT)
    new_records = (
        changes.filter("change_type = 'INSERT'")
        .select([col(f"source.{c}") for c in source_with_hash.columns])
        .withColumn("valid_from", current_timestamp())
        .withColumn("valid_to", lit(HIGH_DATE).cast("timestamp"))
        .withColumn("is_current", lit(True))
        .withColumn("created_at", current_timestamp())
        .withColumn("updated_at", current_timestamp())
    )

    # Process updated records (UPDATE) - new version
    updated_new = (
        changes.filter("change_type = 'UPDATE'")
        .select([col(f"source.{c}") for c in source_with_hash.columns])
        .withColumn("valid_from", current_timestamp())
        .withColumn("valid_to", lit(HIGH_DATE).cast("timestamp"))
        .withColumn("is_current", lit(True))
        .withColumn("created_at", current_timestamp())
        .withColumn("updated_at", current_timestamp())
    )

    # Expire old versions (UPDATE)
    expire_keys = changes.filter("change_type = 'UPDATE'").select(
        col(f"target.{natural_key}").alias(natural_key)
    )

    # Apply Type 1 updates (overwrite current record)
    if type_1_columns:
        type_1_updates = changes.filter("change_type = 'NO_CHANGE'").select(
            col(f"target.{natural_key}"),
            *[col(f"source.{c}").alias(c) for c in type_1_columns]
        )

    # Execute merge
    now = current_timestamp()

    (
        target.alias("target")
        .merge(
            expire_keys.alias("expire"),
            f"target.{natural_key} = expire.{natural_key} AND target.is_current = true"
        )
        .whenMatchedUpdate(set={
            "valid_to": now,
            "is_current": lit(False),
            "updated_at": now
        })
        .execute()
    )

    # Insert new versions
    new_records.union(updated_new).write.format("delta").mode("append").saveAsTable(target_table)

    print(f"SCD Type 2 applied: {new_records.count()} inserts, {updated_new.count()} updates")
```

### Simplified Version with Delta MERGE

```python
def scd_type_2_delta(
    source_df,
    target_table: str,
    natural_key: str,
    scd_columns: list
):
    """Simplified SCD Type 2 using Delta MERGE."""

    from delta.tables import DeltaTable

    # Hash for change detection
    source_with_hash = source_df.withColumn(
        "_hash", md5(concat_ws("||", *[col(c) for c in scd_columns]))
    )

    target = DeltaTable.forName(spark, target_table)

    # Merge: expire old, insert new
    (
        target.alias("t")
        .merge(
            source_with_hash.alias("s"),
            f"t.{natural_key} = s.{natural_key} AND t.is_current = true"
        )
        # When matched and changed: expire old record
        .whenMatchedUpdate(
            condition="t._hash != s._hash",
            set={
                "valid_to": current_timestamp(),
                "is_current": lit(False)
            }
        )
        # When not matched: insert new record
        .whenNotMatchedInsert(values={
            **{c: f"s.{c}" for c in source_df.columns},
            "valid_from": current_timestamp(),
            "valid_to": lit("9999-12-31").cast("timestamp"),
            "is_current": lit(True),
            "_hash": "s._hash"
        })
        .execute()
    )

    # Insert new versions for updated records
    # (Need a second pass to insert new versions)
```

## Querying SCD Type 2

### Current State

```sql
-- Get current dimension values
SELECT *
FROM dim_customer
WHERE is_current = true;
```

### Point-in-Time Query

```sql
-- Get dimension values as of specific date
SELECT *
FROM dim_customer
WHERE valid_from <= '2024-06-15'
  AND valid_to > '2024-06-15';
```

### Joining with Facts

```sql
-- Join fact to dimension at transaction time
SELECT
    f.transaction_id,
    f.amount,
    f.transaction_date,
    d.customer_name,
    d.industry  -- Industry at time of transaction
FROM fact_sales f
JOIN dim_customer d
    ON f.customer_id = d.customer_id
   AND f.transaction_date >= d.valid_from
   AND f.transaction_date < d.valid_to;
```

## Platform Variations

### Databricks Delta Live Tables

```python
import dlt
from pyspark.sql.functions import *

@dlt.table
def dim_customer():
    """SCD Type 2 dimension with Delta Live Tables."""
    return (
        dlt.apply_changes(
            target="dim_customer",
            source="staged_customers",
            keys=["customer_id"],
            sequence_by="updated_at",
            stored_as_scd_type=2,
            track_history_column_list=["industry", "segment", "account_manager"]
        )
    )
```

### Snowflake Streams + Tasks

```sql
-- Merge procedure for SCD Type 2
CREATE OR REPLACE PROCEDURE apply_scd_type_2()
RETURNS STRING
LANGUAGE SQL
AS
$$
BEGIN
    -- Expire changed records
    UPDATE dim_customer t
    SET valid_to = CURRENT_TIMESTAMP(),
        is_current = FALSE
    FROM customer_changes s
    WHERE t.customer_id = s.customer_id
      AND t.is_current = TRUE
      AND (t.industry != s.industry OR t.segment != s.segment);

    -- Insert new versions
    INSERT INTO dim_customer
    SELECT
        s.*,
        CURRENT_TIMESTAMP() AS valid_from,
        '9999-12-31'::TIMESTAMP AS valid_to,
        TRUE AS is_current
    FROM customer_changes s
    LEFT JOIN dim_customer t
        ON s.customer_id = t.customer_id AND t.is_current = TRUE
    WHERE t.customer_id IS NULL
       OR t.industry != s.industry
       OR t.segment != s.segment;

    RETURN 'SCD Type 2 applied';
END;
$$;
```

## SCD Type Comparison

| Type | Behavior | History | Use Case |
|------|----------|---------|----------|
| **Type 0** | Never change | Original only | Static codes |
| **Type 1** | Overwrite | None | Corrections |
| **Type 2** | New row | Full history | Analysis over time |
| **Type 3** | Previous column | Last value only | Simple history |
| **Type 4** | Mini-dimension | Separate table | Rapidly changing |
| **Type 6** | Hybrid 1+2+3 | Complex | Special cases |

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| **Using business key as PK** | Can't have multiple versions | Use surrogate key |
| **Joining on business key only** | Wrong version linked | Join on validity period |
| **No change detection** | Creates duplicates | Hash comparison |
| **Tracking all columns** | Excessive history | Select meaningful columns |

## References

- [Kimball SCD Types](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/type-1-2-3/)
- [Delta Lake SCD Type 2](https://docs.databricks.com/en/delta-live-tables/python-ref.html#scd-type-2)
- [Snowflake SCD Patterns](https://docs.snowflake.com/en/user-guide/streams-examples)

---

*Last Updated: 2026-02-09*
