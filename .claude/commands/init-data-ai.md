---
name: init-data-ai
description: First-time setup of the Data AI Agents team - install tools, configure MCP servers, validate environment.
---

# Init Data AI Command

Initializes this AI team environment with required tools, MCP servers, and configurations. Run once after cloning this repository.

**Behavior:** Automatic installation and configuration. Only prompts for authentication (az login) when needed.

## Usage

```bash
/init-data-ai                        # Full automatic setup
/init-data-ai check                  # Verify setup without installing
/init-data-ai tools                  # Install/update tools only
/init-data-ai mcp                    # Configure MCP servers only
```

---

## Phase 1: Environment Detection

Detect and display the environment without user interaction.

### 1.1 Detect Operating System & Package Manager

```bash
# Detect OS
uname -s  # Darwin (macOS), Linux, or Windows (via WSL)

# Detect package manager
if [[ "$OSTYPE" == "darwin"* ]]; then
  which brew && brew --version  # macOS with Homebrew
elif command -v apt &> /dev/null; then
  apt --version  # Debian/Ubuntu
elif command -v yum &> /dev/null; then
  yum --version  # RHEL/CentOS
elif command -v dnf &> /dev/null; then
  dnf --version  # Fedora
fi

# Detect shell
echo $SHELL
```

### 1.2 Display Environment

Present environment details in a table:

```markdown
## Environment Detection

| Check | Status | Details |
|-------|--------|---------|
| OS | [macOS/Linux/Windows] | [version] |
| Package Manager | [brew/apt/yum/dnf] | [version] |
| Shell | [zsh/bash] | [path] |

Starting automatic installation...
```

---

## Phase 2: Automatic Tool Installation

**IMPORTANT:** Install tools automatically without prompting. Only report progress and failures.

### 2.1 Check Current Tool Status

Check all tools silently:

```bash
# Core tools (Critical)
git --version 2>/dev/null
node --version 2>/dev/null
npm --version 2>/dev/null
jq --version 2>/dev/null

# Generic platform tools (Recommended)
python3 --version 2>/dev/null
az --version 2>/dev/null | head -1
terraform --version 2>/dev/null | head -1
docker --version 2>/dev/null
yq --version 2>/dev/null
```

### 2.2 Install Missing Tools Automatically

**macOS with Homebrew:**

```bash
# Track what needs installing
MISSING_TOOLS=()

# Check and queue missing tools
command -v git &> /dev/null || MISSING_TOOLS+=("git")
command -v node &> /dev/null || MISSING_TOOLS+=("node")
command -v jq &> /dev/null || MISSING_TOOLS+=("jq")
command -v python3 &> /dev/null || MISSING_TOOLS+=("python3")
command -v az &> /dev/null || MISSING_TOOLS+=("azure-cli")
command -v terraform &> /dev/null || MISSING_TOOLS+=("terraform")
command -v docker &> /dev/null || MISSING_TOOLS+=("docker")
command -v yq &> /dev/null || MISSING_TOOLS+=("yq")

# Install all missing tools in one command
if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
  echo "Installing: ${MISSING_TOOLS[*]}"

  # Add terraform tap if needed
  if [[ " ${MISSING_TOOLS[*]} " =~ " terraform " ]]; then
    brew tap hashicorp/tap 2>/dev/null
    brew install hashicorp/tap/terraform
    # Remove terraform from array
    MISSING_TOOLS=("${MISSING_TOOLS[@]/terraform/}")
  fi

  # Install remaining tools
  if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
    brew install "${MISSING_TOOLS[@]}"
  fi
fi
```

**Linux with apt:**

