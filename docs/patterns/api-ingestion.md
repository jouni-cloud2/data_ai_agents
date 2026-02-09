# API Ingestion Pattern

Extract data from REST APIs into the data platform.

## Problem

External systems expose data via REST APIs that need to be:
- Extracted on a schedule
- Handled reliably with retries
- Stored with proper metadata
- Protected with secure credential handling

## Solution

```
┌─────────────────────────────────────────────────────────────────┐
│                    API INGESTION FLOW                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐  │
│  │ Schedule │───►│  Fetch   │───►│ Enrich   │───►│  Store   │  │
│  │ Trigger  │    │ API Data │    │ Metadata │    │  Bronze  │  │
│  └──────────┘    └──────────┘    └──────────┘    └──────────┘  │
│                       │                                         │
│                       ▼                                         │
│                 ┌──────────┐                                    │
│                 │  Secret  │                                    │
│                 │  Store   │                                    │
│                 └──────────┘                                    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Implementation

### Core Extraction Logic

```python
import requests
from typing import Iterator, Dict, Any
from datetime import datetime
import time

class APIExtractor:
    """Generic REST API extractor with pagination and retry."""

    def __init__(
        self,
        base_url: str,
        auth_header: Dict[str, str],
        rate_limit_per_second: float = 10
    ):
        self.base_url = base_url
        self.auth_header = auth_header
        self.rate_limit_delay = 1.0 / rate_limit_per_second
        self.session = requests.Session()
        self.session.headers.update(auth_header)

    def fetch_with_retry(
        self,
        endpoint: str,
        params: Dict = None,
        max_retries: int = 3
    ) -> Dict:
        """Fetch endpoint with exponential backoff retry."""
        url = f"{self.base_url}{endpoint}"

        for attempt in range(max_retries):
            try:
                time.sleep(self.rate_limit_delay)
                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                wait_time = 2 ** attempt
                print(f"Retry {attempt + 1}/{max_retries} after {wait_time}s: {e}")
                time.sleep(wait_time)

    def fetch_paginated(
        self,
        endpoint: str,
        page_size: int = 100
    ) -> Iterator[Dict]:
        """Fetch all pages from paginated endpoint."""
        params = {"limit": page_size}

        while True:
            response = self.fetch_with_retry(endpoint, params)

            # Yield records from this page
            records = response.get("results", response.get("data", []))
            for record in records:
                yield record

            # Check for next page (adapt to API's pagination style)
            paging = response.get("paging", {})
            next_cursor = paging.get("next", {}).get("after")

            if not next_cursor:
                break

            params["after"] = next_cursor
```

### Metadata Enrichment

```python
from pyspark.sql.functions import current_timestamp, lit, input_file_name

def enrich_with_metadata(df, source_name: str, environment: str):
    """Add ingestion metadata columns to DataFrame."""
    return (
        df
        .withColumn("_ingested_at", current_timestamp())
        .withColumn("_source_system", lit(source_name))
        .withColumn("_environment", lit(environment))
        .withColumn("_batch_id", lit(datetime.now().strftime("%Y%m%d%H%M%S")))
    )
```

### Complete Ingestion Pipeline

```python
def ingest_api_to_bronze(
    api_endpoint: str,
    source_name: str,
    entity_name: str,
    auth_secret_name: str,
    target_table: str,
    environment: str = "dev"
):
    """Full API to Bronze ingestion pipeline."""

    # 1. Get credentials from secret store
    api_key = get_secret(auth_secret_name)

    # 2. Initialize extractor
    extractor = APIExtractor(
        base_url="https://api.example.com",
        auth_header={"Authorization": f"Bearer {api_key}"}
    )

    # 3. Fetch all records
    records = list(extractor.fetch_paginated(api_endpoint))

    if not records:
        print(f"No records returned from {api_endpoint}")
        return

    # 4. Convert to DataFrame
    df = spark.createDataFrame(records)

    # 5. Enrich with metadata
    df = enrich_with_metadata(df, source_name, environment)

    # 6. Write to Bronze (append mode for history)
    df.write.format("delta").mode("append").saveAsTable(target_table)

    print(f"Ingested {len(records)} records to {target_table}")
```

## Authentication Patterns

### Bearer Token

```python
def get_bearer_auth(secret_name: str) -> Dict[str, str]:
    """Get Bearer token authentication header."""
    token = get_secret(secret_name)
    return {"Authorization": f"Bearer {token}"}
