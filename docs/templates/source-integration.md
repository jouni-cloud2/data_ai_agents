# {Source Name}

## Overview

| Field | Value |
|-------|-------|
| **System** | {Full system name} |
| **Vendor** | {Company name} |
| **Domain(s)** | {Which domains consume this source} |
| **Authentication** | {Bearer token / OAuth2 / API key / Basic Auth} |
| **Base URL** | `{API base URL}` |
| **Rate Limits** | {Requests per time period} |

## Entities

| Entity | API Endpoint | Bronze Table | Silver Table | Frequency |
|--------|--------------|--------------|--------------|-----------|
| {Entity} | `{endpoint}` | `bronze_{source}_{entity}` | `silver_{entity}` | {Daily/Hourly} |

## Authentication Setup

### Method: {Authentication Method}

{Description of how authentication works}

### Setup Steps

1. {Step 1}
2. {Step 2}
3. {Step 3}

### Secret Storage

| Secret Name | Description | Location |
|-------------|-------------|----------|
| `{source}-api-key` | {What it is} | Key Vault |

### Accessing Secrets

```python
# Example code for accessing secrets
api_key = mssparkutils.credentials.getSecret("keyvault-name", "{source}-api-key")
```

## API Details

### {Entity 1}

**Endpoint:** `GET /api/v1/{entity}`

**Key Fields:**

| Field | Type | Description | PII |
|-------|------|-------------|-----|
| `{field}` | {type} | {description} | {Yes/No} |

**Pagination:** {Cursor / Offset / Link header / None}

**Example Request:**
```bash
curl -X GET "{base_url}/{endpoint}" \
  -H "Authorization: Bearer {token}"
```

**Example Response:**
```json
{
  "results": [
    {
      "id": "123",
      "name": "Example"
    }
  ],
  "paging": {
    "next": {"after": "cursor123"}
  }
}
```

## Known Issues & Quirks

- {Issue 1: Description and workaround}
- {Issue 2: Description and workaround}

## Related Documentation

- [Vendor API Docs]({link})
- [{Domain} Runbook]({link})
- [Bronze Table Catalog Entry]({link})

---

*Last Updated: {YYYY-MM-DD}*
