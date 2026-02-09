# Documentation Plan

## Overview

This document defines the documentation structure, rules, and standards for data platforms. The documentation serves two audiences:

1. **Human developers** (data engineers, new team members)
2. **AI agents** (Claude, GitHub Copilot, etc.)

## Design Principles

### 1. Single Source of Truth
Every piece of information has exactly one authoritative location. Cross-references are used instead of duplication.

### 2. Layered Access
- **Quick start** → `README.md`, `CLAUDE.md`
- **Understanding** → `docs/` (human-readable)
- **Implementation** → `.claude/skills/` (AI-consumable)
- **Reference** → Project-specific catalogs

### 3. Mandatory Documentation
No new data asset or architectural decision ships without documentation.

### 4. Living Documentation
Documentation is updated as part of implementation, not as a separate phase.

### 5. Multi-AI Tool Compatibility
Documentation works with both Claude Code and GitHub Copilot.

---

## Documentation Structure

### Parent Repository (data_ai_agents)

```
data_ai_agents/
├── README.md                       # Human entry point
├── CLAUDE.md                       # Claude Code entry point
│
├── .claude/
│   ├── commands/                   # Slash commands (/sdd, /document)
│   ├── skills/                     # Agent skills
│   └── workflows/                  # Multi-step workflows
│
├── docs/
│   ├── principles/                 # Platform-agnostic principles
│   ├── patterns/                   # Reusable patterns
│   ├── platforms/                  # Platform-specific docs
│   ├── templates/                  # Documentation templates
│   ├── architecture/               # ADR templates
│   └── mcp/                        # MCP server docs
│
├── terraform/                      # Infrastructure modules
│   └── modules/
│
└── projects/                       # Project subrepos (gitignored)
```

### Project Subrepos

Project-specific documentation lives in subrepos:

```
project-subrepo/
├── docs/
│   ├── catalog/                    # Data catalog entries
│   │   └── {domain}/
│   ├── sources/                    # Source system docs
│   ├── runbooks/                   # Operational runbooks
│   ├── architecture/
│   │   └── decisions/              # Project ADRs
│   └── specs/                      # SDD specifications
└── ...
```

---

## Content Ownership

| Content Type | Location | Owner |
|--------------|----------|-------|
| Core principles | `docs/principles/` | Data AI Agents repo |
| Implementation patterns | `docs/patterns/` | Data AI Agents repo |
| Platform docs | `docs/platforms/` | Data AI Agents repo |
| Templates | `docs/templates/` | Data AI Agents repo |
| Agent skills | `.claude/skills/` | Data AI Agents repo |
| Project catalogs | Project subrepo | Project team |
| Project sources | Project subrepo | Project team |
| Project runbooks | Project subrepo | Project team |
| Project ADRs | Project subrepo | Project team |

---

## Documentation Rules

### Rule 1: When to Create Documentation

| Event | Required Documentation | Location |
|-------|----------------------|----------|
| New table (Bronze/Silver/Gold) | Catalog entry | Project `docs/catalog/` |
| New source integration | Source doc | Project `docs/sources/` |
| Architectural decision | ADR | Project `docs/architecture/decisions/` |
| New pipeline pattern | Pattern doc | `docs/patterns/` or skill |
| Production incident | Runbook update | Project `docs/runbooks/` |

### Rule 2: Naming Conventions

| Document Type | Pattern | Example |
|---------------|---------|---------|
| Catalog entries | `{layer}_{source}_{entity}.md` | `bronze_hubspot_companies.md` |
| ADRs | `ADR-{NNNN}-{slug}.md` | `ADR-0001-domain-structure.md` |
| Source docs | `{source}.md` | `hubspot.md` |
| Runbooks | `{topic}.md` | `pipeline-failures.md` |

### Rule 3: Cross-Referencing

Use relative markdown links. Never duplicate content.

```markdown
<!-- Good: reference -->
See [Data Governance](../principles/data-governance.md) for classification rules.

<!-- Bad: duplication -->
## Data Classification
Public, Internal, Confidential, Restricted...  <!-- Copied from another file -->
```

### Rule 4: Templates

Use templates from `docs/templates/` for consistency:
- [Catalog Entry](templates/catalog-entry.md)
- [Source Integration](templates/source-integration.md)
- [Runbook](templates/runbook.md)
- [ADR](templates/adr.md)

---

## Commands

### /document Command

The `/document` command maintains documentation holistically.

```bash
# Audit modes
/document                    # Full documentation audit
/document audit              # Same as above
/document <domain>           # Audit specific domain
/document catalog            # Audit data catalog only
/document adrs               # Audit ADRs only
/document sources            # Audit source docs only
/document runbooks           # Audit runbooks only

# Create specific documentation
/document <table_name>       # Document specific table
/document "topic"            # Document a concept

# Improve existing documentation
/document improve <path>     # Enhance specific doc
```

### /sdd Command

Spec-Driven Development includes documentation as part of the workflow.

---

## Multi-AI Tool Strategy

### Claude Code

- Entry point: `CLAUDE.md`
- Skills: `.claude/skills/`
- Commands: `.claude/commands/`
- Activation: Manual via SDD workflow

### GitHub Copilot

- Entry point: `.github/copilot-instructions.md`
- Instructions: `.github/instructions/*.instructions.md`
- Activation: Auto via `applyTo` file patterns

### Content Strategy

| Content | Location | Used By |
|---------|----------|---------|
| Detailed patterns | `.claude/skills/` | Claude (primary) |
| File-specific rules | `.github/instructions/` | Copilot (auto) |
| Reference docs | `docs/` | Both + humans |

---

## Maintenance Rules

### When Adding to Parent Repo

1. Is it generic/reusable? → Add to `docs/`
2. Is it platform-specific? → Add to `docs/platforms/{platform}/`
3. Is it a pattern? → Add to `docs/patterns/`
4. Is it project-specific? → Add to project subrepo

### Quarterly Review

- [ ] Review and update principles
- [ ] Check for outdated patterns
- [ ] Archive deprecated content
- [ ] Update platform documentation

---

## References

- [MADR Format](https://adr.github.io/madr/)
- [Diátaxis Documentation Framework](https://diataxis.fr/)
- [GitHub Copilot Custom Instructions](https://docs.github.com/copilot/customizing-copilot/adding-custom-instructions-for-github-copilot)

---

*Last Updated: 2026-02-09*
