# GCP Terraform Modules

Reusable Terraform modules for GCP data platform infrastructure.

## Available Modules

| Module | Status | Description |
|--------|--------|-------------|
| bigquery/ | Planned | BigQuery datasets and tables |
| gcs-bucket/ | Planned | Cloud Storage for data lake |
| iam/ | Planned | IAM bindings |
| secret-manager/ | Planned | Secret management |

## Provider Configuration

```hcl
terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.gcp_project
  region  = var.gcp_region
}
```

## Example Usage

```hcl
module "data_lake" {
  source = "./modules/gcp/gcs-bucket"

  name     = "dataplatform-${var.environment}"
  location = var.gcp_region

  folders = [
    "landing/",
    "bronze/",
    "silver/",
    "gold/"
  ]

  lifecycle_rules = {
    archive_after_days = 90
  }
}

module "bigquery" {
  source = "./modules/gcp/bigquery"

  dataset_id = "dataplatform_${var.environment}"
  location   = var.gcp_region

  tables = {
    bronze_events = {}
    silver_events = {}
    gold_metrics  = {}
  }
}
```

## References

- [GCP Terraform Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)
- [GCP Data Analytics](https://cloud.google.com/solutions/data-analytics)

---

*Last Updated: 2026-02-09*
