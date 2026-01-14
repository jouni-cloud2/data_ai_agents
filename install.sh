#!/bin/bash
set -e

# ============================================
# Data AI Agents - Installation Script
# ============================================
# Installs the AI-powered data platform development system
# into your current project directory.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/OWNER/REPO/main/install.sh | bash
#
# Requirements: Node.js (for npx)
# ============================================

REPO="jouni-cloud2/data_ai_agents"

echo "🚀 Installing Data AI Agents..."
echo ""

# Check for npx
if ! command -v npx &> /dev/null; then
    echo "❌ Error: npx not found. Please install Node.js first."
    echo "   Download from: https://nodejs.org/"
    echo ""
    echo "   Or use the no-npx version:"
    echo "   curl -fsSL https://raw.githubusercontent.com/$REPO/main/install-no-npx.sh | bash"
    exit 1
fi

# Check if already installed
if [ -d ".claude" ]; then
    echo "⚠️  .claude directory already exists."
    read -p "   Overwrite? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        exit 0
    fi
    rm -rf .claude
fi

# Backup existing CLAUDE.md
if [ -f "CLAUDE.md" ]; then
    echo "📦 Backing up existing CLAUDE.md to CLAUDE.md.backup"
    mv CLAUDE.md CLAUDE.md.backup
fi

# Copy .claude directory using degit
echo "📁 Copying .claude directory..."
npx -y degit "$REPO/.claude" .claude --force

# Copy CLAUDE.md
echo "📄 Copying CLAUDE.md..."
curl -fsSL "https://raw.githubusercontent.com/$REPO/main/CLAUDE.md" -o CLAUDE.md

# Create project directories if they don't exist
echo "📂 Creating project directories..."
mkdir -p pipelines notebooks sql tests docs config

echo ""
echo "✅ Installation complete!"
echo ""
echo "📋 What was installed:"
echo "   • .claude/agents/     - 8 specialized AI agents"
echo "   • .claude/skills/     - 20 reusable skills (Fabric + Databricks)"
echo "   • .claude/commands/   - Workflow commands"
echo "   • CLAUDE.md           - Project knowledge base"
echo ""
echo "🚀 Quick start:"
echo "   /develop-story \"Add Salesforce as a data source\""
echo ""
echo "📖 For more info, see: https://github.com/$REPO"
echo ""
