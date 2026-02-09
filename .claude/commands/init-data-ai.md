---
name: init-data-ai
description: First-time setup of the Data AI Agents team - install tools, configure MCP servers, validate environment.
---

# Init Data AI Command

Initializes this AI team environment with required tools, MCP servers, and configurations. Run once after cloning this repository.

## Usage

```bash
/init-data-ai                        # Full setup
/init-data-ai check                  # Verify setup without installing
/init-data-ai tools                  # Install/update tools only
/init-data-ai mcp                    # Configure MCP servers only
```

## Behavior

When invoked, Claude acts as the **Setup Agent** and guides through environment initialization.

---

## Phase 1: Environment Check

### 1.1 Detect Operating System

```bash
uname -s  # Darwin (macOS), Linux, or Windows (via WSL)
```

### 1.2 Check Package Manager

**macOS:**
```bash
# Check for Homebrew
which brew && brew --version
```

**Linux:**
```bash
# Check for apt, yum, or dnf
which apt || which yum || which dnf
```

### 1.3 Present Environment

```markdown
## Environment Detection

| Check | Status | Details |
|-------|--------|---------|
| OS | [macOS/Linux/Windows] | [version] |
| Package Manager | [brew/apt/...] | [version] |
| Shell | [zsh/bash] | [version] |

Proceeding with setup...
```

---

## Phase 2: Install Prerequisites

### 2.1 Required Tools

| Tool | Purpose | Check Command |
|------|---------|---------------|
| `git` | Version control | `git --version` |
| `node` | MCP servers runtime | `node --version` |
| `npm` | Package management | `npm --version` |
| `jq` | JSON processing | `jq --version` |

### 2.2 Platform Tools

| Tool | Purpose | When Needed |
|------|---------|-------------|
| `az` | Azure CLI | Azure/Fabric projects |
| `terraform` | Infrastructure as Code | Terraform projects |
| `databricks` | Databricks CLI | Databricks projects |

### 2.3 Installation (macOS with Homebrew)

```bash
# Core tools
brew install git node jq

# Azure tools
brew install azure-cli
brew tap hashicorp/tap
brew install hashicorp/tap/terraform

# Databricks (if needed)
brew install databricks
```

### 2.4 Installation (Linux with apt)

```bash
# Core tools
sudo apt update
sudo apt install -y git nodejs npm jq

# Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Terraform
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

---

## Phase 3: Configure MCP Servers

### 3.1 Check Claude Code MCP Config

```bash
# Check existing MCP configuration
cat ~/.claude/mcp_settings.json 2>/dev/null || echo "No MCP config found"
```

### 3.2 Install MCP Servers

**Microsoft Docs MCP** (for Azure/Fabric documentation):
```bash
# Check if already installed
grep -q "microsoft-docs" ~/.claude/mcp_settings.json 2>/dev/null

# The microsoft-docs server is typically configured via Claude Code settings
# or installed as an npm package
```

**Azure MCP Server** (for Azure resource management):
```bash
# Install via npm (recommended for Claude Code)
npm install -g @azure/mcp

# Or use npx (no installation)
npx -y @azure/mcp@latest server start

# Python alternative
pip install msmcp-azure
```

**Fabric MCP Server** (for Microsoft Fabric development - Preview):
```bash
# Clone and build (dotnet required)
git clone https://github.com/microsoft/mcp.git
cd mcp
dotnet build servers/Fabric.Mcp.Server/src/Fabric.Mcp.Server.csproj --configuration Release

# Note: Executable will be at servers/Fabric.Mcp.Server/src/bin/Release/fabmcp
```

**Context7 MCP** (for library documentation):
```bash
# Similar check and install process
```

### 3.3 Update MCP Configuration

Present the recommended MCP configuration:

```markdown
## MCP Server Configuration

Recommended MCP servers for data platform development:

### Microsoft Docs
- **Purpose:** Official Azure and Fabric documentation
- **Tools:** `microsoft_docs_search`, `microsoft_code_sample_search`, `microsoft_docs_fetch`

### Azure MCP Server
- **Purpose:** Manage Azure resources, run CLI commands, deploy infrastructure
- **Tools:** 47+ Azure service integrations (AI Foundry, Storage, Databases, etc.)
- **Status:** Production (v1.0+)

### Fabric MCP Server
- **Purpose:** Fabric API access, item definitions, best practices
- **Tools:** Fabric template generation, API interactions
- **Status:** Public Preview

### Context7 (Optional)
- **Purpose:** Library and SDK documentation
- **Tools:** Context-aware documentation lookup

### Configuration

Add to your Claude Code settings or `~/.claude/mcp_settings.json`:

```json
{
  "mcpServers": {
    "microsoft-docs": {
      "command": "npx",
      "args": ["-y", "@anthropic/mcp-server-microsoft-docs"]
    },
    "azure": {
      "command": "npx",
      "args": ["-y", "@azure/mcp@latest", "server", "start"]
    },
    "fabric": {
      "command": "/path/to/mcp/servers/Fabric.Mcp.Server/src/bin/Release/fabmcp",
      "args": ["server", "start", "--mode", "all"]
    }
  }
}
```

**Note:** For Fabric MCP, replace `/path/to/` with your actual build path. Use `fabmcp.exe` on Windows.

