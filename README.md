# Data AI Agents

AI-powered development team for building enterprise data platforms. Supports **Microsoft Fabric**, **Azure**, **Databricks**, **Snowflake**, and other cloud data platforms.

## For Developers

This README covers how to **set up and use** the AI agent team. For documentation structure and principles, see [docs/README.md](docs/README.md).

## Quick Start

```bash
# Clone this repository
git clone https://github.com/your-org/data_ai_agents.git
cd data_ai_agents

# Open in VS Code with Claude Code extension
code .

# Initialize the AI team (checks and installs required tools)
/init-data-ai
```

That's it! The `/init-data-ai` command will:
- Check for required CLI tools
- Install missing tools (with your confirmation)
- Configure MCP servers
- Validate your environment

Then use `/init-project <url>` to set up your first project.

## Required CLI Tools

The `/init-data-ai` command checks for these tools and helps install them:

### Core Tools

| Tool | Purpose |
|------|---------|
| `git` | Version control |
| `node` | MCP server runtime |
| `npm` | Node package manager |
| `jq` | JSON processing |

### Platform-Specific Tools

| Tool | When Required |
|------|---------------|
| `az` | Azure/Fabric projects |
| `terraform` | Infrastructure as Code |
| `databricks` | Databricks projects |
| `docker` | Containerized workflows |
| `yq` | YAML processing |

## Repository Structure

### Parent Repo (data_ai_agents)

Generic AI team configuration and documentation:

```
data_ai_agents/                    # Parent repo (this repo)
├── .claude/                       # AI agent configuration
│   ├── commands/                  # Slash commands
│   │   ├── sdd.md                 # Spec-Driven Development
│   │   ├── document.md            # Documentation maintenance
│   │   ├── architect.md           # Architecture guidance
│   │   ├── init-data-ai.md        # Environment setup
│   │   ├── init-project.md        # Project initialization
│   │   └── improve-ai.md          # AI team improvement
│   └── settings.json              # Claude Code settings
│
├── docs/                          # Shared documentation (principles, patterns)
│   ├── principles/                # Platform-agnostic principles
│   │   ├── medallion-architecture.md
│   │   ├── data-governance.md
│   │   └── data-quality.md
│   ├── patterns/                  # Reusable implementation patterns
│   ├── platforms/                 # Platform-specific guidance
│   │   ├── fabric/                # Microsoft Fabric
│   │   ├── azure/                 # Azure
│   │   ├── databricks/            # Databricks
│   │   └── snowflake/             # Snowflake
│   ├── templates/                 # Documentation templates for projects
│   └── DOCUMENTATION-PLAN.md      # Documentation system rules
│
├── terraform/                     # Terraform modules (IaC)
│   └── modules/
│       ├── azure/                 # Azure resources
│       ├── fabric/                # Fabric workspaces
│       ├── databricks/            # Databricks resources
│       └── snowflake/             # Snowflake resources
│
├── projects/                      # Project subrepos (gitignored)
│   ├── .gitignore                 # Ignores all projects/*
│   ├── client-a-fabric/           # Example: Fabric project
│   └── client-b-databricks/       # Example: Databricks project
│
├── CLAUDE.md                      # AI agent instructions
├── README.md                      # This file (developer guide)
└── .env.example                   # Environment variables template
```

### Project Subrepo Structure

Project-specific implementation and documentation:

```
projects/your-project/             # Your project (separate git repo)
├── fabric/                        # Platform-specific code (Fabric example)
│   ├── domain_name/               # Domain folder (sales, hr, finance)
│   │   ├── *.Notebook/            # Spark notebooks
│   │   ├── *.DataPipeline/        # Data pipelines
│   │   └── *.Warehouse/           # Warehouse items
│
├── docs/                          # Project documentation
│   ├── catalog/                   # Data catalog
│   │   ├── domain_name/           # Per domain
│   │   │   ├── bronze_source_entity.md
│   │   │   ├── silver_entity.md
│   │   │   └── gold_dim_entity.md
│   │   └── README.md              # Catalog index
│   ├── sources/                   # Source system docs
│   │   ├── source_name.md         # Per source (hubspot.md, salesforce.md)
│   │   └── README.md
│   ├── architecture/              # Architecture documentation
│   │   └── decisions/             # ADRs
│   │       ├── ADR-0001-*.md
│   │       └── README.md
│   ├── runbooks/                  # Operational procedures
│   │   ├── pipeline-failures.md
│   │   └── README.md
│   └── specs/                     # Spec-Driven Development specs
│       └── SDD-YYYYMMDD-*/        # Per SDD workflow
│
├── terraform/                     # Project infrastructure (if applicable)
│   ├── main.tf
│   ├── variables.tf
│   └── backend.tf
│
└── README.md                      # Project-specific README
```

