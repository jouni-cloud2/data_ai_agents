---
name: databricks-deployment
description: Deploying artifacts to Databricks workspaces.
tools: terraform, databricks, az
---

# Databricks Deployment Skill

## Available CLI Tools

| Tool | Purpose |
|------|---------|
| `terraform` | Infrastructure as Code for Databricks resources |
| `databricks` | Databricks CLI for workspace operations |
| `az` | Azure CLI for Azure Databricks management |

## Deployment Methods

1. **Terraform** - Recommended for infrastructure
2. **Databricks Asset Bundles (DAB)** - Recommended for jobs/pipelines
3. **Databricks CLI**
4. **REST API / SDK**
5. **Git Integration (Repos)**

## Databricks Asset Bundles (DAB)

### Project Structure
```
project/
+-- databricks.yml           # Main bundle config
+-- resources/
|   +-- jobs/
|   |   +-- etl_job.yml
|   +-- pipelines/
|       +-- dlt_pipeline.yml
+-- src/
|   +-- notebooks/
|   |   +-- ingest.py
|   |   +-- transform.py
|   +-- libraries/
|       +-- common/
|           +-- __init__.py
|           +-- utils.py
+-- tests/
|   +-- test_transform.py
+-- environments/
    +-- dev.yml
    +-- prod.yml
```

### Main Bundle Configuration
```yaml
# databricks.yml
bundle:
  name: salesforce_etl

workspace:
  host: https://workspace.cloud.databricks.com

include:
  - resources/*.yml
  - resources/**/*.yml

targets:
  dev:
    mode: development
    default: true
    workspace:
      host: https://dev.cloud.databricks.com

  staging:
    mode: staging
    workspace:
      host: https://staging.cloud.databricks.com

  prod:
    mode: production
    workspace:
      host: https://prod.cloud.databricks.com
    run_as:
      service_principal_name: sp-etl-prod
```

### Job Definition
```yaml
# resources/jobs/etl_job.yml
resources:
  jobs:
    salesforce_etl:
      name: "[${bundle.target}] Salesforce ETL"
      schedule:
        quartz_cron_expression: "0 0 2 * * ?"
        timezone_id: UTC
      tasks:
        - task_key: ingest
          notebook_task:
            notebook_path: ../src/notebooks/ingest.py
          new_cluster:
            spark_version: 14.3.x-scala2.12
            num_workers: 2

        - task_key: transform
          depends_on:
            - task_key: ingest
          notebook_task:
            notebook_path: ../src/notebooks/transform.py
```

### DLT Pipeline Definition
```yaml
# resources/pipelines/dlt_pipeline.yml
resources:
  pipelines:
    salesforce_dlt:
      name: "[${bundle.target}] Salesforce DLT"
      target: ${bundle.target}_salesforce
      development: ${bundle.target == "dev"}
      continuous: false
      channel: CURRENT
      libraries:
        - notebook:
            path: ../src/notebooks/dlt_pipeline.py
      configuration:
        source_path: s3://bucket/landing/salesforce/
```

### Environment Overrides
```yaml
# environments/prod.yml
targets:
  prod:
    resources:
      jobs:
        salesforce_etl:
          tasks:
            - task_key: ingest
              new_cluster:
                num_workers: 8
            - task_key: transform
              new_cluster:
                num_workers: 8
```

### DAB Commands
```bash
# Validate bundle
databricks bundle validate

# Deploy to dev
databricks bundle deploy --target dev

# Deploy to prod
databricks bundle deploy --target prod

# Run job
databricks bundle run salesforce_etl --target dev

# Destroy resources
databricks bundle destroy --target dev
```

## Databricks CLI

### Setup
```bash
# Install CLI
pip install databricks-cli

# Configure authentication
databricks configure --token
# Or use environment variables
export DATABRICKS_HOST=https://workspace.cloud.databricks.com
export DATABRICKS_TOKEN=dapi...
```