```bash
# Track what needs installing
MISSING_TOOLS=()

# Check and queue missing tools
command -v git &> /dev/null || MISSING_TOOLS+=("git")
command -v node &> /dev/null || MISSING_TOOLS+=("nodejs")
command -v npm &> /dev/null || MISSING_TOOLS+=("npm")
command -v jq &> /dev/null || MISSING_TOOLS+=("jq")
command -v python3 &> /dev/null || MISSING_TOOLS+=("python3" "python3-pip")
command -v docker &> /dev/null || MISSING_TOOLS+=("docker.io")
command -v yq &> /dev/null || MISSING_TOOLS+=("yq")

# Update apt cache once
if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
  sudo apt update
fi

# Install standard tools
if [ ${#MISSING_TOOLS[@]} -gt 0 ]; then
  echo "Installing: ${MISSING_TOOLS[*]}"
  sudo apt install -y "${MISSING_TOOLS[@]}"
fi

# Install Azure CLI if missing
if ! command -v az &> /dev/null; then
  echo "Installing Azure CLI..."
  curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
fi

# Install Terraform if missing
if ! command -v terraform &> /dev/null; then
  echo "Installing Terraform..."
  wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
  echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
  sudo apt update && sudo apt install -y terraform
fi
```

### 2.3 Display Installation Results

Show a concise table of installed tools:

```markdown
## Tool Installation Complete

| Tool | Status | Version |
|------|--------|---------|
| git | ✅ Installed | [version] |
| node | ✅ Installed | [version] |
| npm | ✅ Installed | [version] |
| jq | ✅ Installed | [version] |
| python3 | ✅ Installed | [version] |
| az | ✅ Installed | [version] |
| terraform | ✅ Installed | [version] |
| docker | ✅ Installed | [version] |
| yq | ✅ Installed | [version] |

Proceeding to MCP configuration...
```

If any critical tools failed:

```markdown
## Installation Issues

| Tool | Status | Action |
|------|--------|--------|
| node | ❌ Failed | [error message] |

**Critical tools failed to install. Please install manually:**
```bash
[manual installation command]
```

Stopping setup. Run `/init-data-ai` again after fixing.
```

**Note:** Platform-specific tools (databricks, snowsql, aws, gcloud) are installed by `/init-project` based on platform detection.

---

## Phase 3: Automatic MCP Configuration

**IMPORTANT:** Configure MCP servers automatically without prompting.

### 3.1 Install Azure MCP Server

```bash
# Install Azure MCP globally
echo "Installing Azure MCP Server..."
npm install -g @azure/mcp@latest

# Verify installation
azmcp --version
```

### 3.2 Enable Microsoft Docs Plugin

```bash
# Check if settings file exists
if [ ! -f ".claude/settings.json" ]; then
  echo '{"enabledPlugins": {}}' > .claude/settings.json
fi

# Update settings to enable microsoft-docs plugin
# Use jq to merge the plugin configuration
jq '.enabledPlugins["microsoft-docs@microsoft-docs-marketplace"] = true' .claude/settings.json > .claude/settings.json.tmp
mv .claude/settings.json.tmp .claude/settings.json
```

### 3.3 Configure MCP Settings File

```bash
# Create or update ~/.claude/mcp_settings.json
cat > ~/.claude/mcp_settings.json <<'EOF'
{
  "mcpServers": {
    "azure": {
      "command": "azmcp",
      "args": ["server", "start"]
    }
  }
}
EOF

echo "MCP configuration written to ~/.claude/mcp_settings.json"
```

### 3.4 Verify MCP Configuration

```bash
# Verify MCP settings file is valid JSON
jq empty ~/.claude/mcp_settings.json 2>&1

# Verify Azure MCP binary exists
which azmcp

# Verify project settings file is valid JSON
jq empty .claude/settings.json 2>&1
```

### 3.5 Display MCP Status

```markdown
## MCP Configuration Complete

| Component | Status | Details |
|-----------|--------|---------|
| Azure MCP | ✅ Installed | v[version] at [path] |
| Microsoft Docs Plugin | ✅ Enabled | In .claude/settings.json |
| MCP Settings File | ✅ Configured | ~/.claude/mcp_settings.json |

**Installed MCP Servers:**

1. **Azure MCP Server** (`@azure/mcp`)
   - 47+ Azure service integrations
   - Azure CLI command execution
   - Resource management

2. **Microsoft Docs Plugin** (`microsoft-docs@microsoft-docs-marketplace`)
   - Official Azure/Fabric documentation search
   - Code sample search
   - Full documentation fetch

**To activate:** Restart Claude Code (reload VS Code window)
```

