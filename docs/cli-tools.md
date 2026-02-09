# CLI Tools Reference

Reference documentation for CLI tools used by AI agents for data platform development. This document categorizes tools by necessity and platform, enabling the `/init-data-ai` and `/init-project` commands to install appropriate tools.

## Tool Categories

### Core Tools (Always Required)

These tools are required for all projects and the AI team functionality.

| Tool | Purpose | Check Command | Priority |
|------|---------|---------------|----------|
| `git` | Version control for code and notebooks | `git --version` | Critical |
| `node` | Runtime for MCP servers and JavaScript tools | `node --version` | Critical |
| `npm` | Node package manager for MCP servers | `npm --version` | Critical |
| `jq` | JSON processing (parse API responses, `.platform` files) | `jq --version` | Critical |

**Installation:**

```bash
# macOS (Homebrew)
brew install git node jq

# Linux (apt)
sudo apt update
sudo apt install -y git nodejs npm jq

# Linux (yum/dnf)
sudo yum install -y git nodejs npm jq
```

---

### Generic Platform Tools

Tools useful across multiple data platforms.

| Tool | Purpose | Platforms | Check Command | Priority |
|------|---------|-----------|---------------|----------|
| `python3` | Python runtime for scripts and notebooks | All | `python3 --version` | High |
| `pip3` | Python package manager | All | `pip3 --version` | High |
| `az` | Azure CLI for authentication and resource management | Azure, Fabric | `az --version` | High |
| `terraform` | Infrastructure as Code | All | `terraform --version` | Medium |
| `docker` | Containerization and local development | All | `docker --version` | Medium |
| `yq` | YAML processing for config files | All | `yq --version` | Medium |

**Installation:**

```bash
# macOS (Homebrew)
brew install python3 azure-cli
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
brew install docker yq

# Linux (apt) - Azure CLI
sudo apt install -y python3 python3-pip yq
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# Linux - Terraform
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform
```

---

## Platform-Specific Tools

### Microsoft Fabric

| Tool | Purpose | Check Command | Priority |
|------|---------|---------------|----------|
| `az` | Azure CLI (required for Fabric authentication) | `az --version` | Critical |
| `python3` | Notebook development | `python3 --version` | High |
| `terraform` | Workspace and capacity provisioning | `terraform --version` | Medium |
| `azcopy` | Bulk data transfers to/from OneLake | `azcopy --version` | Low |
| `ruff` | Python linting for notebooks | `ruff --version` | Low |

**Installation:**

```bash
# macOS
brew install azure-cli azcopy ruff

# Linux
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
pip3 install ruff
```

**Authentication:**

```bash
az login
az account set --subscription "<subscription-name>"
```

---

### Azure Infrastructure

| Tool | Purpose | Check Command | Priority |
|------|---------|---------------|----------|
| `az` | Azure CLI | `az --version` | Critical |
| `terraform` | Infrastructure provisioning | `terraform --version` | Critical |
| `azcopy` | Storage transfers | `azcopy --version` | Medium |
| `terraform-docs` | Generate IaC documentation | `terraform-docs --version` | Low |
| `tflint` | Terraform linting | `tflint --version` | Low |
| `checkov` | Infrastructure security scanning | `checkov --version` | Low |
| `trivy` | Vulnerability scanning | `trivy --version` | Low |
| `infracost` | Cost estimation | `infracost --version` | Low |

**Installation:**

```bash
# macOS
brew install terraform tflint terraform-docs checkov trivy infracost

# Linux
# Terraform - see Generic Platform Tools
curl -s https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash
pip3 install checkov
```

---

### Databricks

| Tool | Purpose | Check Command | Priority |
|------|---------|---------------|----------|
| `databricks` | Databricks CLI | `databricks --version` | Critical |
| `python3` | Notebook development | `python3 --version` | High |
| `terraform` | Workspace and cluster provisioning | `terraform --version` | Medium |

**Installation:**

```bash
# macOS
brew tap databricks/tap
brew install databricks

# Linux
curl -fsSL https://raw.githubusercontent.com/databricks/setup-cli/main/install.sh | sh

# Python alternative
pip3 install databricks-cli
```

**Authentication:**

```bash
databricks configure --token
```

---

### Snowflake

| Tool | Purpose | Check Command | Priority |
|------|---------|---------------|----------|
| `snowsql` | Snowflake CLI | `snowsql --version` | High |
| `python3` | Snowpark development | `python3 --version` | High |
| `terraform` | Snowflake provisioning | `terraform --version` | Medium |

**Installation:**

```bash
# macOS
brew install snowflake-cli

# Linux
pip3 install snowflake-cli-labs

# Or download from Snowflake
curl -O https://sfc-repo.snowflakecomputing.com/snowsql/bootstrap/latest/linux_x86_64/snowsql-linux_x86_64.bash
```

---

### AWS

| Tool | Purpose | Check Command | Priority |
|------|---------|---------------|----------|
| `aws` | AWS CLI | `aws --version` | Critical |
| `terraform` | Infrastructure provisioning | `terraform --version` | High |
| `python3` | Lambda and Glue development | `python3 --version` | High |