### Workspace Operations
```bash
# List files
databricks workspace ls /Repos

# Import notebook
databricks workspace import notebook.py /Workspace/project/notebook -l PYTHON

# Export notebook
databricks workspace export /Workspace/project/notebook ./local/notebook.py

# Import directory
databricks workspace import_dir ./local/notebooks /Workspace/project/notebooks
```

### Job Operations
```bash
# Create job
databricks jobs create --json @job_definition.json

# List jobs
databricks jobs list

# Run job
databricks jobs run-now --job-id 123

# Get run status
databricks runs get --run-id 456
```

### Cluster Operations
```bash
# Create cluster
databricks clusters create --json @cluster_config.json

# Start cluster
databricks clusters start --cluster-id abc123

# Delete cluster
databricks clusters delete --cluster-id abc123
```

## REST API / SDK

### Authentication
```python
from databricks.sdk import WorkspaceClient

# Using environment variables (DATABRICKS_HOST, DATABRICKS_TOKEN)
w = WorkspaceClient()

# Or explicit config
w = WorkspaceClient(
    host="https://workspace.cloud.databricks.com",
    token="dapi..."
)
```

### Deploy Notebook
```python
import base64

def deploy_notebook(w, local_path, remote_path):
    """Deploy notebook to workspace."""
    with open(local_path, "rb") as f:
        content = base64.b64encode(f.read()).decode()

    w.workspace.import_(
        path=remote_path,
        format="SOURCE",
        language="PYTHON",
        content=content,
        overwrite=True
    )
    print(f"Deployed {local_path} to {remote_path}")
```

### Create/Update Job
```python
from databricks.sdk.service.jobs import *

def deploy_job(w, job_config):
    """Create or update job."""
    # Check if job exists
    jobs = w.jobs.list(name=job_config["name"])

    if jobs:
        job_id = list(jobs)[0].job_id
        w.jobs.reset(job_id, JobSettings(**job_config))
        print(f"Updated job {job_id}")
    else:
        job = w.jobs.create(**job_config)
        print(f"Created job {job.job_id}")

    return job_id

# Job configuration
job_config = {
    "name": "Salesforce ETL",
    "tasks": [
        {
            "task_key": "ingest",
            "notebook_task": {
                "notebook_path": "/Repos/project/notebooks/ingest"
            }
        }
    ],
    "schedule": {
        "quartz_cron_expression": "0 0 2 * * ?",
        "timezone_id": "UTC"
    }
}
```

### Create DLT Pipeline
```python
def deploy_dlt_pipeline(w, pipeline_config):
    """Create or update DLT pipeline."""
    pipelines = w.pipelines.list_pipelines(filter=f"name = '{pipeline_config['name']}'")

    if pipelines.statuses:
        pipeline_id = pipelines.statuses[0].pipeline_id
        w.pipelines.update(
            pipeline_id=pipeline_id,
            **pipeline_config
        )
        print(f"Updated pipeline {pipeline_id}")
    else:
        pipeline = w.pipelines.create(**pipeline_config)
        print(f"Created pipeline {pipeline.pipeline_id}")
```

## Git Integration (Repos)

### Setup Repo
```python
# Create repo connection
w.repos.create(
    url="https://github.com/org/repo",
    provider="gitHub",
    path="/Repos/production/project"
)

# Update to branch
w.repos.update(
    repo_id="repo-id",
    branch="main"
)
```

### CI/CD with Repos
```yaml
# GitHub Actions
name: Deploy to Databricks

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install Databricks CLI
        run: pip install databricks-cli

      - name: Update Repo
        env:
          DATABRICKS_HOST: ${{ secrets.DATABRICKS_HOST }}
          DATABRICKS_TOKEN: ${{ secrets.DATABRICKS_TOKEN }}
        run: |
          databricks repos update \
            --path /Repos/production/project \
            --branch main
```

## Environment Configuration

