# Documentation Index

This documentation supports AI agents building enterprise data platforms.

## Navigation

| I want to... | Go to... |
|--------------|----------|
| Understand core principles | [Principles](principles/) |
| Find implementation patterns | [Patterns](patterns/) |
| Get platform-specific guidance | [Platforms](platforms/) |
| Use documentation templates | [Templates](templates/) |
| Configure MCP servers | [MCP](mcp/) |
| Understand architecture decisions | [Architecture](architecture/) |

## Documentation Structure

```
docs/
├── principles/        # Platform-agnostic data principles
├── patterns/          # Reusable implementation patterns
├── platforms/         # Platform-specific guidance
│   ├── fabric/        # Microsoft Fabric (complete)
│   ├── databricks/    # Databricks (planned)
│   ├── snowflake/     # Snowflake (planned)
│   ├── azure/         # Azure services (planned)
│   ├── aws/           # AWS services (planned)
│   └── gcp/           # GCP services (planned)
├── templates/         # Templates for project documentation
├── architecture/      # ADR templates and reference architectures
└── mcp/               # MCP server configuration
```

## By Audience

### For AI Agents (Claude Code)
1. Read [CLAUDE.md](../CLAUDE.md) for skills and commands
2. Reference [Principles](principles/) for governance rules
3. Use [Patterns](patterns/) for implementation guidance
4. Check [Platforms](platforms/) for technology-specific details

### For Data Engineers
1. Start with [Principles](principles/) for data governance
2. Check [Patterns](patterns/) before implementing
3. Use [Templates](templates/) for documentation
4. Reference platform docs for your tech stack

### For Architects
1. Review [Principles](principles/) for design constraints
2. See [Architecture](architecture/) for ADR templates
3. Check platform docs for capability comparisons

## Platform Status

| Platform | Documentation | Status |
|----------|---------------|--------|
| [Microsoft Fabric](platforms/fabric/) | Complete | Production |
| [Databricks](platforms/databricks/) | Stub | Planned |
| [Snowflake](platforms/snowflake/) | Stub | Planned |
| [Azure](platforms/azure/) | Stub | Planned |
| [AWS](platforms/aws/) | Stub | Planned |
| [GCP](platforms/gcp/) | Stub | Planned |

## Project Documentation

This repository contains **generic** documentation only. Project-specific documentation (catalogs, source docs, runbooks) lives in project subrepos.

Use [Templates](templates/) to create project documentation.

---

*Last Updated: 2026-02-09*
