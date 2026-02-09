# Data Platform Principles

Platform-agnostic principles for building enterprise data platforms.

## Principles Index

| Principle | Description |
|-----------|-------------|
| [Well-Architected Framework](well-architected.md) | AWS/Azure framework pillars for data platforms |
| [Medallion Architecture](medallion-architecture.md) | Bronze/Silver/Gold layered data architecture |
| [Data Governance](data-governance.md) | Classification, ownership, stewardship |
| [Data Quality](data-quality.md) | Quality dimensions and validation patterns |
| [Security & Privacy](security-privacy.md) | PII handling, encryption, access control |
| [MDM Patterns](mdm-patterns.md) | Master Data Management approaches |
| [Environment Separation](environment-separation.md) | Dev/Test/Prod compliance and data isolation |

## How to Use

These principles apply across all platforms (Fabric, Databricks, Snowflake, etc.). Platform-specific implementations are in [platforms/](../platforms/).

### For AI Agents
Load relevant principles before making architectural decisions:
- Data classification impacts storage and access patterns
- PII handling affects transformation logic
- Quality rules inform validation code

### For Architects
Use as design constraints and review checklist:
- Does the design follow medallion architecture?
- Is data governance addressed?
- Are environments properly separated?

---

*Last Updated: 2026-02-09*
