---
name: databricks-workflows
description: Building Databricks Workflows for orchestration.
---

# Databricks Workflows Skill

## Workflow Structure

```json
{
  "name": "wf_ingest_salesforce_daily",
  "tasks": [
    {
      "task_key": "task_name",
      "notebook_task": {...},
      "depends_on": [...],
      "cluster": {...}
    }
  ],
  "schedule": {...},
  "notification_settings": {...}
}
```

## Task Types

### Notebook Task
```json
{
  "task_key": "transform_bronze_to_silver",
  "notebook_task": {
    "notebook_path": "/Repos/project/notebooks/transform_silver",
    "source": "WORKSPACE",
    "base_parameters": {
      "run_date": "{{job.start_time.iso_date}}",
      "table_name": "account"
    }
  }
}
```

### SQL Task
```json
{
  "task_key": "run_quality_checks",
  "sql_task": {
    "warehouse_id": "abc123",
    "query": {
      "query_id": "query-uuid"
    }
  }
}
```

### Python Script Task
```json
{
  "task_key": "run_python_script",
  "python_wheel_task": {
    "package_name": "my_package",
    "entry_point": "main",
    "parameters": ["--date", "{{job.start_time.iso_date}}"]
  }
}
```

### DLT Pipeline Task
```json
{
  "task_key": "run_dlt_pipeline",
  "pipeline_task": {
    "pipeline_id": "pipeline-uuid",
    "full_refresh": false
  }
}
```

### Spark Submit Task
```json
{
  "task_key": "run_jar",
  "spark_submit_task": {
    "parameters": [
      "--class", "com.company.Main",
      "dbfs:/jars/app.jar",
      "--date", "{{job.start_time.iso_date}}"
    ]
  }
}
```

## Task Dependencies

### Linear Dependencies
```json
{
  "tasks": [
    {"task_key": "ingest", "depends_on": []},
    {"task_key": "transform", "depends_on": [{"task_key": "ingest"}]},
    {"task_key": "load", "depends_on": [{"task_key": "transform"}]}
  ]
}
```

### Parallel Dependencies
```json
{
  "tasks": [
    {"task_key": "ingest_accounts", "depends_on": []},
    {"task_key": "ingest_contacts", "depends_on": []},
    {"task_key": "transform", "depends_on": [
      {"task_key": "ingest_accounts"},
      {"task_key": "ingest_contacts"}
    ]}
  ]
}
```

### Conditional Dependencies
```json
{
  "task_key": "notify_failure",
  "depends_on": [
    {
      "task_key": "transform",
      "outcome": "failed"
    }
  ]
}
```

## Compute Configuration

### Job Cluster (Dedicated)
```json
{
  "task_key": "heavy_transform",
  "new_cluster": {
    "spark_version": "14.3.x-scala2.12",
    "node_type_id": "i3.xlarge",
    "num_workers": 4,
    "spark_conf": {
      "spark.databricks.delta.autoCompact.enabled": "true"
    },
    "aws_attributes": {
      "instance_profile_arn": "arn:aws:iam::..."
    }
  }
}
```

### Serverless (Recommended)
```json
{
  "task_key": "light_transform",
  "existing_cluster_id": "",
  "job_cluster_key": "",
  "compute_key": "serverless"
}
```

### Shared Cluster
```json
{
  "job_clusters": [
    {
      "job_cluster_key": "shared_cluster",
      "new_cluster": {
        "spark_version": "14.3.x-scala2.12",
        "num_workers": 4
      }
    }
  ],
  "tasks": [
    {
      "task_key": "task1",
      "job_cluster_key": "shared_cluster"
    },
    {
      "task_key": "task2",
      "job_cluster_key": "shared_cluster"
    }
  ]
}
```

## Scheduling

### Cron Schedule
```json
{
  "schedule": {
    "quartz_cron_expression": "0 0 2 * * ?",
    "timezone_id": "UTC",
    "pause_status": "UNPAUSED"
  }
}
```

### Common Cron Expressions
```
0 0 2 * * ?     - Daily at 2 AM
0 0 */6 * * ?   - Every 6 hours
0 30 8 ? * MON-FRI - Weekdays at 8:30 AM
0 0 0 1 * ?     - First day of month
```

### Continuous Trigger
```json
{
  "trigger": {
    "file_arrival": {
      "url": "s3://bucket/landing/",
      "min_time_between_triggers_seconds": 60
    }
  }
}
```

## Parameters

### Job Parameters
```json
{
  "parameters": [
    {
      "name": "run_date",
      "default": "{{job.start_time.iso_date}}"
    },
    {
      "name": "load_type",
      "default": "incremental"
    }
  ]
}
```

