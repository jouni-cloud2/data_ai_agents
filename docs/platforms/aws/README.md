# AWS Data Services

Platform-specific guidance for AWS data services.

> **Status**: Documentation planned. Contributions welcome.

## Overview

AWS provides comprehensive data services:
- **Amazon Redshift**: Cloud data warehouse
- **AWS Glue**: Serverless ETL
- **Amazon S3**: Object storage (data lake)
- **Amazon Athena**: Serverless SQL queries
- **AWS Lake Formation**: Data lake governance
- **Amazon Kinesis**: Real-time streaming
- **Amazon EMR**: Managed Spark/Hadoop

## When to Use AWS Services

| Service | Use Case |
|---------|----------|
| **Redshift** | Enterprise data warehouse |
| **Glue** | Serverless ETL pipelines |
| **S3 + Athena** | Data lake with SQL access |
| **Lake Formation** | Centralized data governance |
| **EMR** | Large-scale Spark processing |
| **Kinesis** | Real-time data streaming |

## Planned Documentation

- [ ] S3 data lake organization
- [ ] Glue job patterns
- [ ] Redshift cluster design
- [ ] Lake Formation setup
- [ ] Athena query optimization
- [ ] IAM best practices
- [ ] Cost optimization

## Terraform Modules

See [terraform/modules/aws/](../../../terraform/modules/aws/) for ready-to-use infrastructure modules:
- S3 buckets with policies
- Glue databases and crawlers
- IAM roles and policies
- VPC and networking

## Key References

- [AWS Data Analytics](https://aws.amazon.com/big-data/datalakes-and-analytics/)
- [AWS Glue](https://docs.aws.amazon.com/glue/)
- [Amazon Redshift](https://docs.aws.amazon.com/redshift/)
- [Lake Formation](https://docs.aws.amazon.com/lake-formation/)
- [AWS Terraform Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

## Shared Principles

All AWS implementations follow:
- [Well-Architected Framework](../../principles/well-architected.md)
- [Data Governance](../../principles/data-governance.md)
- [Security & Privacy](../../principles/security-privacy.md)

---

*Last Updated: 2026-02-09*
