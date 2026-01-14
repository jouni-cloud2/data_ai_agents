# Data Platform AI Agents

AI-powered data platform development system that automates the journey from user story to production-ready code. Built for **Microsoft Fabric** and **Databricks**.

## Features

- **8 Specialized Agents** - Requirements gathering, architecture design, implementation, testing, deployment, documentation, and continuous learning
- **20 Reusable Skills** - Platform-specific patterns for Fabric and Databricks, plus shared ETL patterns
- **Automated Workflow** - Takes a user story through requirements → design → implementation → testing → PR
- **Self-Improving System** - Learning agent captures insights and improves agents/skills over time

## Quick Install

### Option 1: With npx (recommended)

```bash
curl -fsSL https://raw.githubusercontent.com/jouni-cloud2/data_ai_agents/main/install.sh | bash
```

### Option 2: Without Node.js

```bash
curl -fsSL https://raw.githubusercontent.com/jouni-cloud2/data_ai_agents/main/install-no-npx.sh | bash
```

### Option 3: Manual with degit

```bash
npx degit OWNER/REPO/.claude .claude --force
curl -fsSL https://raw.githubusercontent.com/OWNER/REPO/main/CLAUDE.md -o CLAUDE.md
mkdir -p pipelines notebooks sql tests docs config
```

> **Note:** Replace `OWNER/REPO` with the actual GitHub repository path after forking/cloning.

## Usage

After installation, use the main workflow command in Claude Code:

```bash
/develop-story "Add Salesforce as a data source"
```

This will:
1. **Gather Requirements** - Ask clarifying questions about platform, source, fields, etc.
2. **Design Architecture** - Create medallion architecture (Bronze/Silver/Gold) design
3. **Implement** - Generate pipelines, notebooks, SQL, and tests
4. **Test & Deploy** - Run quality checks and deploy to dev environment
5. **Create PR** - Generate documentation and create pull request
6. **Learn** (optional) - Update agents/skills with lessons learned

## What's Installed

```
.claude/
├── agents/                    # 8 Specialized AI agents
│   ├── requirements-analyst.md
│   ├── data-architect.md
│   ├── data-engineer-fabric.md
│   ├── data-engineer-databricks.md
│   ├── qa-engineer.md
│   ├── devops-engineer.md
│   ├── documentation-engineer.md
│   └── learning-agent.md
│
├── commands/                  # Workflow commands
│   └── develop-story.md
│
└── skills/                    # 20 Reusable skills
    ├── shared/               # Platform-agnostic (7 skills)
    │   ├── requirements-gathering/
    │   ├── data-modeling-standards/
    │   ├── etl-patterns/
    │   ├── sql-optimization/
    │   ├── data-quality-validation/
    │   ├── documentation-standards/
    │   └── continuous-improvement/
    │
    ├── fabric/               # Microsoft Fabric (6 skills)
    │   ├── fabric-architecture/
    │   ├── fabric-pipelines/
    │   ├── fabric-notebooks/
    │   ├── fabric-deployment/
    │   ├── fabric-testing/
    │   └── onelake-patterns/
    │
    └── databricks/           # Databricks (7 skills)
        ├── databricks-architecture/
        ├── databricks-workflows/
        ├── databricks-notebooks/
        ├── databricks-deployment/
        ├── databricks-testing/
        ├── unity-catalog/
        └── delta-live-tables/

CLAUDE.md                      # Project knowledge base (auto-updated)
```

## Supported Platforms

### Microsoft Fabric
- OneLake storage with folders (not schemas)
- Fabric pipelines (Copy Activity, Dataflow Gen2, Notebooks)
- Lakehouse architecture
- Domain-based workspace organization

### Databricks
- Unity Catalog governance (catalog.schema.table)
- Workflows and Delta Live Tables (DLT)
- Serverless compute
- Expectations for data quality

## Agents Overview

| Agent | Role |
|-------|------|
| **Requirements Analyst** | Gathers requirements through targeted questions |
| **Data Architect** | Designs medallion architecture, routes to platform skills |
| **Data Engineer (Fabric)** | Implements Fabric pipelines, notebooks, OneLake |
| **Data Engineer (Databricks)** | Implements workflows, DLT, Unity Catalog |
| **QA Engineer** | Tests implementations, validates data quality |
| **DevOps Engineer** | Manages git workflow, deployments, PRs |
| **Documentation Engineer** | Generates data dictionaries, runbooks, lineage |
| **Learning Agent** | Analyzes work and improves agents/skills |

## Architecture

The system follows the **medallion architecture** pattern:

```
Source → Bronze (Raw) → Silver (Cleaned) → Gold (Business) → Consumers
```

- **Bronze**: Raw data as-is with metadata (_ingested_at, _source_file)
- **Silver**: Cleaned, typed, PII masked, SCD Type 2
- **Gold**: Star schema, business KPIs, optimized for analytics

## Customization

### Adding New Skills

Create a new skill in `.claude/skills/[category]/[skill-name]/SKILL.md`:

```markdown
---
name: my-new-skill
description: What this skill provides
---

# My New Skill

## Overview
[Description]

## Patterns
[Code examples and best practices]
```

### Updating CLAUDE.md

The `CLAUDE.md` file serves as the project's knowledge base. It's automatically updated by the Learning Agent after each PR, but you can also manually add:
- Project-specific patterns
- Team conventions
- Lessons learned

## Contributing

1. Fork this repository
2. Make your changes
3. Test the installation scripts
4. Submit a pull request

## License

MIT

---

Built with Claude Code for data platform teams.
