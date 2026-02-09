# Data AI Agents

AI team for building enterprise data platforms. Supports **Microsoft Fabric**, **Azure**, **Databricks**, **Snowflake**, and other cloud platforms.

## Setup

```bash
# 1. Clone and open in VS Code with Claude Code extension
git clone https://github.com/your-org/data_ai_agents.git
cd data_ai_agents
code .

# 2. Initialize the AI team
/init-data-ai

# 3. Set up your project
/init-project <git-url>
```

## Tools Installed

`/init-data-ai` installs and configures:

**Core Tools:**
- `git`, `node`, `npm`, `jq` (required)
- `python3`, `az`, `terraform`, `docker`, `yq` (recommended)

**Platform-Specific** (installed by `/init-project` based on detection):
- **Fabric**: `az`, `python3`, `azcopy`, `ruff`
- **Databricks**: `databricks`, `python3`
- **Snowflake**: `snowsql`, `python3`
- **AWS**: `aws`, `terraform`
- **GCP**: `gcloud`, `terraform`

**MCP Servers:**
- `microsoft-docs` - Microsoft/Azure/Fabric documentation
- `azure` - Azure resource management (47+ services)
- `fabric` - Microsoft Fabric API (Preview)
- `context7` - Library/SDK documentation (optional)

See [CLI Tools Reference](docs/cli-tools.md) for details.

## Commands

| Command | Purpose |
|---------|---------|
| `/init-data-ai` | Environment setup (first time) |
| `/init-project <url>` | Clone and configure project |
| `/architect` | Architecture guidance |
| `/sdd <description>` | Spec-Driven Development workflow |
| `/document [scope]` | Maintain documentation |
| `/improve-ai` | Generalize learnings to AI team |

## Repository Structure

```
data_ai_agents/              # This repo: AI team + generic knowledge
├── .claude/commands/        # Slash commands
├── docs/                    # Principles, patterns, platform guides
├── terraform/modules/       # Reusable IaC modules
└── projects/                # Your projects (gitignored)
    └── your-project/        # Project subrepo: actual work
        ├── fabric/          # Platform code (Fabric/Databricks/etc)
        ├── docs/            # Project docs (catalog, ADRs, sources)
        └── terraform/       # Project infrastructure
```

**Separation:**
- **Generic knowledge** → `data_ai_agents/docs/`
- **Project-specific** → `projects/your-project/docs/`

## Supported Platforms

| Platform | Status | Docs |
|----------|--------|------|
| **Microsoft Fabric** | Production | [docs/platforms/fabric/](docs/platforms/fabric/) |
| **Azure** | Production | [docs/platforms/azure/](docs/platforms/azure/) |
| **Databricks** | Planned | [docs/platforms/databricks/](docs/platforms/databricks/) |
| **Snowflake** | Planned | [docs/platforms/snowflake/](docs/platforms/snowflake/) |

## Core Principles

All platforms follow: [Medallion Architecture](docs/principles/medallion-architecture.md), [Data Governance](docs/principles/data-governance.md), [Data Quality](docs/principles/data-quality.md), [Security & Privacy](docs/principles/security-privacy.md), [Well-Architected](docs/principles/well-architected.md).

See [docs/principles/](docs/principles/) for details.

## Example Workflow

```bash
/init-data-ai                        # First time setup
/init-project <git-url>              # Clone project
cd projects/your-project

/architect                           # Plan architecture
/sdd "Add bronze_hubspot_contacts"  # Implement with SDD
/document                            # Audit and create docs
/improve-ai                          # Generalize patterns
```

## Documentation

| Audience | File | Purpose |
|----------|------|---------|
| **Developers** | [README.md](README.md) | Setup and commands |
| **AI Agents** | [CLAUDE.md](CLAUDE.md) | AI instructions |
| **Principles** | [docs/](docs/) | Patterns and guides |

## Troubleshooting

**Tool not found:** `/init-data-ai check` then `/init-data-ai tools`
**MCP not working:** `/init-data-ai mcp`
**Azure auth:** `az login && az account set --subscription <name>`
**Project detection:** Ensure you're in `projects/your-project/`

## References

[Claude Code](https://docs.anthropic.com/claude-code) • [Microsoft Fabric](https://learn.microsoft.com/fabric/) • [Azure](https://learn.microsoft.com/azure/) • [Terraform](https://www.terraform.io/)
