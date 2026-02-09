# Error Handling Pattern

Build resilient data pipelines with proper error handling, retries, and alerting.

## Problem

Data pipelines fail due to:
- Transient network/API issues
- Data quality problems
- Resource constraints
- Upstream system outages

Without proper handling, failures cause:
- Data loss or inconsistency
- Silent failures (no one knows)
- Cascading downstream failures

## Solution

Implement defense in depth:

```
┌─────────────────────────────────────────────────────────────────┐
│                    ERROR HANDLING LAYERS                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐                                               │
│  │   RETRY      │ ←── Transient failures (network, rate limit) │
│  └──────┬───────┘                                               │
│         ▼                                                       │
│  ┌──────────────┐                                               │
│  │  QUARANTINE  │ ←── Bad records (validation failures)        │
│  └──────┬───────┘                                               │
│         ▼                                                       │
│  ┌──────────────┐                                               │
│  │  DEAD LETTER │ ←── Unrecoverable records                    │
│  └──────┬───────┘                                               │
│         ▼                                                       │
│  ┌──────────────┐                                               │
│  │    ALERT     │ ←── Notify on threshold breaches             │
│  └──────────────┘                                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Retry Pattern

### Exponential Backoff

```python
import time
from functools import wraps
from typing import Callable, TypeVar, Any

T = TypeVar('T')

