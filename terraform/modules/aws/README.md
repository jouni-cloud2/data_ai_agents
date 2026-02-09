# AWS Terraform Modules

Reusable Terraform modules for AWS data platform infrastructure.

## Available Modules

| Module | Status | Description |
|--------|--------|-------------|
| s3-bucket/ | Planned | S3 bucket for data lake |
| glue/ | Planned | Glue database, crawlers, jobs |
| iam/ | Planned | IAM roles and policies |
| secrets-manager/ | Planned | Secret management |

## Provider Configuration

```hcl
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}
```

## Example Usage

```hcl
module "data_lake" {
  source = "./modules/aws/s3-bucket"

  bucket_name = "dataplatform-${var.environment}-${var.aws_account_id}"

  folders = [
    "landing/",
    "bronze/",
    "silver/",
    "gold/"
  ]

  enable_versioning = true
  enable_encryption = true

  tags = {
    environment = var.environment
  }
}

module "glue_database" {
  source = "./modules/aws/glue"

  database_name = "dataplatform_${var.environment}"
  s3_location   = module.data_lake.bucket_arn
}
```

## References

- [AWS Terraform Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [AWS Data Lake Best Practices](https://docs.aws.amazon.com/prescriptive-guidance/latest/defining-bucket-names-data-lakes/)

---

*Last Updated: 2026-02-09*
