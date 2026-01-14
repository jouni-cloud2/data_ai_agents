#!/bin/bash
set -e

# ============================================
# Data AI Agents - Installation Script (No NPX)
# ============================================
# Installs the AI-powered data platform development system
# into your current project directory.
#
# This version doesn't require Node.js - uses curl/tar only.
#
# Usage:
#   curl -fsSL https://raw.githubusercontent.com/OWNER/REPO/main/install-no-npx.sh | bash
# ============================================

REPO_OWNER="jouni-cloud2"
REPO_NAME="data_ai_agents"
BRANCH="main"

REPO_URL="https://github.com/$REPO_OWNER/$REPO_NAME/archive/$BRANCH.tar.gz"
TEMP_DIR=$(mktemp -d)

echo "🚀 Installing Data AI Agents..."
echo ""

# Check if already installed
if [ -d ".claude" ]; then
    echo "⚠️  .claude directory already exists."
    read -p "   Overwrite? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        rm -rf "$TEMP_DIR"
        exit 0
    fi
    rm -rf .claude
fi

# Download and extract
echo "📥 Downloading from GitHub..."
curl -sL "$REPO_URL" | tar xz -C "$TEMP_DIR"

# Backup existing CLAUDE.md
if [ -f "CLAUDE.md" ]; then
    echo "📦 Backing up existing CLAUDE.md to CLAUDE.md.backup"
    mv CLAUDE.md CLAUDE.md.backup
fi

# Copy files
echo "📁 Copying .claude directory..."
cp -r "$TEMP_DIR/$REPO_NAME-$BRANCH/.claude" .

echo "📄 Copying CLAUDE.md..."
cp "$TEMP_DIR/$REPO_NAME-$BRANCH/CLAUDE.md" .

# Create project directories if they don't exist
echo "📂 Creating project directories..."
mkdir -p pipelines notebooks sql tests docs config

# Cleanup
rm -rf "$TEMP_DIR"

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
echo "📖 For more info, see: https://github.com/$REPO_OWNER/$REPO_NAME"
echo ""
