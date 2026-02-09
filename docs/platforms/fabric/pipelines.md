# Fabric Pipeline Patterns

Data Factory pipeline patterns for Microsoft Fabric.

## Pipeline Structure

### Naming Convention

| Type | Pattern | Example |
|------|---------|---------|
| Ingestion | `pl_ingest_{source}_{entity}_{freq}` | `pl_ingest_hubspot_companies_daily` |
| Transform | `pl_transform_{domain}_{freq}` | `pl_transform_sales_daily` |
| Orchestration | `pl_orchestrate_{domain}_{freq}` | `pl_orchestrate_sales_daily` |
| Utility | `pl_util_{purpose}` | `pl_util_data_quality` |

## Common Patterns

### Basic Ingestion Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    INGESTION PIPELINE                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌────────┐    ┌────────────┐    ┌───────────┐    ┌──────────┐ │
│  │Schedule│───►│Copy from   │───►│Run Bronze │───►│Log Status│ │
│  │Trigger │    │API to Files│    │Notebook   │    │          │ │
│  └────────┘    └────────────┘    └───────────┘    └──────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Pipeline JSON Structure

```json
{
    "name": "pl_ingest_hubspot_companies_daily",
    "properties": {
        "activities": [
            {
                "name": "Copy API to Files",
                "type": "Copy",
                "inputs": [
                    {"referenceName": "ds_hubspot_api", "type": "DatasetReference"}
                ],
                "outputs": [
                    {"referenceName": "ds_lakehouse_files", "type": "DatasetReference"}
                ],
                "typeProperties": {
                    "source": {
                        "type": "RestSource",
                        "httpRequestTimeout": "00:05:00"
                    },
                    "sink": {
                        "type": "JsonSink",
                        "storeSettings": {
                            "type": "LakehouseWriteSettings"
                        }
                    }
                }
            },
            {
                "name": "Run Bronze Notebook",
                "type": "TridentNotebook",
                "dependsOn": [
                    {"activity": "Copy API to Files", "dependencyConditions": ["Succeeded"]}
                ],
                "typeProperties": {
                    "notebookId": "notebook-guid",
                    "parameters": {
                        "source_path": {"value": "@pipeline().parameters.sourcePath", "type": "string"},
                        "target_table": {"value": "bronze_hubspot_companies", "type": "string"}
                    }
                }
            }
        ],
        "parameters": {
            "sourcePath": {"type": "string", "defaultValue": "landing/hubspot/companies"}
        }
    }
}
```

## Orchestration Pattern

### Master Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    MASTER ORCHESTRATION                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  pl_orchestrate_sales_daily                                     │
│  ├── Execute: pl_ingest_hubspot_companies_daily                 │
│  ├── Execute: pl_ingest_hubspot_deals_daily (parallel)          │
│  ├── Execute: pl_ingest_hubspot_contacts_daily (parallel)       │
│  │                                                              │
│  ├── (Wait for all ingestion)                                   │
│  │                                                              │
│  ├── Notebook: nb_silver_transform_companies                    │
│  ├── Notebook: nb_silver_transform_deals (parallel)             │
│  ├── Notebook: nb_silver_transform_contacts (parallel)          │
│  │                                                              │
│  ├── (Wait for all silver)                                      │
│  │                                                              │
│  ├── Notebook: nb_gold_dim_customer                             │
│  └── Notebook: nb_gold_fact_sales                               │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### ForEach for Multiple Entities

```json
{
    "name": "ForEach Entity",
    "type": "ForEach",
    "typeProperties": {
        "items": {
            "value": "@pipeline().parameters.entities",
            "type": "Expression"
        },
        "isSequential": false,
        "batchCount": 5,
        "activities": [
            {
                "name": "Ingest Entity",
                "type": "ExecutePipeline",
                "typeProperties": {
                    "pipeline": {
                        "referenceName": "pl_ingest_generic",
                        "type": "PipelineReference"
                    },
                    "parameters": {
                        "entity": "@item().name",
                        "endpoint": "@item().endpoint"
                    }
                }
            }
        ]
    }
}
```

## Error Handling

### Retry Configuration

```json
{
    "name": "Activity with Retry",
    "type": "Copy",
    "policy": {
        "retry": 3,
        "retryIntervalInSeconds": 30,
        "secureOutput": false,
        "timeout": "01:00:00"
    }
}
```

### Failure Notification

