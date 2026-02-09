# MCP Server Documentation

Model Context Protocol (MCP) servers extend Claude Code with external tools and knowledge.

## Configured MCP Servers

| MCP Server | Purpose | Platforms |
|------------|---------|-----------|
| **microsoft-docs** | Official Microsoft/Azure documentation | Azure, Fabric, .NET |
| **context7** | Library and SDK documentation | All platforms |

## microsoft-docs

Access official Microsoft Learn documentation.

### Available Tools

| Tool | Description |
|------|-------------|
| `microsoft_docs_search` | Search docs, returns content chunks |
| `microsoft_code_sample_search` | Find code examples |
| `microsoft_docs_fetch` | Get full page content |

### Usage Examples

**Search for concept:**
```
Use microsoft_docs_search to find information about Fabric lakehouse architecture
```

**Find code samples:**
```
Use microsoft_code_sample_search to find Python examples for Azure Key Vault
```

**Get full page:**
```
Use microsoft_docs_fetch to read https://learn.microsoft.com/fabric/...
```

### Best Practices

1. **Search first** - Use `microsoft_docs_search` to find relevant pages
2. **Fetch for depth** - Use `microsoft_docs_fetch` when you need complete content
3. **Code samples** - Use `microsoft_code_sample_search` for implementation examples

## context7

Access up-to-date library and SDK documentation.

### Usage

```
Use context7 to look up the latest pandas DataFrame API
```

### Supported Libraries

- Python packages (pandas, pyspark, etc.)
- JavaScript/TypeScript libraries
- Popular SDKs and frameworks

## Adding New MCP Servers

### Configuration

MCP servers are configured in Claude Code settings:

```json
{
  "mcpServers": {
    "microsoft-docs": {
      "command": "...",
      "args": ["..."]
    },
    "context7": {
      "command": "...",
      "args": ["..."]
    }
  }
}
```

### Recommended MCPs by Platform

| Platform | Recommended MCPs |
|----------|------------------|
| **Fabric** | microsoft-docs |
| **Databricks** | context7 (for Spark) |
| **Snowflake** | context7 (for Snowpark) |
| **AWS** | aws-docs (if available), context7 |
| **GCP** | gcp-docs (if available), context7 |

## MCP Best Practices

1. **Use MCPs for official docs** - More reliable than web search
2. **Verify critical information** - Double-check important API details
3. **Combine with code search** - MCPs complement codebase search
4. **Prefer specific queries** - Narrow queries get better results

## References

- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Claude Code MCP Configuration](https://docs.anthropic.com/claude-code/mcp)

---

*Last Updated: 2026-02-09*
