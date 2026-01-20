---
name: fabric-deployment
description: Deploying artifacts to Microsoft Fabric workspaces.
tools: az, azcopy, jq
---

# Fabric Deployment Skill

## Available CLI Tools

| Tool | Purpose |
|------|---------|
| `az` | Azure CLI for Fabric REST API calls and authentication |
| `azcopy` | High-performance data transfer to OneLake |
| `jq` | JSON processing for API responses |

## Deployment Overview

Fabric supports multiple deployment approaches:
- Git integration (recommended)
- Deployment pipelines
- Azure CLI with REST API (`az rest`)
- azcopy for data transfer

## Git Integration

### Setup
1. Connect workspace to Git repository
2. Configure branch policies
3. Set up sync settings

### Repository Structure
```
repo/
+-- .fabric/
|   +-- workspace.json
+-- lakehouses/
|   +-- lh_sales/
|       +-- lakehouse.json
+-- pipelines/
|   +-- pl_ingest_salesforce/
|       +-- pipeline.json
+-- notebooks/
|   +-- nb_transform_bronze_silver/
|       +-- notebook.py
+-- dataflows/
|   +-- df_transform_data/
|       +-- dataflow.json
```

### Workflow
```bash
# 1. Create feature branch
git checkout -b feature/new-pipeline

# 2. Make changes in Fabric workspace (connected to branch)
# Or edit files locally

# 3. Commit changes
git add .
git commit -m "feat: add new pipeline"

# 4. Create PR
git push origin feature/new-pipeline
# Create PR in GitHub/Azure DevOps

# 5. Merge to main (triggers sync to workspace)
```

## Deployment Pipelines

### Pipeline Stages
```
Development -> Test -> Production
     |           |          |
  Sales_Dev  Sales_Test  Sales_Prod
```

### Configure Deployment Rules
```json
{
  "deploymentRules": [
    {
      "sourceItem": "pl_ingest_salesforce",
      "targetItem": "pl_ingest_salesforce",
      "parameterRules": [
        {
          "name": "environment",
          "value": "${stage}"
        }
      ]
    }
  ]
}
```

### Trigger Deployment
```python
# Using Fabric REST API
import requests

def deploy_to_stage(pipeline_id, source_stage, target_stage, token):
    """Deploy artifacts between stages."""
    url = f"https://api.fabric.microsoft.com/v1/deploymentPipelines/{pipeline_id}/deploy"

    payload = {
        "sourceStageId": source_stage,
        "targetStageId": target_stage,
        "options": {
            "allowCreateItem": True,
            "allowDeleteItem": False,
            "allowUpdateItem": True
        }
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()
```

## Azure CLI Deployment (az rest)

### Authentication
```bash
# Login to Azure (interactive)
az login

# Or with service principal
az login --service-principal \
  -u $AZURE_CLIENT_ID \
  -p $AZURE_CLIENT_SECRET \
  --tenant $AZURE_TENANT_ID

# Verify login
az account show | jq '{name: .name, id: .id}'
```

### List Workspaces
```bash
# Get all Fabric workspaces
az rest --method GET \
  --url "https://api.fabric.microsoft.com/v1/workspaces" \
  --headers "Content-Type=application/json" \
  | jq '.value[] | {id: .id, name: .displayName, type: .type}'

# Get specific workspace by name
WORKSPACE_NAME="Sales_Dev"
az rest --method GET \
  --url "https://api.fabric.microsoft.com/v1/workspaces" \
  | jq --arg name "$WORKSPACE_NAME" '.value[] | select(.displayName == $name)'
```

### Deploy Items
```bash
# Get workspace ID
WORKSPACE_ID=$(az rest --method GET \
  --url "https://api.fabric.microsoft.com/v1/workspaces" \
  | jq -r --arg name "$WORKSPACE_NAME" '.value[] | select(.displayName == $name) | .id')

# List items in workspace
az rest --method GET \
  --url "https://api.fabric.microsoft.com/v1/workspaces/$WORKSPACE_ID/items" \
  | jq '.value[] | {name: .displayName, type: .type, id: .id}'

# Create new item (pipeline, notebook, etc.)
az rest --method POST \
  --url "https://api.fabric.microsoft.com/v1/workspaces/$WORKSPACE_ID/items" \
  --headers "Content-Type=application/json" \
  --body @item-definition.json

# Get item details
ITEM_ID="your-item-id"
az rest --method GET \
  --url "https://api.fabric.microsoft.com/v1/workspaces/$WORKSPACE_ID/items/$ITEM_ID" \
  | jq '.'
```