## Parent vs Subrepo: What Goes Where?

| Content Type | Location | Example |
|--------------|----------|---------|
| **Generic principles** | `data_ai_agents/docs/principles/` | Medallion architecture, data governance |
| **Reusable patterns** | `data_ai_agents/docs/patterns/` | API ingestion, incremental loads |
| **Platform guidance** | `data_ai_agents/docs/platforms/{platform}/` | Fabric notebook standards |
| **Terraform modules** | `data_ai_agents/terraform/modules/` | Azure resource modules |
| **Project code** | `projects/your-project/` | Notebooks, pipelines, SQL |
| **Data catalog** | `projects/your-project/docs/catalog/` | Table documentation |
| **Source docs** | `projects/your-project/docs/sources/` | API documentation |
| **ADRs** | `projects/your-project/docs/architecture/` | Project decisions |
| **Runbooks** | `projects/your-project/docs/runbooks/` | Operational procedures |
| **Specs** | `projects/your-project/docs/specs/` | SDD specifications |

## Git Branching Strategy

### Parent Repo (data_ai_agents)

Single branch model for AI team configuration:

```
main                    # Stable AI team configuration
├── docs/              # Generic documentation
├── .claude/           # AI agent configuration
└── terraform/         # Reusable modules
```

**Branching:**
- Work on feature branches: `feature/improve-fabric-docs`
- Merge to `main` via PR
- No environment branches (this repo has no deployable code)

### Project Subrepos

Each project follows its own branching strategy. Recommended:

```
main                           # Production code
├── develop                    # Integration branch
│   ├── feature/add-customer-dim
│   └── feature/hubspot-integration
└── hotfix/pipeline-fix
```

**Common strategies:**
1. **Git Flow**: `main` + `develop` + feature branches
2. **GitHub Flow**: `main` + feature branches (simpler)
3. **Environment branches**: `main`, `test`, `develop` (if needed)

**The parent repo (data_ai_agents) doesn't dictate project branching.**

## Available Commands

Claude Code slash commands for data platform development:

| Command | Purpose | When to Use |
|---------|---------|-------------|
| `/init-data-ai` | Environment setup | First time after cloning this repo |
| `/init-project <url>` | Clone project subrepo | Setting up a new project |
| `/architect` | Architecture guidance | Planning features, making decisions |
| `/sdd <description>` | Spec-Driven Development | Implementing features with traceability |
| `/document [scope]` | Maintain documentation | Audit/create/update project docs |
| `/improve-ai` | Improve AI team | Capture learnings, improve agents |

### Command Examples

```bash
# First-time setup
/init-data-ai

# Set up a project
/init-project https://github.com/your-org/data-platform-fabric.git

# Plan architecture
/architect
# Ask questions like: "How should we structure customer data?"

# Implement with SDD
/sdd "Add HubSpot companies to bronze layer"
# Creates spec → implements → tests → documents

# Maintain documentation
/document                              # Full audit
/document bronze_hubspot_contacts      # Document specific table
/document sales                        # Audit sales domain
/document recent                       # Document recent git changes

# Improve the AI team
/improve-ai
# When you find patterns worth generalizing
```

## MCP Servers

Model Context Protocol servers provide AI agents with specialized tools:

| Server | Tools | Purpose |
|--------|-------|---------|
| `microsoft-docs` | `microsoft_docs_search`<br>`microsoft_code_sample_search`<br>`microsoft_docs_fetch` | Official Microsoft/Azure/Fabric documentation |
| `azure` | 47+ Azure service tools<br>Resource management<br>CLI commands<br>Deployments | Manage Azure resources and infrastructure |
| `fabric` | Fabric API access<br>Template generation<br>Item definitions | Microsoft Fabric development (Preview) |
| `context7` | `query-docs`<br>`resolve-library-id` | Library and SDK documentation |

