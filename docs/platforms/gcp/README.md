# Google Cloud Platform Data Services

Platform-specific guidance for GCP data services.

> **Status**: Documentation planned. Contributions welcome.

## Overview

GCP provides powerful data services:
- **BigQuery**: Serverless data warehouse
- **Cloud Storage**: Object storage (data lake)
- **Dataflow**: Stream and batch processing (Apache Beam)
- **Dataproc**: Managed Spark/Hadoop
- **Pub/Sub**: Event messaging
- **Data Catalog**: Metadata management
- **Dataplex**: Data fabric/mesh

## When to Use GCP Services

| Service | Use Case |
|---------|----------|
| **BigQuery** | Serverless analytics, ML integration |
| **Cloud Storage** | Data lake storage |
| **Dataflow** | Streaming and batch ETL |
| **Dataproc** | Spark workloads |
| **Dataplex** | Data mesh architecture |

## Planned Documentation

- [ ] BigQuery dataset organization
- [ ] Cloud Storage bucket patterns
- [ ] Dataflow pipeline design
- [ ] Dataproc cluster configuration
- [ ] IAM and security
- [ ] Cost optimization

## Terraform Modules

See [terraform/modules/gcp/](../../../terraform/modules/gcp/) for ready-to-use infrastructure modules:
- BigQuery datasets
- Cloud Storage buckets
- IAM bindings
- VPC networking

## Key References

- [GCP Data Analytics](https://cloud.google.com/solutions/data-analytics)
- [BigQuery](https://cloud.google.com/bigquery/docs)
- [Dataflow](https://cloud.google.com/dataflow/docs)
- [Dataplex](https://cloud.google.com/dataplex/docs)
- [GCP Terraform Provider](https://registry.terraform.io/providers/hashicorp/google/latest/docs)

## Shared Principles

All GCP implementations follow:
- [Well-Architected Framework](../../principles/well-architected.md)
- [Data Governance](../../principles/data-governance.md)
- [Security & Privacy](../../principles/security-privacy.md)

---

*Last Updated: 2026-02-09*
