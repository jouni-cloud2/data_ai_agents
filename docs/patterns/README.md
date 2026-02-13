# Implementation Patterns

Reusable patterns for data platform development across all platforms.

## Pattern Catalog

| Pattern | Description | Use Case |
|---------|-------------|----------|
| [API Ingestion](api-ingestion.md) | REST API data extraction | External data sources |
| [Incremental Load](incremental-load.md) | CDC, watermarks, merge strategies | Large/changing datasets |
| [SCD Type 2](scd-type-2.md) | Slowly Changing Dimensions | Dimensional modeling |
| [Error Handling](error-handling.md) | Retry, dead-letter, alerting | Pipeline reliability |
| [PII Mock Data Generation](pii-mock-data-generation.md) | Generate synthetic data for PII sources | Dev environment without production PII |

## Pattern Structure

Each pattern document includes:

1. **Problem**: What challenge does this solve?
2. **Solution**: High-level approach
3. **Implementation**: Platform-agnostic code
4. **Platform Variations**: Platform-specific considerations
5. **Anti-patterns**: What to avoid
6. **References**: Further reading

## How to Use

1. **Identify the pattern** needed for your use case
2. **Read the platform-agnostic** implementation
3. **Check platform variations** for your tech stack
4. **Adapt to your context** (naming, configuration)

## Contributing Patterns

When adding new patterns:

1. Use the pattern template structure
2. Include working code examples
3. Document platform variations
4. Link to official documentation

---

*Last Updated: 2026-02-09*