**Azure Authentication:** Run `az login` before using Azure MCP Server.

Would you like me to update your MCP configuration? (yes/no)
```

---

## Phase 4: Validate Claude Code Setup

### 4.1 Check Claude Code Extension

```bash
# Check VS Code extensions
code --list-extensions 2>/dev/null | grep -i claude
```

### 4.2 Check Claude Code CLI

```bash
# Check if claude command is available
which claude
claude --version 2>/dev/null
```

### 4.3 Validate Settings

```bash
# Check local settings
cat .claude/settings.local.json 2>/dev/null | jq '.'
```

---

## Phase 5: Azure Setup (If Applicable)

### 5.1 Check Azure CLI Login

```bash
az account show 2>/dev/null
```

### 5.2 Guide Azure Login

```markdown
## Azure Configuration

Azure CLI is installed but not logged in.

### Login Options

1. **Interactive Login** (recommended for development):
   ```bash
   az login
   ```

2. **Service Principal** (for CI/CD):
   ```bash
   az login --service-principal -u <app-id> -p <password> --tenant <tenant>
   ```

3. **Managed Identity** (for Azure VMs):
   ```bash
   az login --identity
   ```

After login, select your subscription:
```bash
az account set --subscription "<subscription-name>"
```
```

### 5.3 Validate Azure Access

```bash
# List subscriptions
az account list --output table

# Check Fabric access (if applicable)
az resource list --resource-type "Microsoft.Fabric/capacities" --output table 2>/dev/null
```

---

## Phase 6: Terraform Setup (If Applicable)

### 6.1 Check Terraform

```bash
terraform --version
```

### 6.2 Initialize Backend (Optional)

```markdown
## Terraform Backend

For team collaboration, configure a remote backend.

### Azure Storage Backend

1. Create storage account for state:
   ```bash
   az group create -n rg-terraform-state -l westeurope
   az storage account create -n stterraformstate -g rg-terraform-state -l westeurope --sku Standard_LRS
   az storage container create -n tfstate --account-name stterraformstate
   ```

2. Configure backend in `terraform/backend.tf`:
   ```hcl
   terraform {
     backend "azurerm" {
       resource_group_name  = "rg-terraform-state"
       storage_account_name = "stterraformstate"
       container_name       = "tfstate"
       key                  = "data-platform.tfstate"
     }
   }
   ```

Would you like me to set this up? (yes/no/skip)
```

---

## Phase 7: Create Environment File

### 7.1 Check for .env

```bash
ls .env 2>/dev/null || ls .env.example 2>/dev/null
```

### 7.2 Create .env from Template

```bash
# If .env.example exists and .env doesn't
cp .env.example .env
```

### 7.3 Guide Configuration

```markdown
## Environment Configuration

Created `.env` from template. Please configure:

```bash
# Required
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_TENANT_ID=your-tenant-id

# For Fabric
FABRIC_WORKSPACE_ID=your-workspace-id

# For Terraform
TF_VAR_environment=dev
```

Edit `.env` with your values, then source it:
```bash
source .env
```
```

---

## Phase 8: Validation Summary

```markdown
## Setup Complete

### Tool Status

| Tool | Status | Version |
|------|--------|---------|
| git | ✅ | [version] |
| node | ✅ | [version] |
| npm | ✅ | [version] |
| jq | ✅ | [version] |
| az | ✅ | [version] |
| terraform | ✅ | [version] |

### MCP Servers

| Server | Status |
|--------|--------|
| microsoft-docs | ✅ Configured |
| azure | ✅ Configured |
| fabric | ✅ Configured (Preview) |
| context7 | ⚪ Optional |

### Azure

| Check | Status |
|-------|--------|
| CLI installed | ✅ |
| Logged in | ✅ |
| Subscription set | ✅ |

### Next Steps

1. **Set up a project:**
   ```bash
   /init-project <your-project-url>
   ```

2. **Plan architecture:**
   ```bash
   cd projects/<project>
   /architect
   ```

3. **Start development:**
   ```bash
   /sdd "Your first feature"
   ```

---

Data AI Agents ready for development!
```

---

## Check Mode

For `/init-data-ai check`:

Only validate, don't install:

```markdown
## Environment Check

### Required Tools

| Tool | Required | Installed | Version |
|------|----------|-----------|---------|
| git | ✅ | ✅ | 2.43.0 |
| node | ✅ | ❌ | - |
| npm | ✅ | ❌ | - |
| jq | ✅ | ✅ | 1.7.1 |

### Platform Tools

| Tool | For | Installed | Version |
|------|-----|-----------|---------|
| az | Azure | ✅ | 2.57.0 |
| terraform | IaC | ✅ | 1.7.0 |
| databricks | Databricks | ❌ | - |

### Missing Tools

Install with:
```bash
brew install node npm  # macOS
# or
sudo apt install nodejs npm  # Linux
```

Or run `/init-data-ai` for guided installation.
```

---

## Quick Reference

| Command | Action |
|---------|--------|
| `/init-data-ai` | Full guided setup |
| `/init-data-ai check` | Validate only |
| `/init-data-ai tools` | Install tools only |
| `/init-data-ai mcp` | Configure MCP only |
