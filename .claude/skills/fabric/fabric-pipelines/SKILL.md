---
name: fabric-pipelines
description: Building Fabric Data Factory pipelines.
---

# Fabric Pipelines Skill

## Pipeline Structure

```json
{
  "name": "pl_name",
  "properties": {
    "activities": [...],
    "parameters": {...}
  }
}
```

## Activity Types

### Copy Activity
```json
{
  "name": "CopyData",
  "type": "Copy",
  "typeProperties": {
    "source": {"type": "SalesforceSource"},
    "sink": {"type": "DeltaSink"}
  },
  "policy": {
    "timeout": "01:00:00",
    "retry": 3,
    "retryIntervalInSeconds": 30
  }
}
```

### Notebook Activity
```json
{
  "name": "Transform",
  "type": "Notebook",
  "typeProperties": {
    "notebookPath": "/notebooks/transform",
    "parameters": {
      "run_date": "@pipeline().parameters.run_date"
    }
  }
}
```

### ForEach Loop
```json
{
  "name": "ForEachTable",
  "type": "ForEach",
  "typeProperties": {
    "items": "@pipeline().parameters.tableList",
    "isSequential": false,
    "activities": [...]
  }
}
```

### If Condition
```json
{
  "name": "CheckCondition",
  "type": "IfCondition",
  "typeProperties": {
    "expression": {
      "value": "@equals(pipeline().parameters.loadType, 'full')",
      "type": "Expression"
    },
    "ifTrueActivities": [...],
    "ifFalseActivities": [...]
  }
}
```

### Lookup Activity
```json
{
  "name": "GetWatermark",
  "type": "Lookup",
  "typeProperties": {
    "source": {
      "type": "AzureSqlSource",
      "sqlReaderQuery": "SELECT MAX(modified_date) as watermark FROM watermark_table"
    }
  }
}
```

### Set Variable
```json
{
  "name": "SetWatermark",
  "type": "SetVariable",
  "typeProperties": {
    "variableName": "watermark",
    "value": "@activity('GetWatermark').output.firstRow.watermark"
  }
}
```

## Parameters

```json
{
  "parameters": {
    "watermark": {
      "type": "String",
      "defaultValue": "2024-01-01"
    },
    "loadType": {
      "type": "String",
      "defaultValue": "incremental"
    },
    "tableList": {
      "type": "Array",
      "defaultValue": ["table1", "table2"]
    }
  }
}
```

## Variables

```json
{
  "variables": {
    "currentWatermark": {
      "type": "String"
    },
    "processedCount": {
      "type": "Integer"
    }
  }
}
```

## Error Handling

### Retry Policy
```json
{
  "policy": {
    "timeout": "01:00:00",
    "retry": 3,
    "retryIntervalInSeconds": 30,
    "secureOutput": false,
    "secureInput": false
  }
}
```

### On Failure Activities
```json
{
  "name": "MainActivity",
  "type": "Copy",
  "dependsOn": [],
  "typeProperties": {...}
},
{
  "name": "OnFailure_SendAlert",
  "type": "WebActivity",
  "dependsOn": [
    {
      "activity": "MainActivity",
      "dependencyConditions": ["Failed"]
    }
  ],
  "typeProperties": {
    "url": "https://alerts.company.com/webhook",
    "method": "POST",
    "body": {
      "pipeline": "@pipeline().Pipeline",
      "error": "@activity('MainActivity').error.message"
    }
  }
}
```

## Scheduling

### Schedule Trigger
```json
{
  "name": "DailyTrigger",
  "properties": {
    "type": "ScheduleTrigger",
    "typeProperties": {
      "recurrence": {
        "frequency": "Day",
        "interval": 1,
        "startTime": "2024-01-01T02:00:00Z",
        "timeZone": "UTC"
      }
    },
    "pipelines": [
      {
        "pipelineReference": {
          "referenceName": "pl_ingest_daily",
          "type": "PipelineReference"
        },
        "parameters": {}
      }
    ]
  }
}
```

### Tumbling Window Trigger
```json
{
  "name": "HourlyTrigger",
  "properties": {
    "type": "TumblingWindowTrigger",
    "typeProperties": {
      "frequency": "Hour",
      "interval": 1,
      "startTime": "2024-01-01T00:00:00Z",
      "delay": "00:05:00",
      "maxConcurrency": 1,
      "retryPolicy": {
        "count": 3,
        "intervalInSeconds": 30
      }
    }
  }
}
```

## Common Patterns

