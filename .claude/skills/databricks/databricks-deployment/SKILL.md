---
name: databricks-deployment
description: Deploying artifacts to Databricks workspaces.
---

# Databricks Deployment Skill

## Deployment Methods

1. **Databricks Asset Bundles (DAB)** - Recommended
2. **Databricks CLI**
3. **REST API / SDK**
4. **Git Integration (Repos)**

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

## Best Practices

- Use Databricks Asset Bundles for IaC
- Parameterize environment-specific values
- Use service principals for production
- Version control all configurations
- Test in dev before promoting
- Use Git integration for notebooks

## Anti-Patterns

- Don't deploy directly to production
- Don't hardcode credentials
- Don't skip validation
- Don't use personal tokens in CI/CD
- Don't deploy without testing