```

### Basic Auth

```python
import base64

def get_basic_auth(user_secret: str, pass_secret: str) -> Dict[str, str]:
    """Get Basic authentication header."""
    username = get_secret(user_secret)
    password = get_secret(pass_secret)
    credentials = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {"Authorization": f"Basic {credentials}"}
```

### OAuth 2.0

```python
def get_oauth_token(
    token_url: str,
    client_id_secret: str,
    client_secret_secret: str
) -> str:
    """Get OAuth 2.0 access token using client credentials flow."""
    client_id = get_secret(client_id_secret)
    client_secret = get_secret(client_secret_secret)

    response = requests.post(
        token_url,
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret
        }
    )
    response.raise_for_status()
    return response.json()["access_token"]
```

## Pagination Patterns

### Cursor-Based

```python
# Common in modern APIs (HubSpot, Shopify)
params = {"limit": 100}
while True:
    response = fetch(endpoint, params)
    yield from response["results"]

    next_cursor = response.get("paging", {}).get("next", {}).get("after")
    if not next_cursor:
        break
    params["after"] = next_cursor
```

### Offset-Based

```python
# Common in legacy APIs
offset = 0
limit = 100
while True:
    response = fetch(endpoint, {"offset": offset, "limit": limit})
    results = response["results"]

    if not results:
        break

    yield from results
    offset += limit
```

### Link Header

```python
# REST standard (GitHub API)
url = endpoint
while url:
    response = session.get(url)
    yield from response.json()

    # Parse Link header for next page
    links = response.headers.get("Link", "")
    next_link = parse_link_header(links).get("next")
    url = next_link
```

## Platform Variations

### Microsoft Fabric

```python
# Fabric notebook with Key Vault
from notebookutils import mssparkutils

def get_secret(secret_name: str) -> str:
    return mssparkutils.credentials.getSecret("keyvault-name", secret_name)

# Write to Lakehouse
df.write.format("delta").mode("append").saveAsTable("lakehouse.bronze_api_data")
```

### Databricks

```python
# Databricks with secret scopes
def get_secret(secret_name: str) -> str:
    return dbutils.secrets.get(scope="my-scope", key=secret_name)

# Write to Unity Catalog
df.write.format("delta").mode("append").saveAsTable("catalog.schema.bronze_api_data")
```

### Azure Functions + Fabric

```python
# Serverless ingestion writing to OneLake
from azure.storage.filedatalake import DataLakeServiceClient

def write_to_onelake(data: list, path: str):
    """Write JSON to OneLake Files folder."""
    service_client = DataLakeServiceClient(
        account_url="https://onelake.dfs.fabric.microsoft.com",
        credential=DefaultAzureCredential()
    )
    file_system = service_client.get_file_system_client(workspace_id)
    file_client = file_system.get_file_client(f"{lakehouse_id}/Files/{path}")
    file_client.upload_data(json.dumps(data), overwrite=True)
```

## Anti-Patterns

| Anti-Pattern | Problem | Solution |
|--------------|---------|----------|
| **Secrets in code** | Security risk | Use Key Vault / Secrets Manager |
| **No retry logic** | Transient failures cause data loss | Exponential backoff retry |
| **Ignoring rate limits** | API blocks requests | Implement rate limiting |
| **No pagination** | Miss records beyond first page | Always paginate |
| **Overwriting history** | Lose audit trail | Append mode in Bronze |

## Monitoring

### Key Metrics

| Metric | Description | Alert Threshold |
|--------|-------------|-----------------|
| Records ingested | Count per run | <50% of expected |
| Ingestion duration | Time to complete | >2x average |
| API errors | Failed requests | >5% error rate |
| Missing runs | Scheduled runs not executed | Any missed |

### Logging

```python
import logging

logging.info(f"Starting ingestion: {source_name}/{entity_name}")
logging.info(f"Fetched {len(records)} records")
logging.info(f"Written to {target_table}")
logging.error(f"Ingestion failed: {error}", exc_info=True)
```

## References

- [REST API Design Best Practices](https://restfulapi.net/)
- [Azure Key Vault](https://learn.microsoft.com/azure/key-vault/)
- [Databricks Secrets](https://docs.databricks.com/en/security/secrets/index.html)

---

*Last Updated: 2026-02-09*