### Trigger Pipeline
```bash
# Run a pipeline
PIPELINE_ID="your-pipeline-id"
az rest --method POST \
  --url "https://api.fabric.microsoft.com/v1/workspaces/$WORKSPACE_ID/items/$PIPELINE_ID/jobs/instances?jobType=Pipeline" \
  --headers "Content-Type=application/json"

# Check pipeline run status
JOB_ID="job-instance-id"
az rest --method GET \
  --url "https://api.fabric.microsoft.com/v1/workspaces/$WORKSPACE_ID/items/$PIPELINE_ID/jobs/instances/$JOB_ID" \
  | jq '{status: .status, startTime: .startTimeUtc, endTime: .endTimeUtc}'
```

## Data Transfer with azcopy

### OneLake Operations
```bash
# Copy local files to OneLake
azcopy copy "./data/*" \
  "https://onelake.dfs.fabric.microsoft.com/$WORKSPACE_NAME/$LAKEHOUSE_NAME.Lakehouse/Files/landing/" \
  --recursive

# Copy from Azure Blob to OneLake
azcopy copy \
  "https://sourceaccount.blob.core.windows.net/container/path/*" \
  "https://onelake.dfs.fabric.microsoft.com/$WORKSPACE_NAME/$LAKEHOUSE_NAME.Lakehouse/Files/raw/" \
  --recursive

# Sync directories (only copy changed files)
azcopy sync "./local/data" \
  "https://onelake.dfs.fabric.microsoft.com/$WORKSPACE_NAME/$LAKEHOUSE_NAME.Lakehouse/Files/landing/" \
  --recursive

# List files in OneLake
azcopy list "https://onelake.dfs.fabric.microsoft.com/$WORKSPACE_NAME/$LAKEHOUSE_NAME.Lakehouse/Files/"

# Delete files
azcopy remove \
  "https://onelake.dfs.fabric.microsoft.com/$WORKSPACE_NAME/$LAKEHOUSE_NAME.Lakehouse/Files/temp/*" \
  --recursive
```

### Authentication for azcopy
```bash
# Option 1: Azure CLI auth (recommended)
azcopy login

# Option 2: Service Principal
azcopy login --service-principal \
  --application-id $AZURE_CLIENT_ID \
  --tenant-id $AZURE_TENANT_ID
# Then provide client secret when prompted

# Option 3: SAS token (append to URL)
azcopy copy "./data/*" \
  "https://onelake.dfs.fabric.microsoft.com/workspace/lakehouse.Lakehouse/Files/?$SAS_TOKEN" \
  --recursive
```

## REST API Deployment (Python alternative)

### Authentication
```python
from azure.identity import DefaultAzureCredential

credential = DefaultAzureCredential()
token = credential.get_token("https://api.fabric.microsoft.com/.default")
```

### Deploy Notebook
```python
import requests
import base64

def deploy_notebook(workspace_id, notebook_name, notebook_content, token):
    """Deploy notebook to workspace."""
    url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/notebooks"

    # Encode content
    encoded_content = base64.b64encode(notebook_content.encode()).decode()

    payload = {
        "displayName": notebook_name,
        "definition": {
            "format": "ipynb",
            "parts": [
                {
                    "path": "notebook.ipynb",
                    "payload": encoded_content,
                    "payloadType": "InlineBase64"
                }
            ]
        }
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()
```