### Config File Structure
```python
# config/environments.py
ENVIRONMENTS = {
    "dev": {
        "catalog": "development",
        "workspace_url": "https://dev.cloud.databricks.com",
        "cluster_size": "small"
    },
    "staging": {
        "catalog": "staging",
        "workspace_url": "https://staging.cloud.databricks.com",
        "cluster_size": "medium"
    },
    "prod": {
        "catalog": "production",
        "workspace_url": "https://prod.cloud.databricks.com",
        "cluster_size": "large"
    }
}

def get_config(env):
    return ENVIRONMENTS[env]
```

### Use in Notebooks
```python
# Get environment from widget or bundle variable
env = dbutils.widgets.get("environment")

# Load config
from config.environments import get_config
config = get_config(env)

# Use config
catalog = config["catalog"]
spark.sql(f"USE CATALOG {catalog}")
```

## Deployment Script

```python
# deploy.py
import argparse
from databricks.sdk import WorkspaceClient
import os

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", required=True, choices=["dev", "staging", "prod"])
    args = parser.parse_args()

    # Setup client
    w = WorkspaceClient()

    # Deploy notebooks
    deploy_notebooks(w, args.env)

    # Deploy jobs
    deploy_jobs(w, args.env)

    # Deploy DLT pipelines
    deploy_pipelines(w, args.env)

    print(f"Deployed to {args.env}")

def deploy_notebooks(w, env):
    """Deploy all notebooks."""
    notebooks_dir = "src/notebooks"
    remote_path = f"/Repos/{env}/project/notebooks"

    for notebook in os.listdir(notebooks_dir):
        if notebook.endswith(".py"):
            deploy_notebook(
                w,
                os.path.join(notebooks_dir, notebook),
                f"{remote_path}/{notebook}"
            )

if __name__ == "__main__":
    main()
```

## Terraform Deployment

### Provider Configuration
```hcl
# providers.tf
terraform {
  required_providers {
    databricks = {
      source  = "databricks/databricks"
      version = "~> 1.0"
    }
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

# Configure Azure provider
provider "azurerm" {
  features {}
}

# Configure Databricks provider (Azure)
provider "databricks" {
  host = azurerm_databricks_workspace.this.workspace_url
}
```

### Workspace Resources
```hcl
# main.tf

# Create Azure Databricks workspace
resource "azurerm_databricks_workspace" "this" {
  name                = "dbw-${var.project}-${var.environment}"
  resource_group_name = var.resource_group_name
  location            = var.location
  sku                 = var.sku  # "standard" or "premium"

  custom_parameters {
    no_public_ip = true
    virtual_network_id = var.vnet_id
    public_subnet_name = var.public_subnet_name
    private_subnet_name = var.private_subnet_name
  }

  tags = var.tags
}

# Unity Catalog metastore assignment
resource "databricks_metastore_assignment" "this" {
  metastore_id = var.metastore_id
  workspace_id = azurerm_databricks_workspace.this.workspace_id
}
```

### Unity Catalog Resources
```hcl
# unity_catalog.tf

# Create catalog
resource "databricks_catalog" "this" {
  name    = "${var.project}_${var.environment}"
  comment = "Catalog for ${var.project} ${var.environment}"

  properties = {
    environment = var.environment
    project     = var.project
  }
}

# Create schemas
resource "databricks_schema" "bronze" {
  catalog_name = databricks_catalog.this.name
  name         = "bronze"
  comment      = "Raw data landing zone"
}

resource "databricks_schema" "silver" {
  catalog_name = databricks_catalog.this.name
  name         = "silver"
  comment      = "Cleaned and transformed data"
}

resource "databricks_schema" "gold" {
  catalog_name = databricks_catalog.this.name
  name         = "gold"
  comment      = "Business-ready data"
}

# Create external location
resource "databricks_external_location" "landing" {
  name            = "landing_${var.environment}"
  url             = "abfss://landing@${var.storage_account}.dfs.core.windows.net/"
  credential_name = databricks_storage_credential.this.name
  comment         = "Landing zone for raw files"
}
```