```json
{
    "name": "Send Failure Alert",
    "type": "WebActivity",
    "dependsOn": [
        {"activity": "Main Activity", "dependencyConditions": ["Failed"]}
    ],
    "typeProperties": {
        "url": "@pipeline().parameters.alertWebhookUrl",
        "method": "POST",
        "headers": {"Content-Type": "application/json"},
        "body": {
            "pipeline": "@pipeline().Pipeline",
            "runId": "@pipeline().RunId",
            "status": "Failed",
            "error": "@activity('Main Activity').Error.message",
            "timestamp": "@utcNow()"
        }
    }
}
```

### Success/Failure Branching

```
                    ┌─────────────────┐
                    │  Main Activity  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
        [Succeeded]    [Failed]      [Completed]
              │              │              │
              ▼              ▼              ▼
        ┌─────────┐    ┌─────────┐    ┌─────────┐
        │ Log     │    │ Send    │    │ Cleanup │
        │ Success │    │ Alert   │    │         │
        └─────────┘    └─────────┘    └─────────┘
```

## Parameters and Variables

### Pipeline Parameters

```json
{
    "parameters": {
        "environment": {
            "type": "string",
            "defaultValue": "dev"
        },
        "runDate": {
            "type": "string",
            "defaultValue": "@formatDateTime(utcNow(), 'yyyy-MM-dd')"
        },
        "fullRefresh": {
            "type": "bool",
            "defaultValue": false
        }
    }
}
```

### Dynamic Expressions

```json
{
    "typeProperties": {
        "notebookId": "notebook-guid",
        "parameters": {
            "target_table": {
                "value": "@concat('bronze_hubspot_companies_', pipeline().parameters.environment)",
                "type": "string"
            },
            "run_date": {
                "value": "@pipeline().parameters.runDate",
                "type": "string"
            }
        }
    }
}
```

## Scheduling

### Trigger Configuration

```json
{
    "name": "tr_daily_0200_utc",
    "type": "ScheduleTrigger",
    "typeProperties": {
        "recurrence": {
            "frequency": "Day",
            "interval": 1,
            "startTime": "2026-01-01T02:00:00Z",
            "timeZone": "UTC"
        }
    },
    "pipelines": [
        {
            "pipelineReference": {
                "referenceName": "pl_orchestrate_sales_daily",
                "type": "PipelineReference"
            },
            "parameters": {
                "environment": "prod"
            }
        }
    ]
}
```

### Dependency Triggers

```json
{
    "name": "tr_after_upstream",
    "type": "TumblingWindowTrigger",
    "typeProperties": {
        "frequency": "Day",
        "interval": 1,
        "startTime": "2026-01-01T03:00:00Z",
        "delay": "00:00:00",
        "maxConcurrency": 1,
        "retryPolicy": {
            "count": 2,
            "intervalInSeconds": 30
        },
        "dependsOn": [
            {
                "type": "TumblingWindowTriggerDependencyReference",
                "referenceTrigger": {
                    "referenceName": "tr_upstream_pipeline",
                    "type": "TriggerReference"
                }
            }
        ]
    }
}
```

## Best Practices

| Practice | Rationale |
|----------|-----------|
| **Use parameters** | Reusable pipelines across environments |
| **Set timeouts** | Prevent runaway pipelines |
| **Add retries** | Handle transient failures |
| **Log activity status** | Debugging and monitoring |
| **Fail fast** | Don't continue after critical failures |
| **Parallel when possible** | Reduce total runtime |

## Monitoring

### Key Metrics

| Metric | Where to Find |
|--------|---------------|
| Pipeline duration | Monitor Hub → Pipeline runs |
| Activity success rate | Monitor Hub → Activity runs |
| Data processed | Copy activity output |
| Error details | Activity run details |

### Custom Logging

```json
{
    "name": "Log Pipeline Start",
    "type": "SetVariable",
    "typeProperties": {
        "variableName": "startTime",
        "value": "@utcNow()"
    }
},
{
    "name": "Log to Table",
    "type": "TridentNotebook",
    "typeProperties": {
        "notebookId": "logging-notebook-guid",
        "parameters": {
            "pipeline_name": {"value": "@pipeline().Pipeline", "type": "string"},
            "run_id": {"value": "@pipeline().RunId", "type": "string"},
            "status": {"value": "completed", "type": "string"},
            "duration_seconds": {
                "value": "@div(sub(ticks(utcNow()), ticks(variables('startTime'))), 10000000)",
                "type": "int"
            }
        }
    }
}
```

## References

- [Fabric Data Factory](https://learn.microsoft.com/fabric/data-factory/)
- [Pipeline Activities](https://learn.microsoft.com/fabric/data-factory/activity-overview)
- [Expressions and Functions](https://learn.microsoft.com/azure/data-factory/control-flow-expression-language-functions)

---

*Last Updated: 2026-02-09*
