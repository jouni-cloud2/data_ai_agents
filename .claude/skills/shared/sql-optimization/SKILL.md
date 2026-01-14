---
name: sql-optimization
description: SQL performance optimization techniques for data platforms.
---

# SQL Optimization Skill

## Query Optimization

### 1. Avoid SELECT *
```sql
-- Bad
SELECT * FROM large_table;

-- Good
SELECT id, name, created_at FROM large_table;
```

### 2. Use Predicate Pushdown
```sql
-- Bad (filter after join)
SELECT *
FROM orders o
JOIN customers c ON o.customer_id = c.id
WHERE o.order_date > '2024-01-01';

-- Good (filter before join)
SELECT *
FROM (SELECT * FROM orders WHERE order_date > '2024-01-01') o
JOIN customers c ON o.customer_id = c.id;
```

### 3. Partition Pruning
```sql
-- Good: Uses partition
SELECT * FROM sales
WHERE sale_date BETWEEN '2024-01-01' AND '2024-01-31';

-- Bad: Function prevents partition pruning
SELECT * FROM sales
WHERE YEAR(sale_date) = 2024;
```

### 4. Avoid Functions on Indexed Columns
```sql
-- Bad
SELECT * FROM users WHERE UPPER(email) = 'TEST@EXAMPLE.COM';

-- Good
SELECT * FROM users WHERE email = 'test@example.com';
```

## Join Optimization

### 1. Join Order
```sql
-- Put smaller table first in broadcast scenarios
-- Delta/Spark will optimize, but be explicit when needed

SELECT /*+ BROADCAST(small_table) */
    l.*, s.category
FROM large_table l
JOIN small_table s ON l.id = s.id;
```

### 2. Use Appropriate Join Types
```sql
-- INNER: Both tables have matching rows
SELECT * FROM orders o
INNER JOIN customers c ON o.customer_id = c.id;

-- LEFT: Keep all from left, null if no match
SELECT * FROM customers c
LEFT JOIN orders o ON c.id = o.customer_id;

-- ANTI: Rows in left NOT in right
SELECT * FROM customers c
LEFT ANTI JOIN orders o ON c.id = o.customer_id;
```

### 3. Avoid Cartesian Joins
```sql
-- Bad: No join condition = cartesian product
SELECT * FROM table_a, table_b;

-- Good: Always have join condition
SELECT * FROM table_a a
JOIN table_b b ON a.key = b.key;
```

## Aggregation Optimization

### 1. Filter Before Aggregate
```sql
-- Good
SELECT customer_id, SUM(amount)
FROM orders
WHERE order_date > '2024-01-01'
GROUP BY customer_id;

-- Bad
SELECT customer_id, SUM(amount)
FROM orders
GROUP BY customer_id
HAVING order_date > '2024-01-01';  -- Wrong anyway
```

### 2. Use Approximate Functions for Large Data
```sql
-- Exact (slower)
SELECT COUNT(DISTINCT user_id) FROM events;

-- Approximate (faster, ~2% error)
SELECT APPROX_COUNT_DISTINCT(user_id) FROM events;
```

## Delta Lake Optimization

### 1. Z-Ordering
```sql
-- Optimize for common filter columns
OPTIMIZE table_name
ZORDER BY (customer_id, order_date);
```

**When to Z-Order:**
- Columns frequently in WHERE clauses
- High cardinality columns
- Join columns

### 2. Auto-Optimize
```sql
ALTER TABLE table_name
SET TBLPROPERTIES (
    'delta.autoOptimize.optimizeWrite' = 'true',
    'delta.autoOptimize.autoCompact' = 'true'
);
```

### 3. Vacuum
```sql
-- Remove old files
VACUUM table_name RETAIN 168 HOURS;

-- Check before vacuum
VACUUM table_name DRY RUN;
```

### 4. Analyze Statistics
```sql
-- Compute table statistics
ANALYZE TABLE table_name COMPUTE STATISTICS;

-- Compute column statistics
ANALYZE TABLE table_name COMPUTE STATISTICS FOR COLUMNS col1, col2;
```

### 5. Liquid Clustering (Databricks)
```sql
-- Modern alternative to Z-ordering
ALTER TABLE table_name
CLUSTER BY (customer_id, order_date);
```

## Partitioning Strategies

### 1. Choose Partition Column Wisely
```sql
-- Good: Date-based partitioning for time-series
CREATE TABLE sales (
    id BIGINT,
    amount DECIMAL(18,2),
    sale_date DATE
)
PARTITIONED BY (sale_date);

-- Bad: High cardinality partition
PARTITIONED BY (customer_id);  -- Too many partitions
```

### 2. Partition Size
- Target: 1GB per partition
- Avoid: >10,000 partitions
- Consider: Hierarchical (year/month)

### 3. Query Partitioned Tables
```sql
-- Good: Filters on partition column
SELECT * FROM sales
WHERE sale_date = '2024-01-15';

-- Bad: Scans all partitions
SELECT * FROM sales
WHERE customer_id = 123;
```

## Caching Strategies

### 1. Cache Frequently Used Tables
```python
# Spark
df.cache()
df.persist(StorageLevel.MEMORY_AND_DISK)
```

### 2. Use Delta Caching
```sql
-- Databricks: Result caching
SET spark.databricks.delta.autoCompact.enabled = true;
```

## Common Anti-Patterns

### 1. N+1 Query Pattern
```python
# Bad: Query in loop
for customer_id in customer_ids:
    orders = spark.sql(f"SELECT * FROM orders WHERE customer_id = {customer_id}")

# Good: Single query with IN
orders = spark.sql(f"""
    SELECT * FROM orders
    WHERE customer_id IN ({','.join(map(str, customer_ids))})
""")
```

### 2. UDF Overuse
```python
# Bad: UDF for simple operations
@udf
def add_one(x):
    return x + 1

df.withColumn("new_col", add_one(col("col")))

# Good: Use built-in functions
df.withColumn("new_col", col("col") + 1)
```

### 3. Collect Large Results
```python
# Bad: Brings all data to driver
all_rows = df.collect()

# Good: Use limit or aggregations
sample = df.limit(1000).collect()
count = df.count()
```

## Performance Checklist

Before running:
- [ ] SELECT only needed columns
- [ ] Filter early in query
- [ ] Check partition usage
- [ ] Use appropriate join type
- [ ] Consider broadcast for small tables

After running:
- [ ] Check execution plan (EXPLAIN)
- [ ] Monitor shuffle operations
- [ ] Track query duration
- [ ] Review resource usage