### Deploy Pipeline
```python
def deploy_pipeline(workspace_id, pipeline_name, pipeline_json, token):
    """Deploy pipeline to workspace."""
    url = f"https://api.fabric.microsoft.com/v1/workspaces/{workspace_id}/dataPipelines"

    payload = {
        "displayName": pipeline_name,
        "definition": {
            "parts": [
                {
                    "path": "pipeline-content.json",
                    "payload": base64.b64encode(json.dumps(pipeline_json).encode()).decode(),
                    "payloadType": "InlineBase64"
                }
            ]
        }
    }

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)
    return response.json()
```

## Environment Configuration

### Parameter Files
```json
// config/dev.json
{
  "environment": "dev",
  "workspace": "Sales_Dev",
  "lakehouse": "lh_sales",
  "connections": {
    "salesforce": "conn_salesforce_sandbox"
  }
}

// config/prod.json
{
  "environment": "prod",
  "workspace": "Sales_Prod",
  "lakehouse": "lh_sales",
  "connections": {
    "salesforce": "conn_salesforce_prod"
  }
}
```

### Load Configuration
```python
import json

def load_config(environment):
    """Load environment-specific configuration."""
    with open(f"config/{environment}.json") as f:
        return json.load(f)

config = load_config("dev")
workspace = config["workspace"]
```

## CI/CD Integration

### GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy to Fabric

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  deploy-dev:
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    steps:
      - uses: actions/checkout@v3

      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Deploy to Dev
        run: |
          python scripts/deploy.py --env dev

  deploy-test:
    runs-on: ubuntu-latest
    needs: deploy-dev
    if: github.event_name == 'push'
    steps:
      - uses: actions/checkout@v3

      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}

      - name: Deploy to Test
        run: |
          python scripts/deploy.py --env test
```

### Azure DevOps Pipeline
```yaml
# azure-pipelines.yml
trigger:
  - main

pool:
  vmImage: 'ubuntu-latest'

stages:
  - stage: DeployDev
    jobs:
      - job: Deploy
        steps:
          - task: AzureCLI@2
            inputs:
              azureSubscription: 'fabric-connection'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                python scripts/deploy.py --env dev

  - stage: DeployTest
    dependsOn: DeployDev
    jobs:
      - job: Deploy
        steps:
          - task: AzureCLI@2
            inputs:
              azureSubscription: 'fabric-connection'
              scriptType: 'bash'
              scriptLocation: 'inlineScript'
              inlineScript: |
                python scripts/deploy.py --env test
```

## Deployment Script

```python
# scripts/deploy.py
import argparse
import json
import os
from azure.identity import DefaultAzureCredential

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True, choices=["dev", "test", "prod"])
    args = parser.parse_args()

    # Load config
    config = load_config(args.env)

    # Get token
    credential = DefaultAzureCredential()
    token = credential.get_token("https://api.fabric.microsoft.com/.default").token

    # Deploy artifacts
    deploy_notebooks(config, token)
    deploy_pipelines(config, token)

    print(f"Deployed to {args.env} successfully")

def deploy_notebooks(config, token):
    """Deploy all notebooks."""
    notebooks_dir = "notebooks/"
    for notebook_file in os.listdir(notebooks_dir):
        if notebook_file.endswith(".py"):
            with open(os.path.join(notebooks_dir, notebook_file)) as f:
                content = f.read()
            deploy_notebook(
                config["workspace_id"],
                notebook_file.replace(".py", ""),
                content,
                token
            )

def deploy_pipelines(config, token):
    """Deploy all pipelines."""
    pipelines_dir = "pipelines/"
    for pipeline_file in os.listdir(pipelines_dir):
        if pipeline_file.endswith(".json"):
            with open(os.path.join(pipelines_dir, pipeline_file)) as f:
                pipeline_json = json.load(f)
            deploy_pipeline(
                config["workspace_id"],
                pipeline_file.replace(".json", ""),
                pipeline_json,
                token
            )

if __name__ == "__main__":
    main()
```

## Best Practices

- Use Git integration for source control
- Use deployment pipelines for promotions
- Parameterize environment-specific values
- Test in lower environments first
- Use service principals for automation
- Document deployment procedures

## Anti-Patterns

- Don't deploy directly to production
- Don't hardcode environment values
- Don't skip testing stages
- Don't deploy without review