### Job Resources
```hcl
# jobs.tf

resource "databricks_job" "etl" {
  name = "[${var.environment}] ${var.source_name} ETL"

  schedule {
    quartz_cron_expression = var.schedule_cron
    timezone_id            = "UTC"
  }

  task {
    task_key = "ingest"

    notebook_task {
      notebook_path = "/Repos/${var.environment}/project/notebooks/ingest"
      base_parameters = {
        environment = var.environment
        source      = var.source_name
      }
    }

    new_cluster {
      spark_version = var.spark_version
      num_workers   = var.cluster_workers

      node_type_id = var.node_type

      spark_conf = {
        "spark.databricks.delta.optimizeWrite.enabled" = "true"
      }
    }
  }

  task {
    task_key = "transform"
    depends_on {
      task_key = "ingest"
    }

    notebook_task {
      notebook_path = "/Repos/${var.environment}/project/notebooks/transform"
    }
  }

  email_notifications {
    on_failure = var.alert_emails
  }
}
```

### DLT Pipeline Resource
```hcl
# dlt.tf

resource "databricks_pipeline" "dlt" {
  name    = "[${var.environment}] ${var.source_name} DLT"
  target  = "${var.environment}_${var.source_name}"
  edition = "ADVANCED"
  channel = "CURRENT"

  cluster {
    label       = "default"
    num_workers = var.dlt_workers

    custom_tags = {
      environment = var.environment
    }
  }

  library {
    notebook {
      path = "/Repos/${var.environment}/project/notebooks/dlt_pipeline"
    }
  }

  configuration = {
    "source_path" = var.source_path
    "environment" = var.environment
  }

  continuous = false
  development = var.environment == "dev"
}
```

### Terraform Commands
```bash
# Initialize terraform
terraform init

# Plan changes
terraform plan \
  -var="environment=dev" \
  -var="project=salesforce" \
  -out=tfplan

# Apply changes
terraform apply tfplan

# Apply with variables file
terraform apply \
  -var-file="environments/dev.tfvars"

# Destroy resources
terraform destroy \
  -var-file="environments/dev.tfvars"

# Import existing resource
terraform import \
  databricks_job.etl \
  "12345"  # job_id
```

### Environment Variables Files
```hcl
# environments/dev.tfvars
environment        = "dev"
project            = "salesforce"
location           = "westeurope"
sku                = "premium"
spark_version      = "14.3.x-scala2.12"
cluster_workers    = 2
node_type          = "Standard_DS3_v2"
schedule_cron      = "0 0 2 * * ?"
alert_emails       = ["dev-team@company.com"]

# environments/prod.tfvars
environment        = "prod"
project            = "salesforce"
location           = "westeurope"
sku                = "premium"
spark_version      = "14.3.x-scala2.12"
cluster_workers    = 8
node_type          = "Standard_DS4_v2"
schedule_cron      = "0 0 1 * * ?"
alert_emails       = ["data-ops@company.com"]
```

### Azure CLI for Databricks
```bash
# Get Databricks workspace info
az databricks workspace show \
  --name "dbw-project-dev" \
  --resource-group "rg-databricks-dev"

# List workspaces
az databricks workspace list \
  --resource-group "rg-databricks" \
  | jq '.[] | {name: .name, url: .workspaceUrl}'

# Create workspace
az databricks workspace create \
  --name "dbw-project-dev" \
  --resource-group "rg-databricks-dev" \
  --location "westeurope" \
  --sku premium

# Delete workspace
az databricks workspace delete \
  --name "dbw-project-dev" \
  --resource-group "rg-databricks-dev"
```

## Best Practices

- Use Terraform for infrastructure (workspaces, catalogs, schemas)
- Use Databricks Asset Bundles for jobs and pipelines
- Parameterize environment-specific values
- Use service principals for production
- Version control all configurations
- Test in dev before promoting
- Use Git integration for notebooks
- Store Terraform state in remote backend (Azure Storage)

## Anti-Patterns

- Don't deploy directly to production
- Don't hardcode credentials
- Don't skip validation
- Don't use personal tokens in CI/CD
- Don't deploy without testing
- Don't store Terraform state locally in CI/CD