If verification fails:

```markdown
## MCP Configuration Issues

| Check | Status | Issue |
|-------|--------|-------|
| MCP Settings | ❌ | [error message] |

**Fix:** [suggested resolution]
```

---

## Phase 4: Azure Authentication (Interactive)

**IMPORTANT:** This is the ONLY interactive step - prompt for Azure login if needed.

### 4.1 Check Azure Login Status

```bash
az account show 2>/dev/null
```

### 4.2 Prompt for Login (If Needed)

**If not logged in:**

```markdown
## Azure Authentication Required

Azure CLI is installed but you're not logged in.

**Please run the following command to authenticate:**

```bash
az login
```

This will open a browser for authentication. After login, select your subscription if needed:

```bash
# List subscriptions
az account list --output table

# Set default subscription (if needed)
az account set --subscription "<subscription-name-or-id>"
```

**Waiting for you to complete Azure login...**

Press Enter when done to continue setup.
```

Wait for user to press Enter, then verify:

```bash
# Verify login succeeded
if az account show &> /dev/null; then
  echo "✅ Azure login successful"
  az account show --output table
else
  echo "❌ Azure login failed or not completed"
  echo "Run 'az login' manually, then run /init-data-ai again"
  exit 1
fi
```

**If already logged in:**

```markdown
## Azure Authentication

✅ Already logged in to Azure

| Property | Value |
|----------|-------|
| Subscription | [name] |
| Tenant | [tenant name] |
| User | [email] |
```

---

## Phase 5: Environment File Setup

### 5.1 Check for .env File

```bash
# Check if .env exists
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
  # Copy template
  cp .env.example .env
  echo "✅ Created .env from .env.example"
elif [ ! -f ".env" ]; then
  echo "⚠️  No .env.example found, skipping .env creation"
else
  echo "✅ .env file already exists"
fi
```

### 5.2 Display .env Guidance (If Created)

**If .env was just created:**

```markdown
## Environment Configuration

Created `.env` file from template.

**Action Required:** Edit `.env` with your configuration:

```bash
# Required values
AZURE_SUBSCRIPTION_ID=<from-az-account-show>
AZURE_TENANT_ID=<from-az-account-show>

# Optional (for Fabric)
FABRIC_WORKSPACE_ID=<your-workspace-id>

# Optional (for Terraform)
TF_VAR_environment=dev
```

**Quick setup:** Some values can be auto-populated from Azure CLI:

```bash
# Get subscription and tenant IDs
az account show --query '{subscription:id, tenant:tenantId}' -o json
```

Edit [`.env`](.env) file now if needed.
```

---

## Phase 6: Setup Summary

Display comprehensive summary without prompting:

```markdown
## 🎉 Data AI Agents Setup Complete

### ✅ Installed Tools

| Tool | Version | Status |
|------|---------|--------|
| git | [version] | ✅ |
| node | [version] | ✅ |
| npm | [version] | ✅ |
| jq | [version] | ✅ |
| python3 | [version] | ✅ |
| az | [version] | ✅ |
| terraform | [version] | ✅ |
| docker | [version] | ✅ |
| yq | [version] | ✅ |

### ✅ Configured MCP Servers

| Server | Status | Configuration |
|--------|--------|---------------|
| Azure MCP | ✅ Ready | ~/.claude/mcp_settings.json |
| Microsoft Docs | ✅ Ready | .claude/settings.json |

### ✅ Azure Connection

| Property | Value |
|----------|-------|
| Status | ✅ Logged in |
| Subscription | [name] |
| Tenant | [tenant] |

### ⚠️ Next Steps

1. **Activate MCP servers:**
   - Restart Claude Code (Cmd+Shift+P → "Developer: Reload Window")
   - MCP servers will start automatically

2. **Set up a project:**
   ```bash
   /init-project <your-project-git-url>
   ```

3. **Verify MCP servers** (after restart):
   - Ask me to search Microsoft docs
   - Request Azure resource information

4. **Start development:**
   ```bash
   cd projects/<project>
   /architect          # Plan architecture
   /sdd "feature"      # Implement with SDD
   ```

---

**Environment ready for data platform development!**
```