**Installation:**

```bash
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

---

### GCP

| Tool | Purpose | Check Command | Priority |
|------|---------|---------------|----------|
| `gcloud` | Google Cloud CLI | `gcloud --version` | Critical |
| `terraform` | Infrastructure provisioning | `terraform --version` | High |
| `python3` | Dataflow and Cloud Functions development | `python3 --version` | High |

**Installation:**

```bash
# macOS
brew install google-cloud-sdk

# Linux
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

---

## Code Quality & CI/CD Tools

Optional tools for production-grade development.

| Tool | Purpose | When Needed | Check Command |
|------|---------|-------------|---------------|
| `pre-commit` | Git hooks framework | Production projects | `pre-commit --version` |
| `yamllint` | YAML validation | YAML-heavy projects | `yamllint --version` |
| `shellcheck` | Shell script linting | Bash scripts | `shellcheck --version` |
| `gh` | GitHub CLI for workflows and PRs | GitHub projects | `gh --version` |
| `ruff` | Python linting and formatting | Python/notebook projects | `ruff --version` |

**Installation:**

```bash
# macOS
brew install pre-commit yamllint shellcheck gh ruff

# Linux
pip3 install pre-commit yamllint
sudo apt install -y shellcheck
# gh - see https://cli.github.com/
pip3 install ruff
```

---

## Tool Detection Logic

### For `/init-data-ai`

Install **Core Tools** always, plus **Generic Platform Tools** that are commonly needed:

1. **Critical**: `git`, `node`, `npm`, `jq`
2. **High Priority**: `python3`, `az` (if Azure/Fabric user)
3. **Recommended**: `terraform`, `docker`

### For `/init-project`

Detect platform and install **Platform-Specific Tools**:

```bash
# Detection logic
if [[ -d *.Notebook ]]; then
  PLATFORM="fabric"
  REQUIRED_TOOLS="az python3"
  RECOMMENDED_TOOLS="terraform azcopy ruff"
elif [[ -f "databricks.yml" ]]; then
  PLATFORM="databricks"
  REQUIRED_TOOLS="databricks python3"
  RECOMMENDED_TOOLS="terraform"
elif [[ -d "terraform" && grep -q "aws" terraform/*.tf ]]; then
  PLATFORM="aws"
  REQUIRED_TOOLS="aws terraform"
  RECOMMENDED_TOOLS="python3"
# ... more platforms
fi
```

---

## Tool Priority Levels

| Priority | Meaning | Action |
|----------|---------|--------|
| **Critical** | Required for basic functionality | Install automatically with confirmation |
| **High** | Needed for most development tasks | Strongly recommend, ask to install |
| **Medium** | Useful for advanced features | Suggest installation, optional |
| **Low** | Nice to have, quality improvements | Mention, don't install by default |

---

## Installation Templates

### Check Tool Availability

```bash
check_tool() {
  local tool=$1
  local cmd=$2
  if command -v $cmd &> /dev/null; then
    version=$($cmd --version 2>&1 | head -1)
    echo "✅ $tool: $version"
    return 0
  else
    echo "❌ $tool: Not installed"
    return 1
  fi
}

# Usage
check_tool "Git" "git"
check_tool "Node.js" "node"
check_tool "Azure CLI" "az"
```

### Install Tool with Confirmation

```bash
install_tool() {
  local tool=$1
  local install_cmd=$2

  read -p "Install $tool? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing $tool..."
    eval $install_cmd
  else
    echo "Skipped $tool"
  fi
}

# Usage
install_tool "Azure CLI" "brew install azure-cli"
```

---

## Platform Detection Patterns

| Platform | Detection Pattern | File/Folder Indicators |
|----------|-------------------|------------------------|
| **Fabric** | `find . -name "*.Notebook" -type d` | `*.Notebook/`, `*.DataPipeline/`, `*.Warehouse/` |
| **Databricks** | `ls databricks.yml` | `databricks.yml`, `.databricks/` |
| **Snowflake** | `grep -r "snowflake" .` | `snowflake.yml`, SQL files with Snowflake syntax |
| **AWS** | `grep "aws" terraform/*.tf` | `provider "aws"` in Terraform |
| **GCP** | `grep "google" terraform/*.tf` | `provider "google"` in Terraform |
| **dbt** | `ls dbt_project.yml` | `dbt_project.yml`, `models/`, `macros/` |
| **Terraform** | `ls terraform/*.tf` | `*.tf` files in terraform/ |

---

## References

- [Azure CLI Installation](https://learn.microsoft.com/cli/azure/install-azure-cli)
- [Terraform Installation](https://developer.hashicorp.com/terraform/install)
- [Databricks CLI](https://docs.databricks.com/dev-tools/cli/index.html)
- [Snowflake CLI](https://docs.snowflake.com/en/user-guide/snowsql)
- [AWS CLI Installation](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
- [Google Cloud SDK](https://cloud.google.com/sdk/docs/install)

---

*Last Updated: 2026-02-09*
