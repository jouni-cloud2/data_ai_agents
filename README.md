# Data AI Agents

An agentic AI team for building enterprise data platforms.

## What Is This?

This repository provides:
- **AI agent configuration** for Claude Code and GitHub Copilot
- **Shared documentation** on data platform principles and patterns
- **Platform-specific guidance** for Fabric, Databricks, Snowflake, and cloud providers
- **Terraform modules** for infrastructure as code

## Quick Start

### 1. Clone this repository

```bash
git clone https://github.com/your-org/data_ai_agents.git
cd data_ai_agents
```

### 2. Set up your project

```bash
# Create projects folder (gitignored)
mkdir -p projects

# Clone your project inside
cd projects
git clone https://github.com/your-org/your-project.git
```

### 3. Use Claude Code

Open the repo in VS Code with Claude Code extension and use the configured agents.

## Repository Structure

```
data_ai_agents/
├── .claude/                 # Claude Code configuration
│   ├── commands/            # Slash commands (/sdd, /document)
│   ├── skills/              # Agent skills and knowledge
│   └── workflows/           # Multi-step workflows
│
├── docs/                    # Shared documentation
│   ├── principles/          # Platform-agnostic principles
│   ├── patterns/            # Reusable implementation patterns
│   ├── platforms/           # Platform-specific guidance
│   │   ├── fabric/          # Microsoft Fabric (complete)
│   │   ├── databricks/      # Databricks (planned)
│   │   ├── snowflake/       # Snowflake (planned)
│   │   └── ...              # Azure, AWS, GCP
│   ├── templates/           # Documentation templates
│   └── mcp/                 # MCP server configuration
│
├── terraform/               # Terraform modules
│   └── modules/
│       ├── azure/           # Azure resources
│       ├── databricks/      # Databricks workspaces
│       └── ...              # Other platforms
│
├── projects/                # Your project subrepos (gitignored)
│
├── CLAUDE.md               # Claude Code entry point
└── README.md               # This file (human documentation)
```

## For Humans vs AI

| Audience | Start Here |
|----------|------------|
| **Humans** | This README, [docs/README.md](docs/README.md) |
| **Claude Code** | [CLAUDE.md](CLAUDE.md) |
| **GitHub Copilot** | `.github/copilot-instructions.md` |

## Supported Platforms

| Platform | Documentation | Terraform |
|----------|---------------|-----------|
| Microsoft Fabric | [Complete](docs/platforms/fabric/) | [Planned](terraform/modules/fabric/) |
| Databricks | [Planned](docs/platforms/databricks/) | [Planned](terraform/modules/databricks/) |
| Snowflake | [Planned](docs/platforms/snowflake/) | [Planned](terraform/modules/snowflake/) |
| Azure | [Planned](docs/platforms/azure/) | [Planned](terraform/modules/azure/) |
| AWS | [Planned](docs/platforms/aws/) | [Planned](terraform/modules/aws/) |
| GCP | [Planned](docs/platforms/gcp/) | [Planned](terraform/modules/gcp/) |

## Core Principles

All data platforms built with these agents follow:

| Principle | Description |
|-----------|-------------|
| [Medallion Architecture](docs/principles/medallion-architecture.md) | Bronze/Silver/Gold data layers |
| [Data Governance](docs/principles/data-governance.md) | Classification, ownership, stewardship |
| [Data Quality](docs/principles/data-quality.md) | Validation and monitoring |
| [Security & Privacy](docs/principles/security-privacy.md) | PII handling, access control |
| [Well-Architected](docs/principles/well-architected.md) | AWS/Azure best practices |
| [Environment Separation](docs/principles/environment-separation.md) | Dev/Test/Prod compliance |
| [MDM Patterns](docs/principles/mdm-patterns.md) | Master Data Management |

## Using with Claude Code

### Available Commands

| Command | Description |
|---------|-------------|
| `/sdd` | Spec-Driven Development workflow |
| `/document` | Documentation maintenance |
| `/improve-ai` | Improve agent configuration |

### MCP Servers

| Server | Purpose |
|--------|---------|
| `microsoft-docs` | Official Microsoft/Azure documentation |
| `context7` | Library and SDK documentation |

### Example Workflow

```
You: /sdd Add customer dimension table

Claude: [Creates spec, implements table, documents]
```

## Working with Projects

### Parent/Subrepo Model

```
data_ai_agents/           # Parent repo (agents + docs)
└── projects/             # Your work (gitignored)
    ├── client-a-fabric/  # Subrepo: Fabric project
    └── client-b-spark/   # Subrepo: Databricks project
```

### Project Documentation

Projects use templates from [docs/templates/](docs/templates/):
- Data catalog entries
- Source integration docs
- Runbooks
- Architecture Decision Records

## Contributing

### Adding a New Platform

1. Create `docs/platforms/{platform}/README.md`
2. Add platform-specific patterns
3. Create Terraform modules if applicable
4. Update platform table in this README

### Improving Agents

Use `/improve-ai` command or submit PRs to `.claude/` folder.

### Documentation

Follow the structure in [docs/DOCUMENTATION-PLAN.md](docs/DOCUMENTATION-PLAN.md).

## References

- [Claude Code Documentation](https://docs.anthropic.com/claude-code)
- [Terraform Registry](https://registry.terraform.io/)
- [Microsoft Fabric](https://learn.microsoft.com/fabric/)
- [Databricks](https://docs.databricks.com/)
- [Snowflake](https://docs.snowflake.com/)

## License

[Add your license here]

---

*Last Updated: 2026-02-09*