**Configured automatically by `/init-data-ai`.**

## Supported Platforms

| Platform | Status | Documentation | Terraform Modules |
|----------|--------|---------------|-------------------|
| **Microsoft Fabric** | Production | [Complete](docs/platforms/fabric/) | Available |
| **Azure** | Production | [Available](docs/platforms/azure/) | Available |
| **Databricks** | Planned | [docs/platforms/databricks/](docs/platforms/databricks/) | Available |
| **Snowflake** | Planned | [docs/platforms/snowflake/](docs/platforms/snowflake/) | Available |
| **GCP** | Planned | [docs/platforms/gcp/](docs/platforms/gcp/) | Available |
| **AWS** | Planned | [docs/platforms/aws/](docs/platforms/aws/) | Available |

## Core Principles

All platforms follow these principles (see [docs/principles/](docs/principles/)):

| Principle | Description |
|-----------|-------------|
| [Medallion Architecture](docs/principles/medallion-architecture.md) | Bronze → Silver → Gold data layers |
| [Data Governance](docs/principles/data-governance.md) | Classification, ownership, stewardship |
| [Data Quality](docs/principles/data-quality.md) | Validation, monitoring, alerts |
| [Security & Privacy](docs/principles/security-privacy.md) | PII handling, access control, compliance |
| [Well-Architected](docs/principles/well-architected.md) | Cloud best practices (Azure, AWS) |
| [Environment Separation](docs/principles/environment-separation.md) | Dev/Test/Prod isolation |
| [MDM Patterns](docs/principles/mdm-patterns.md) | Master Data Management |

## Typical Workflow

```bash
# 1. Initialize environment (first time)
cd data_ai_agents
/init-data-ai

# 2. Set up project
/init-project https://github.com/your-org/your-project.git
cd projects/your-project

# 3. Plan architecture
/architect
# Discuss: "We need to ingest HubSpot data for sales analytics"

# 4. Implement with SDD
/sdd "Add HubSpot companies to bronze layer with incremental load"
# AI creates spec → implements notebook → adds tests → documents

# 5. Document existing work
/document
# AI audits catalog, identifies gaps, creates missing docs

# 6. Continue development
/sdd "Create silver_companies with deduplication"
/sdd "Build gold_dim_customer with SCD Type 2"

# 7. Improve AI team (when you find patterns)
/improve-ai
# Example: "Add HubSpot pagination pattern to docs/patterns/"
```

## For Humans vs AI

| Audience | Entry Point | Purpose |
|----------|-------------|---------|
| **Developers** (you) | [README.md](README.md) | Setup, commands, structure |
| **Claude Code** | [CLAUDE.md](CLAUDE.md) | AI agent instructions |
| **Documentation** | [docs/README.md](docs/README.md) | Principles, patterns, platform guides |

## Troubleshooting

### Tool not found

```bash
# Check what's missing
/init-data-ai check

# Install tools
/init-data-ai tools
```

### MCP server not working

```bash
# Re-configure MCP servers
/init-data-ai mcp

# Check MCP settings
cat ~/.claude/mcp_settings.json
```

### Project not detected

```bash
# Ensure you're in the project subrepo
cd projects/your-project

# Check platform detection
ls *.Notebook 2>/dev/null           # Fabric
ls databricks.yml 2>/dev/null       # Databricks
ls terraform/*.tf 2>/dev/null       # Terraform
```

### Azure CLI not authenticated

```bash
az login
az account set --subscription "<subscription-name>"
az account show
```

## Contributing

### To the AI Team (this repo)

1. **Improve documentation**: Add patterns, principles, platform guides
2. **Improve commands**: Enhance `.claude/commands/*.md`
3. **Add Terraform modules**: Create reusable IaC modules
4. **Use `/improve-ai`**: Let AI help generalize learnings

### To Project Subrepos

Follow project-specific contribution guidelines. Use `/sdd` for feature development.

## References

- [Claude Code](https://docs.anthropic.com/claude-code)
- [Microsoft Fabric](https://learn.microsoft.com/fabric/)
- [Azure](https://learn.microsoft.com/azure/)
- [Databricks](https://docs.databricks.com/)
- [Snowflake](https://docs.snowflake.com/)
- [Terraform](https://www.terraform.io/)

## License

[Add your license here]

---

*Last Updated: 2026-02-09*