### Task Parameters
```json
{
  "task_key": "transform",
  "notebook_task": {
    "base_parameters": {
      "run_date": "{{job.parameters.run_date}}",
      "upstream_output": "{{tasks.ingest.values.output_path}}"
    }
  }
}
```

### Dynamic Values
```
{{job.start_time.iso_date}}        - Job start date
{{job.start_time.epoch_ms}}        - Epoch milliseconds
{{job.parameters.param_name}}      - Job parameter
{{tasks.task_key.values.var}}      - Task output value
{{job.id}}                         - Job ID
{{job.run_id}}                     - Run ID
```

## Error Handling

### Retry Policy
```json
{
  "task_key": "transform",
  "retry_on_timeout": true,
  "max_retries": 3,
  "min_retry_interval_millis": 60000
}
```

### Timeout
```json
{
  "task_key": "transform",
  "timeout_seconds": 3600
}
```

### Notifications
```json
{
  "notification_settings": {
    "alerts": [
      {
        "email_notifications": {
          "on_failure": ["team@company.com"],
          "on_success": []
        }
      }
    ],
    "webhook_notifications": {
      "on_failure": [
        {"id": "webhook-uuid"}
      ]
    }
  }
}
```

## Common Patterns

### ETL Pipeline
```json
{
  "name": "wf_etl_salesforce",
  "tasks": [
    {
      "task_key": "ingest_to_bronze",
      "notebook_task": {
        "notebook_path": "/notebooks/ingest_salesforce"
      }
    },
    {
      "task_key": "transform_to_silver",
      "notebook_task": {
        "notebook_path": "/notebooks/transform_silver"
      },
      "depends_on": [{"task_key": "ingest_to_bronze"}]
    },
    {
      "task_key": "build_gold_models",
      "notebook_task": {
        "notebook_path": "/notebooks/build_gold"
      },
      "depends_on": [{"task_key": "transform_to_silver"}]
    },
    {
      "task_key": "run_quality_checks",
      "notebook_task": {
        "notebook_path": "/notebooks/quality_checks"
      },
      "depends_on": [{"task_key": "build_gold_models"}]
    }
  ]
}
```

### Multi-Table Parallel Processing
```json
{
  "name": "wf_ingest_multiple_tables",
  "tasks": [
    {
      "task_key": "ingest_accounts",
      "notebook_task": {
        "base_parameters": {"table": "accounts"}
      }
    },
    {
      "task_key": "ingest_contacts",
      "notebook_task": {
        "base_parameters": {"table": "contacts"}
      }
    },
    {
      "task_key": "ingest_opportunities",
      "notebook_task": {
        "base_parameters": {"table": "opportunities"}
      }
    },
    {
      "task_key": "transform_all",
      "depends_on": [
        {"task_key": "ingest_accounts"},
        {"task_key": "ingest_contacts"},
        {"task_key": "ingest_opportunities"}
      ]
    }
  ]
}
```

### For Each Task
```json
{
  "task_key": "process_tables",
  "for_each_task": {
    "inputs": "[\"accounts\", \"contacts\", \"opportunities\"]",
    "task": {
      "task_key": "process_single_table",
      "notebook_task": {
        "notebook_path": "/notebooks/process_table",
        "base_parameters": {
          "table_name": "{{input}}"
        }
      }
    }
  }
}
```

## Workflow SDK

### Create Workflow
```python
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import *

w = WorkspaceClient()

job = w.jobs.create(
    name="wf_ingest_salesforce",
    tasks=[
        Task(
            task_key="ingest",
            notebook_task=NotebookTask(
                notebook_path="/notebooks/ingest"
            )
        )
    ],
    schedule=CronSchedule(
        quartz_cron_expression="0 0 2 * * ?",
        timezone_id="UTC"
    )
)
```

### Run Workflow
```python
run = w.jobs.run_now(job_id=job.job_id)
```

### Wait for Completion
```python
from databricks.sdk.service.jobs import RunLifeCycleState

run_result = w.jobs.wait_get_run_job_terminated_or_skipped(
    run_id=run.run_id
)

if run_result.state.result_state == RunResultState.SUCCESS:
    print("Job succeeded")
else:
    print(f"Job failed: {run_result.state.state_message}")
```

## Best Practices

- Use Serverless compute when possible
- Share clusters for related tasks
- Set appropriate timeouts
- Configure retries for transient failures
- Use notifications for monitoring
- Parameterize for flexibility
- Use task dependencies effectively

## Anti-Patterns

- Don't create single-task workflows
- Don't hardcode values
- Don't skip error handling
- Don't use overly complex dependencies
- Don't forget to set timeouts