def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    retryable_exceptions: tuple = (Exception,)
) -> Callable:
    """Decorator for retrying functions with exponential backoff."""

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        delay = min(
                            base_delay * (exponential_base ** attempt),
                            max_delay
                        )
                        print(f"Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                    else:
                        print(f"All {max_retries} attempts failed")
                        raise

            raise last_exception

        return wrapper
    return decorator

# Usage
@retry_with_backoff(max_retries=3, retryable_exceptions=(ConnectionError, TimeoutError))
def fetch_api_data(endpoint: str) -> dict:
    response = requests.get(endpoint, timeout=30)
    response.raise_for_status()
    return response.json()
```

### Retry for Specific HTTP Codes

```python
RETRYABLE_STATUS_CODES = {429, 500, 502, 503, 504}

def fetch_with_retry(url: str, max_retries: int = 3) -> dict:
    """Retry on specific HTTP status codes."""

    for attempt in range(max_retries):
        response = requests.get(url)

        if response.status_code in RETRYABLE_STATUS_CODES:
            if attempt < max_retries - 1:
                # Check for Retry-After header
                retry_after = response.headers.get('Retry-After', 2 ** attempt)
                time.sleep(float(retry_after))
                continue

        response.raise_for_status()
        return response.json()

    raise Exception(f"Failed after {max_retries} retries")
```

## Quarantine Pattern

### Separate Good and Bad Records

```python
from pyspark.sql.functions import col, when, lit

def process_with_quarantine(
    df,
    validation_rules: dict,
    good_table: str,
    quarantine_table: str
):
    """Process data with quarantine for bad records."""

    # Apply validation rules
    validation_col = lit(True)
    failure_reasons = []

    for rule_name, rule_condition in validation_rules.items():
        validation_col = validation_col & rule_condition
        failure_reasons.append(
            when(~rule_condition, lit(rule_name))
        )

    # Add validation result
    df_validated = df.withColumn("_is_valid", validation_col)
    df_validated = df_validated.withColumn(
        "_failure_reason",
        coalesce(*failure_reasons, lit(None))
    )

    # Split into good and bad
    df_good = df_validated.filter("_is_valid = true").drop("_is_valid", "_failure_reason")
    df_quarantine = df_validated.filter("_is_valid = false")

    # Write good records
    df_good.write.format("delta").mode("append").saveAsTable(good_table)

    # Write quarantine records
    if df_quarantine.count() > 0:
        df_quarantine.withColumn("_quarantined_at", current_timestamp()).write \
            .format("delta").mode("append").saveAsTable(quarantine_table)

        quarantine_rate = df_quarantine.count() / df.count()
        print(f"Quarantined {df_quarantine.count()} records ({quarantine_rate:.2%})")

        # Alert if threshold exceeded
        if quarantine_rate > 0.05:  # 5% threshold
            send_alert(f"High quarantine rate: {quarantine_rate:.2%}")

    return df_good.count(), df_quarantine.count()

# Usage
validation_rules = {
    "null_customer_id": col("customer_id").isNotNull(),
    "valid_amount": col("amount") > 0,
    "valid_email": col("email").rlike(r"^[\w.+-]+@[\w.-]+\.\w+$")
}

good_count, quarantine_count = process_with_quarantine(
    df,
    validation_rules,
    "silver_orders",
    "quarantine_orders"
)
```

## Dead Letter Queue Pattern

### For Streaming Workloads

```python
from pyspark.sql.functions import struct, to_json, current_timestamp

def write_to_dead_letter(
    failed_records,
    error_message: str,
    source_topic: str,
    dlq_table: str
):
    """Write failed records to dead letter queue."""

    dlq_records = failed_records.select(
        to_json(struct("*")).alias("original_payload"),
        lit(error_message).alias("error_message"),
        lit(source_topic).alias("source"),
        current_timestamp().alias("failed_at"),
        lit(0).alias("retry_count")
    )

    dlq_records.write.format("delta").mode("append").saveAsTable(dlq_table)

def process_stream_with_dlq(source_stream, process_func, dlq_table: str):
    """Process stream with dead letter queue for failures."""

    def process_batch(batch_df, batch_id):
        try:
            # Try to process
            result = process_func(batch_df)
            result.write.format("delta").mode("append").saveAsTable("target_table")
        except Exception as e:
            # Send to DLQ
            write_to_dead_letter(batch_df, str(e), "source_topic", dlq_table)
            logging.error(f"Batch {batch_id} sent to DLQ: {e}")

    source_stream.writeStream \
        .foreachBatch(process_batch) \
        .option("checkpointLocation", "/checkpoints/stream") \
        .start()
```

### Replay DLQ Records

```python
def replay_dead_letter_queue(dlq_table: str, max_retries: int = 3):
    """Replay failed records from DLQ."""

    dlq_records = spark.table(dlq_table).filter(f"retry_count < {max_retries}")

    for row in dlq_records.collect():
        try:
            # Attempt to reprocess
            payload = json.loads(row.original_payload)
            process_record(payload)

            # Remove from DLQ on success
            spark.sql(f"""
                DELETE FROM {dlq_table}
                WHERE original_payload = '{row.original_payload}'
            """)

        except Exception as e:
            # Increment retry count
            spark.sql(f"""
                UPDATE {dlq_table}
                SET retry_count = retry_count + 1,
                    last_retry_at = current_timestamp(),
                    last_error = '{str(e)}'
                WHERE original_payload = '{row.original_payload}'
            """)
```

## Alerting Pattern

### Alert Configuration

```python
from enum import Enum
from dataclasses import dataclass
from typing import Callable

class AlertSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class AlertRule:
    name: str
    condition: Callable[..., bool]
    severity: AlertSeverity
    message_template: str

# Define alert rules
ALERT_RULES = [
    AlertRule(
        name="high_failure_rate",
        condition=lambda stats: stats.failure_rate > 0.05,
        severity=AlertSeverity.ERROR,
        message_template="Pipeline {pipeline} has {failure_rate:.2%} failure rate"
    ),
    AlertRule(
        name="no_records_processed",
        condition=lambda stats: stats.records_processed == 0,
        severity=AlertSeverity.WARNING,
        message_template="Pipeline {pipeline} processed 0 records"
    ),
    AlertRule(
        name="long_running",
        condition=lambda stats: stats.duration_minutes > 60,
        severity=AlertSeverity.WARNING,
        message_template="Pipeline {pipeline} running for {duration_minutes} minutes"
    )
]
```

### Send Alerts

```python
import requests
import logging

def send_alert(
    message: str,
    severity: AlertSeverity,
    channel: str = "default"
):
    """Send alert to configured channels."""

    logging.log(
        logging.ERROR if severity in [AlertSeverity.ERROR, AlertSeverity.CRITICAL]
        else logging.WARNING,
        message
    )

    # Slack webhook
    if channel in ["default", "slack"]:
        slack_webhook = get_secret("slack-webhook-url")
        emoji = {
            AlertSeverity.INFO: ":information_source:",
            AlertSeverity.WARNING: ":warning:",
            AlertSeverity.ERROR: ":x:",
            AlertSeverity.CRITICAL: ":rotating_light:"
        }
        requests.post(slack_webhook, json={
            "text": f"{emoji[severity]} *{severity.value.upper()}*: {message}"
        })

    # PagerDuty for critical
    if severity == AlertSeverity.CRITICAL:
        pagerduty_key = get_secret("pagerduty-routing-key")
        requests.post(
            "https://events.pagerduty.com/v2/enqueue",
            json={
                "routing_key": pagerduty_key,
                "event_action": "trigger",
                "payload": {
                    "summary": message,
                    "severity": "critical",
                    "source": "data-pipeline"
                }
            }
        )
```

## Pipeline Wrapper

### Complete Error Handling Wrapper

```python
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
import traceback

@dataclass
class PipelineStats:
    pipeline_name: str
    start_time: datetime
    end_time: datetime = None
    records_processed: int = 0
    records_failed: int = 0
    status: str = "running"
    error_message: str = None

    @property
    def duration_minutes(self) -> float:
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds() / 60

    @property
    def failure_rate(self) -> float:
        total = self.records_processed + self.records_failed
        return self.records_failed / total if total > 0 else 0

@contextmanager
def pipeline_error_handler(pipeline_name: str, alert_on_failure: bool = True):
    """Context manager for pipeline error handling."""

    stats = PipelineStats(
        pipeline_name=pipeline_name,
        start_time=datetime.now()
    )

    try:
        yield stats
        stats.status = "success"

    except Exception as e:
        stats.status = "failed"
        stats.error_message = str(e)
        stats.end_time = datetime.now()

        logging.error(f"Pipeline {pipeline_name} failed: {e}")
        logging.error(traceback.format_exc())

        if alert_on_failure:
            send_alert(
                f"Pipeline {pipeline_name} failed: {e}",
                AlertSeverity.ERROR
            )

        raise

    finally:
        stats.end_time = datetime.now()
        log_pipeline_stats(stats)

        # Check alert rules
        for rule in ALERT_RULES:
            if rule.condition(stats):
                send_alert(
                    rule.message_template.format(**stats.__dict__),
                    rule.severity
                )

# Usage
with pipeline_error_handler("ingest_orders") as stats:
    df = extract_from_api()
    stats.records_processed = df.count()

    good, bad = process_with_quarantine(df, rules, "orders", "quarantine")
    stats.records_failed = bad
```

## Platform Variations

### Azure Data Factory

```json
{
    "name": "Pipeline with Error Handling",
    "properties": {
        "activities": [
            {
                "name": "ProcessData",
                "type": "ExecuteDataFlow",
                "dependsOn": [],
                "policy": {
                    "retry": 3,
                    "retryIntervalInSeconds": 30,
                    "secureOutput": false,
                    "timeout": "01:00:00"
                }
            },
            {
                "name": "SendAlertOnFailure",
                "type": "WebActivity",
                "dependsOn": [
                    {
                        "activity": "ProcessData",
                        "dependencyConditions": ["Failed"]
                    }
                ],
                "typeProperties": {
                    "url": "@pipeline().parameters.alertWebhookUrl",
                    "method": "POST",
                    "body": {
                        "pipeline": "@pipeline().Pipeline",
                        "error": "@activity('ProcessData').Error.message"
                    }
                }
            }
        ]
    }
}
```

### Databricks Workflows

```python
# Databricks job error handling
from databricks.sdk import WorkspaceClient

w = WorkspaceClient()

job = w.jobs.create(
    name="pipeline_with_retry",
    tasks=[
        {
            "task_key": "ingest",
            "notebook_task": {"notebook_path": "/pipelines/ingest"},
            "retry_on_timeout": True,
            "max_retries": 3,
            "min_retry_interval_millis": 30000
        }
    ],
    email_notifications={
        "on_failure": ["data-alerts@company.com"]
    }
)
```

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| **Catch-all exceptions** | Hides real errors | Catch specific exceptions |
| **Infinite retries** | Never fails, never alerts | Set max retries |
| **No alerting** | Silent failures | Alert on thresholds |
| **Alert fatigue** | Too many alerts ignored | Tune thresholds, batch alerts |
| **Losing error context** | Hard to debug | Log full stack traces |

## References

- [Azure Data Factory Error Handling](https://learn.microsoft.com/azure/data-factory/concepts-pipeline-execution-triggers)
- [Databricks Job Retry](https://docs.databricks.com/en/workflows/jobs/settings.html#add-retry-policy)
- [Spark Structured Streaming Fault Tolerance](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html#fault-tolerance-semantics)

---

*Last Updated: 2026-02-09*
