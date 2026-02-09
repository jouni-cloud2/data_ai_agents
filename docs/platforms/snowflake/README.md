# Snowflake

Platform-specific guidance for building data platforms on Snowflake.

> **Status**: Documentation planned. Contributions welcome.

## Overview

Snowflake is a cloud data platform with:
- **Virtual Warehouses**: Scalable compute
- **Data Sharing**: Secure data exchange
- **Streams & Tasks**: Change data capture and scheduling
- **Snowpark**: Python/Java/Scala development
- **Time Travel**: Point-in-time queries

## When to Use Snowflake

| Use Case | Fit |
|----------|-----|
| SQL-heavy analytics | Excellent |
| Data sharing/marketplace | Excellent |
| Multi-cloud data warehouse | Excellent |
| Real-time streaming | Limited (via Snowpipe) |
| Complex ML pipelines | Consider Databricks |

## Planned Documentation

- [ ] Account and database structure
- [ ] Stage patterns for data loading
- [ ] Streams and Tasks for CDC
- [ ] Snowpark development standards
- [ ] Data sharing patterns
- [ ] Role-based access control
- [ ] Cost management
- [ ] Performance optimization

## Terraform Modules

See [terraform/modules/snowflake/](../../../terraform/modules/snowflake/) for ready-to-use infrastructure modules.

## Key References

- [Snowflake Documentation](https://docs.snowflake.com/)
- [Snowpark Python](https://docs.snowflake.com/en/developer-guide/snowpark/python/index)
- [Streams](https://docs.snowflake.com/en/user-guide/streams-intro)
- [Snowflake Terraform Provider](https://registry.terraform.io/providers/Snowflake-Labs/snowflake/latest/docs)

## Shared Principles

All Snowflake implementations follow:
- [Medallion Architecture](../../principles/medallion-architecture.md)
- [Data Governance](../../principles/data-governance.md)
- [Security & Privacy](../../principles/security-privacy.md)

---

*Last Updated: 2026-02-09*
