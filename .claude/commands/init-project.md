---
name: init-project
description: Set up a new project subrepo - clone, configure, and prepare for development.
---

# Init Project Command

Sets up a new project as a subrepo within this AI team structure.

## Usage

```bash
/init-project <git-url>              # Clone and set up project
/init-project <git-url> <name>       # Clone with custom folder name
/init-project local <path>           # Link existing local project
```

### Examples

```bash
/init-project https://github.com/company/client-fabric-project.git
/init-project git@github.com:company/data-platform.git my-project
/init-project local ../existing-project
```

## Behavior

When invoked, Claude acts as the **Project Setup Agent** and guides through project initialization.

---

## Phase 1: Validate Environment

### 1.1 Check Prerequisites

```bash
# Verify we're in the data_ai_agents root
ls CLAUDE.md .claude/commands/ projects/

# Verify git is available
git --version

# Check projects folder exists
mkdir -p projects
```

### 1.2 Parse Arguments

| Argument | Required | Description |
|----------|----------|-------------|
| `<git-url>` | Yes (unless local) | Git repository URL |
| `<name>` | No | Custom folder name (defaults to repo name) |
| `local` | Special | Indicates linking existing project |
| `<path>` | With local | Path to existing project |

---

## Phase 2: Clone/Link Project

### 2.1 For Git URL

```bash
cd projects

# Extract repo name if not provided
# https://github.com/company/my-project.git → my-project

# Clone the repository
git clone <git-url> <name>

cd <name>
```

### 2.2 For Local Project

```bash
cd projects

# Create symlink to existing project
ln -s <absolute-path> <name>

cd <name>
```

---

## Phase 3: Detect Platform

Scan the project to determine the data platform:

```bash
# Check for platform indicators
ls -la

# Fabric indicators
find . -name "*.Notebook" -type d 2>/dev/null | head -5

# Databricks indicators
ls databricks.yml .databricks/ 2>/dev/null

# Terraform indicators
ls terraform/*.tf 2>/dev/null

# dbt indicators
ls dbt_project.yml 2>/dev/null
```

### Present Detection Results

```markdown
## Project Setup

**Project:** {name}
**Source:** {git-url or local path}

### Platform Detection

| Indicator | Found | Platform |
|-----------|-------|----------|
| *.Notebook folders | [Yes/No] | Fabric |
| databricks.yml | [Yes/No] | Databricks |
| terraform/*.tf | [Yes/No] | IaC present |
| dbt_project.yml | [Yes/No] | dbt |

**Detected Platform:** [Fabric/Databricks/Unknown]

Is this correct? (yes/no/specify platform)
```

---

## Phase 4: Initialize Documentation Structure

Create project documentation structure if not exists:

### 4.1 Check Existing Structure

```bash
ls -la docs/ 2>/dev/null
```

### 4.2 Create Missing Folders

```bash
mkdir -p docs/catalog
mkdir -p docs/sources
mkdir -p docs/architecture/decisions
mkdir -p docs/runbooks
mkdir -p docs/specs
```

### 4.3 Create README Files

**docs/README.md** (if missing):
```markdown
# {Project Name} Documentation

## Structure

| Folder | Purpose |
|--------|---------|
| `catalog/` | Data catalog entries (tables, datasets) |
| `sources/` | Source system documentation |
| `architecture/decisions/` | Architecture Decision Records |
| `runbooks/` | Operational runbooks |
| `specs/` | SDD specifications |

## Quick Links

- [Architecture Overview](architecture/README.md)
- [Data Catalog](catalog/README.md)

## Parent Documentation

Generic patterns and principles are in the parent repo:
- Principles: `../../docs/principles/`
- Patterns: `../../docs/patterns/`
- Platform: `../../docs/platforms/{platform}/`
```

**docs/architecture/README.md** (if missing):
```markdown
# Architecture

## Overview

[Add architecture overview here after running `/architect`]

## Decisions

See [decisions/](decisions/) for Architecture Decision Records.

## Diagrams

[Add architecture diagrams here]
```

**docs/architecture/decisions/README.md** (if missing):
```markdown
# Architecture Decision Records

## Index

| ADR | Status | Title |
|-----|--------|-------|
| - | - | No decisions recorded yet |

## Creating New ADRs

Use `/architect` command to create architecture decisions.

Format: `ADR-{NNNN}-{slug}.md`
```

---

## Phase 5: Update .gitignore

Check and update the parent repo's .gitignore:

```bash
# Verify projects/ is gitignored in parent
cd ../..
grep -q "projects/" .gitignore || echo "projects/" >> .gitignore
```

---

## Phase 6: Platform-Specific Setup

### For Fabric Projects

```bash
# Check for workspace structure
find . -name "*.Workspace" -type d

# Check for environment configs
ls .env* config/ 2>/dev/null
```

Suggest:
- Workspace naming conventions
- OneLake connection setup
- Service principal configuration

### For Databricks Projects

```bash
# Check for cluster configs
ls databricks.yml clusters/ 2>/dev/null

# Check for Unity Catalog setup
grep -r "unity_catalog" . 2>/dev/null | head -5
```

Suggest:
- Workspace connection setup
- Unity Catalog configuration
- Cluster policies

### For Terraform Projects

```bash
# Check terraform structure
ls terraform/

# Check for backend config
grep -l "backend" terraform/*.tf 2>/dev/null
```

Suggest:
- Backend configuration
- Variable files setup
- Module structure

---

## Phase 7: Present Summary

```markdown
## Project Setup Complete

**Project:** {name}
**Location:** projects/{name}/
**Platform:** {platform}

### Created Structure

```
projects/{name}/
├── docs/
│   ├── README.md
│   ├── catalog/
│   ├── sources/
│   ├── architecture/
│   │   ├── README.md
│   │   └── decisions/
│   │       └── README.md
│   ├── runbooks/
│   └── specs/
└── [existing project files]
```

### Next Steps

1. **Architecture Planning**
   ```bash
   cd projects/{name}
   /architect
   ```

2. **Start Development**
   ```bash
   /sdd "Your first feature"
   ```

3. **Set Up Infrastructure** (if using Terraform)
   ```bash
   cd terraform
   terraform init
   ```

### Platform-Specific Recommendations

[Platform-specific next steps based on detection]

---

Project ready for development!
```

---

## Error Handling

### Clone Failures

```markdown
## Clone Failed

**Error:** {error message}

**Possible causes:**
1. Invalid URL or no access
2. SSH keys not configured
3. Network issues

**Solutions:**
- Check URL format: `https://...` or `git@...`
- Verify repository access permissions
- Try: `git clone {url}` manually to diagnose
```

### Existing Project

```markdown
## Project Already Exists

**Location:** projects/{name}/

**Options:**
1. Use existing project: Just `cd projects/{name}`
2. Remove and re-clone: `rm -rf projects/{name}` then retry
3. Use different name: `/init-project {url} {new-name}`
```

---

## Quick Reference

| Command | Result |
|---------|--------|
| `/init-project <url>` | Clone repo to projects/ |
| `/init-project <url> <name>` | Clone with custom name |
| `/init-project local <path>` | Symlink existing project |