---

## Check Mode (`/init-data-ai check`)

Only validate, don't install or configure:

```markdown
## Environment Check (Validation Only)

### Core Tools (Critical)

| Tool | Required | Installed | Version |
|------|----------|-----------|---------|
| git | ✅ | [✅/❌] | [version or -] |
| node | ✅ | [✅/❌] | [version or -] |
| npm | ✅ | [✅/❌] | [version or -] |
| jq | ✅ | [✅/❌] | [version or -] |

### Platform Tools (Recommended)

| Tool | Purpose | Installed | Version |
|------|---------|-----------|---------|
| python3 | Python runtime | [✅/❌] | [version or -] |
| az | Azure CLI | [✅/❌] | [version or -] |
| terraform | IaC | [✅/❌] | [version or -] |
| docker | Containers | [✅/❌] | [version or -] |
| yq | YAML processing | [✅/❌] | [version or -] |

### MCP Servers

| Server | Status | Location |
|--------|--------|----------|
| Azure MCP | [✅/❌] | [path or Not installed] |
| Microsoft Docs | [✅/❌] | [Enabled or Not configured] |

### Azure Authentication

| Check | Status |
|-------|--------|
| CLI installed | [✅/❌] |
| Logged in | [✅/❌] |
| Subscription set | [✅/❌] |

---

### Summary

**Missing Critical Tools:** [count]
**Missing Recommended Tools:** [count]
**MCP Configuration:** [OK/Needs setup]
**Azure Login:** [OK/Required]

**To install missing components:**
```bash
/init-data-ai
```
```

---

## Tools Mode (`/init-data-ai tools`)

Install only tools (skip MCP and auth):

1. Run Phase 1 (Environment Detection)
2. Run Phase 2 (Automatic Tool Installation)
3. Skip Phases 3-6
4. Display tool installation summary only

---

## MCP Mode (`/init-data-ai mcp`)

Configure only MCP servers (skip tools and auth):

1. Verify node/npm are installed (required for MCP)
2. Run Phase 3 (Automatic MCP Configuration)
3. Skip other phases
4. Display MCP configuration summary only

---

## Quick Reference

| Command | Behavior |
|---------|----------|
| `/init-data-ai` | Full automatic setup (only prompts for az login) |
| `/init-data-ai check` | Validation only, no changes |
| `/init-data-ai tools` | Install tools only |
| `/init-data-ai mcp` | Configure MCP servers only |

## Error Handling

### Critical Tool Installation Fails

Stop and report:
```markdown
❌ Critical tool installation failed: [tool]

Error: [error message]

**Manual installation required:**
```bash
[installation command]
```

Run `/init-data-ai` again after fixing.
```

### Azure MCP Installation Fails

Continue but warn:
```markdown
⚠️  Azure MCP installation failed

Error: [error message]

**Workaround:** Azure MCP can also run via npx:
- Configure `~/.claude/mcp_settings.json` to use npx instead
- Add: `"command": "npx", "args": ["-y", "@azure/mcp@latest", "server", "start"]`
```

### MCP Verification Fails

Continue but warn:
```markdown
⚠️  MCP configuration may have issues

Issue: [error message]

**Check:**
- Is `~/.claude/mcp_settings.json` valid JSON?
- Is `azmcp` in your PATH?
- Try running: `azmcp --version`

Setup will continue, but MCP servers may not work until fixed.
```