### Incremental Load Pipeline
```json
{
  "name": "pl_incremental_load",
  "properties": {
    "activities": [
      {
        "name": "GetLastWatermark",
        "type": "Lookup",
        "typeProperties": {
          "source": {
            "type": "AzureSqlSource",
            "sqlReaderQuery": "SELECT watermark FROM control.watermarks WHERE table_name = '@{pipeline().parameters.tableName}'"
          }
        }
      },
      {
        "name": "CopyIncremental",
        "type": "Copy",
        "dependsOn": [{"activity": "GetLastWatermark", "dependencyConditions": ["Succeeded"]}],
        "typeProperties": {
          "source": {
            "type": "SalesforceSource",
            "query": "SELECT * FROM @{pipeline().parameters.tableName} WHERE LastModifiedDate > '@{activity('GetLastWatermark').output.firstRow.watermark}'"
          },
          "sink": {
            "type": "DeltaSink"
          }
        }
      },
      {
        "name": "UpdateWatermark",
        "type": "SqlServerStoredProcedure",
        "dependsOn": [{"activity": "CopyIncremental", "dependencyConditions": ["Succeeded"]}],
        "typeProperties": {
          "storedProcedureName": "control.usp_UpdateWatermark",
          "storedProcedureParameters": {
            "tableName": "@{pipeline().parameters.tableName}",
            "watermark": "@{utcNow()}"
          }
        }
      }
    ],
    "parameters": {
      "tableName": {"type": "String"}
    }
  }
}
```

### Multi-Table Pipeline
```json
{
  "name": "pl_ingest_multiple_tables",
  "properties": {
    "activities": [
      {
        "name": "GetTableList",
        "type": "Lookup",
        "typeProperties": {
          "source": {
            "type": "AzureSqlSource",
            "sqlReaderQuery": "SELECT table_name, watermark_column FROM control.tables WHERE is_active = 1"
          },
          "firstRowOnly": false
        }
      },
      {
        "name": "ForEachTable",
        "type": "ForEach",
        "dependsOn": [{"activity": "GetTableList", "dependencyConditions": ["Succeeded"]}],
        "typeProperties": {
          "items": "@activity('GetTableList').output.value",
          "isSequential": false,
          "batchCount": 5,
          "activities": [
            {
              "name": "CopyTable",
              "type": "Copy",
              "typeProperties": {
                "source": {
                  "type": "SalesforceSource",
                  "query": "SELECT * FROM @{item().table_name}"
                },
                "sink": {
                  "type": "DeltaSink",
                  "tableName": "bronze_@{item().table_name}"
                }
              }
            }
          ]
        }
      }
    ]
  }
}
```

### Bronze-Silver-Gold Pipeline
```json
{
  "name": "pl_etl_salesforce_account",
  "properties": {
    "activities": [
      {
        "name": "IngestToBronze",
        "type": "Copy",
        "typeProperties": {
          "source": {"type": "SalesforceSource"},
          "sink": {"type": "DeltaSink", "tableName": "bronze_salesforce_account"}
        }
      },
      {
        "name": "TransformToSilver",
        "type": "Notebook",
        "dependsOn": [{"activity": "IngestToBronze", "dependencyConditions": ["Succeeded"]}],
        "typeProperties": {
          "notebookPath": "/notebooks/transform_account_bronze_to_silver"
        }
      },
      {
        "name": "BuildGold",
        "type": "Notebook",
        "dependsOn": [{"activity": "TransformToSilver", "dependencyConditions": ["Succeeded"]}],
        "typeProperties": {
          "notebookPath": "/notebooks/build_dim_customer"
        }
      }
    ]
  }
}
```

## Expressions Reference

### System Variables
- `@pipeline().Pipeline` - Pipeline name
- `@pipeline().RunId` - Run ID
- `@pipeline().TriggerTime` - Trigger time
- `@pipeline().parameters.paramName` - Parameter value

### Functions
- `@utcNow()` - Current UTC time
- `@addDays(utcNow(), -1)` - Yesterday
- `@formatDateTime(utcNow(), 'yyyy-MM-dd')` - Format date
- `@concat('prefix_', pipeline().parameters.name)` - Concatenate
- `@json(activity('Lookup').output.firstRow)` - Parse JSON

### Activity Outputs
- `@activity('ActivityName').output` - Full output
- `@activity('ActivityName').output.firstRow.columnName` - Specific value
- `@activity('ActivityName').output.value` - Array output
- `@activity('ActivityName').error.message` - Error message

## Best Practices

- Use parameters for configurability
- Add error handling and retries
- Log outputs for debugging
- Use appropriate timeouts
- Enable retry policies
- Use parallel ForEach when possible

## Anti-Patterns

- Don't hardcode values
- Don't skip error handling
- Don't use sequential ForEach for large lists
- Don't forget to update watermarks
